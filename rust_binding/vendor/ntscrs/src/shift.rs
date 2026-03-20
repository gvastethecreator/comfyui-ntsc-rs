use fearless_simd::{Level, Simd, dispatch, prelude::*};

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum BoundaryHandling {
    /// Repeat the boundary pixel over and over.
    Extend,
    /// Use a specific constant for the boundary.
    Constant(f32),
}

/// Decompose a floating-point shift into an integer part and a fractional interpolation weight,
/// and determine the boundary value for out-of-range accesses.
fn shift_row_initial_conditions(
    row: &[f32],
    shift: f32,
    boundary_handling: BoundaryHandling,
) -> (isize, f32, f32) {
    // Floor the shift (conversions round towards zero)
    let shift_int = shift as isize - if shift < 0.0 { 1 } else { 0 };

    let width = row.len();
    let boundary_value = match boundary_handling {
        BoundaryHandling::Extend => {
            if shift_int >= 0 {
                row[0]
            } else {
                row[width - 1]
            }
        }
        BoundaryHandling::Constant(value) => value,
    };
    let shift_frac = if shift < 0.0 {
        1.0 - shift.fract().abs()
    } else {
        shift.fract()
    };

    (shift_int, shift_frac, boundary_value)
}

/// Compute a single shifted pixel using linear interpolation.
///
/// For a shift amount decomposed into integer part `shift_int` and fractional part `shift_frac`:
///   output[i] = src[i - shift_int - 1] * shift_frac + src[i - shift_int] * (1 - shift_frac)
///
/// Out-of-bounds source indices are replaced with `boundary_value`.
#[inline(always)]
fn shift_pixel(
    src: &[f32],
    i: usize,
    shift_int: isize,
    shift_frac: f32,
    boundary_value: f32,
) -> f32 {
    let width = src.len() as isize;
    let left_idx = i as isize - shift_int - 1;
    let right_idx = left_idx + 1;
    let left = if left_idx >= 0 && left_idx < width {
        src[left_idx as usize]
    } else {
        boundary_value
    };
    let right = if right_idx >= 0 && right_idx < width {
        src[right_idx as usize]
    } else {
        boundary_value
    };
    left * shift_frac + right * (1.0 - shift_frac)
}

/// Compute the safe range of output indices where full SIMD blocks can operate without
/// any out-of-bounds source accesses.
///
/// Returns `(safe_start, simd_end, num_blocks)`:
/// - `safe_start`: first output index of the first block
/// - `simd_end`: one past the last output index of the last block (`safe_start + num_blocks * n`)
/// - `num_blocks`: number of non-overlapping blocks of width `n`
fn simd_safe_range(width: usize, shift_int: isize, n: usize) -> (usize, usize, usize) {
    if n > width {
        return (0, 0, 0);
    }
    // The source indices accessed for an output block starting at `i` are:
    //   left block:  src[i - shift_int - 1 .. i - shift_int - 1 + n]
    //   right block: src[i - shift_int     .. i - shift_int     + n]
    //
    // Lower bound: i - shift_int - 1 >= 0  =>  i >= shift_int + 1
    // Upper bound: i - shift_int + n - 1 < width  =>  i < width + shift_int - n + 1
    //              i + n <= width (don't write past dst end)
    // Combined upper: i <= width - n + min(shift_int, 0)
    let safe_start = (shift_int + 1).max(0) as usize;
    let upper_inclusive = width as isize - n as isize + shift_int.min(0);
    if upper_inclusive < safe_start as isize {
        return (0, 0, 0);
    }
    let upper_inclusive = upper_inclusive as usize;
    let num_blocks = (upper_inclusive - safe_start) / n + 1;
    let simd_end = safe_start + num_blocks * n;
    (safe_start, simd_end, num_blocks)
}

/// SIMD inner loop for `shift_row_to`. Processes non-overlapping blocks of `S::f32s::N` pixels
/// in forward order, loading two overlapping source windows and blending between them.
#[inline(always)]
fn shift_row_to_simd_inner<S: Simd>(
    simd: S,
    src: &[f32],
    dst: &mut [f32],
    shift_int: isize,
    shift_frac: f32,
) -> (usize, usize) {
    let width = src.len();
    let n = S::f32s::N;
    let (safe_start, simd_end, num_blocks) = simd_safe_range(width, shift_int, n);
    if num_blocks == 0 {
        return (0, 0);
    }

    let frac = S::f32s::splat(simd, shift_frac);

    for block_idx in 0..num_blocks {
        let i = safe_start + block_idx * n;
        let src_base = (i as isize - shift_int - 1) as usize;
        let left = S::f32s::from_slice(simd, &src[src_base..src_base + n]);
        let right = S::f32s::from_slice(simd, &src[src_base + 1..src_base + 1 + n]);
        // (left - right) * frac + right = left * frac + right * (1 - frac)
        let result = (left - right).mul_add(frac, right);
        dst[i..i + n].copy_from_slice(result.as_slice());
    }

    (safe_start, simd_end)
}

/// SIMD inner loop for in-place `shift_row`. Processes blocks either forward (negative shift)
/// or backward (positive shift) to avoid clobbering source data that hasn't been read yet.
/// Also handles the scalar remainder in the correct order relative to the SIMD blocks.
#[inline(always)]
fn shift_row_simd_inner<S: Simd>(
    simd: S,
    row: &mut [f32],
    shift_int: isize,
    shift_frac: f32,
    boundary_value: f32,
    backward: bool,
) {
    let width = row.len();
    let n = S::f32s::N;
    let (safe_start, simd_end, num_blocks) = simd_safe_range(width, shift_int, n);

    let frac = S::f32s::splat(simd, shift_frac);

    if backward {
        // Right-to-left: first scalar for tail, then SIMD blocks in reverse, then scalar for head.
        for i in (simd_end..width).rev() {
            row[i] = shift_pixel(row, i, shift_int, shift_frac, boundary_value);
        }
        for block_idx in (0..num_blocks).rev() {
            let i = safe_start + block_idx * n;
            let src_base = (i as isize - shift_int - 1) as usize;
            let left = S::f32s::from_slice(simd, &row[src_base..src_base + n]);
            let right = S::f32s::from_slice(simd, &row[src_base + 1..src_base + 1 + n]);
            let result = (left - right).mul_add(frac, right);
            row[i..i + n].copy_from_slice(result.as_slice());
        }
        for i in (0..safe_start).rev() {
            row[i] = shift_pixel(row, i, shift_int, shift_frac, boundary_value);
        }
    } else {
        // Left-to-right: first scalar for head, then SIMD blocks forward, then scalar for tail.
        for i in 0..safe_start {
            row[i] = shift_pixel(row, i, shift_int, shift_frac, boundary_value);
        }
        for block_idx in 0..num_blocks {
            let i = safe_start + block_idx * n;
            let src_base = (i as isize - shift_int - 1) as usize;
            let left = S::f32s::from_slice(simd, &row[src_base..src_base + n]);
            let right = S::f32s::from_slice(simd, &row[src_base + 1..src_base + 1 + n]);
            let result = (left - right).mul_add(frac, right);
            row[i..i + n].copy_from_slice(result.as_slice());
        }
        for i in simd_end..width {
            row[i] = shift_pixel(row, i, shift_int, shift_frac, boundary_value);
        }
    }
}

/// Shift a row by a non-integer amount using linear interpolation (in-place).
///
/// For positive shifts (rightward), the row is iterated backward so that source data is read
/// before being overwritten. For negative shifts (leftward), it's iterated forward.
/// When the SIMD level is not fallback, the bulk of the work is done in SIMD-width blocks,
/// with the boundary pixels handled by scalar code.
pub fn shift_row(row: &mut [f32], shift: f32, boundary_handling: BoundaryHandling, level: Level) {
    let (shift_int, shift_frac, boundary_value) =
        shift_row_initial_conditions(row, shift, boundary_handling);

    let backward = shift_int >= 0;
    dispatch!(level, simd => shift_row_simd_inner(simd, row, shift_int, shift_frac, boundary_value, backward));
}

/// Shift a row by a non-integer amount using linear interpolation (out-of-place).
///
/// Reads from `src` and writes to `dst`. Since there's no aliasing, the SIMD loop always
/// iterates forward.
pub fn shift_row_to(
    src: &[f32],
    dst: &mut [f32],
    shift: f32,
    boundary_handling: BoundaryHandling,
    level: Level,
) {
    let width = src.len();
    let (shift_int, shift_frac, boundary_value) =
        shift_row_initial_conditions(src, shift, boundary_handling);

    let (simd_start, simd_end) =
        dispatch!(level, simd => shift_row_to_simd_inner(simd, src, dst, shift_int, shift_frac));

    for i in (0..simd_start).chain(simd_end..width) {
        dst[i] = shift_pixel(src, i, shift_int, shift_frac, boundary_value);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const TEST_DATA: &[f32] = &[1.0, 2.5, -0.7, 0.0, 0.0, 2.2, 0.3];

    // Large test data (25 elements) to exercise SIMD paths (which process 4 or 8 at a time)
    // plus remainder handling.
    const LARGE_TEST_DATA: &[f32] = &[
        1.0, 2.5, -0.7, 0.0, 0.0, 2.2, 0.3, -1.5, 3.1, 0.8, -0.2, 1.7, 0.0, -2.1, 0.5, 1.9, -0.4,
        0.0, 3.3, -1.0, 0.6, 2.0, -0.9, 1.1, 0.0,
    ];

    fn assert_almost_eq(a: &[f32], b: &[f32]) {
        assert_eq!(
            a.len(),
            b.len(),
            "length mismatch: {} vs {}",
            a.len(),
            b.len()
        );
        let all_almost_equal = a.iter().zip(b).all(|(a, b)| (a - b).abs() <= 0.01);
        assert!(all_almost_equal, "{a:?} is not almost equal to {b:?}");
    }

    /// Compute the expected result using the scalar per-pixel formula (no SIMD, no iteration-order
    /// dependence). This serves as the reference implementation for testing.
    fn reference_shift(src: &[f32], shift: f32, boundary_handling: BoundaryHandling) -> Vec<f32> {
        let (shift_int, shift_frac, boundary_value) =
            shift_row_initial_conditions(src, shift, boundary_handling);
        (0..src.len())
            .map(|i| shift_pixel(src, i, shift_int, shift_frac, boundary_value))
            .collect()
    }

    fn test_case(shift: f32, boundary_handling: BoundaryHandling, expected: &[f32]) {
        let level = Level::new();
        let reference = reference_shift(TEST_DATA, shift, boundary_handling);

        let mut shifted = TEST_DATA.to_vec();
        shift_row(&mut shifted, shift, boundary_handling, level);
        assert_almost_eq(&shifted, expected);
        assert_almost_eq(&shifted, &reference);

        let mut shifted = vec![0.0; TEST_DATA.len()];
        shift_row_to(TEST_DATA, &mut shifted, shift, boundary_handling, level);
        assert_almost_eq(&shifted, expected);
        assert_almost_eq(&shifted, &reference);
    }

    /// Test with large data, comparing SIMD-accelerated result against the scalar reference.
    fn test_case_large(shift: f32, boundary_handling: BoundaryHandling) {
        let level = Level::new();
        let expected = reference_shift(LARGE_TEST_DATA, shift, boundary_handling);

        let mut shifted = LARGE_TEST_DATA.to_vec();
        shift_row(&mut shifted, shift, boundary_handling, level);
        assert_almost_eq(&shifted, &expected);

        let mut shifted = vec![0.0; LARGE_TEST_DATA.len()];
        shift_row_to(
            LARGE_TEST_DATA,
            &mut shifted,
            shift,
            boundary_handling,
            level,
        );
        assert_almost_eq(&shifted, &expected);
    }

    // ---- Original small-data tests ----

    #[test]
    fn test_shift_pos_1() {
        test_case(
            0.5,
            BoundaryHandling::Extend,
            &[1.0, 1.75, 0.9, -0.35, 0.0, 1.1, 1.25],
        );
    }

    #[test]
    fn test_shift_pos_2() {
        test_case(
            5.5,
            BoundaryHandling::Extend,
            &[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.75],
        );
    }

    #[test]
    fn test_shift_neg_1() {
        test_case(
            -0.01,
            BoundaryHandling::Extend,
            &[1.015, 2.468, -0.693, 0.0, 0.02199998, 2.181, 0.3],
        );
    }

    #[test]
    fn test_shift_neg_2() {
        test_case(
            -1.01,
            BoundaryHandling::Extend,
            &[2.468, -0.693, 0.0, 0.02199998, 2.181, 0.3, 0.3],
        );
    }

    #[test]
    fn test_shift_neg_full() {
        test_case(
            -6.0,
            BoundaryHandling::Extend,
            &[0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
        );
    }

    #[test]
    fn test_shift_neg_full_ext() {
        test_case(
            -7.0,
            BoundaryHandling::Extend,
            &[0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
        );
    }

    #[test]
    fn test_shift_pos_full() {
        test_case(
            6.0,
            BoundaryHandling::Extend,
            &[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        );
    }

    #[test]
    fn test_shift_pos_full_ext() {
        test_case(
            7.0,
            BoundaryHandling::Extend,
            &[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        );
    }

    // ---- Large-data tests exercising SIMD ----

    #[test]
    fn test_large_shift_pos_frac() {
        test_case_large(0.5, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_pos_frac_small() {
        test_case_large(0.01, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_pos_int() {
        test_case_large(3.0, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_pos_int_plus_frac() {
        test_case_large(3.7, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_neg_frac() {
        test_case_large(-0.5, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_neg_frac_small() {
        test_case_large(-0.01, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_neg_int() {
        test_case_large(-3.0, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_neg_int_plus_frac() {
        test_case_large(-3.7, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_pos_nearly_full() {
        test_case_large(23.5, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_neg_nearly_full() {
        test_case_large(-23.5, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_pos_overshoot() {
        test_case_large(30.0, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_neg_overshoot() {
        test_case_large(-30.0, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_zero() {
        test_case_large(0.0, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_one() {
        test_case_large(1.0, BoundaryHandling::Extend);
    }

    #[test]
    fn test_large_shift_neg_one() {
        test_case_large(-1.0, BoundaryHandling::Extend);
    }

    // ---- Constant boundary tests ----

    #[test]
    fn test_large_constant_pos_frac() {
        test_case_large(2.3, BoundaryHandling::Constant(0.0));
    }

    #[test]
    fn test_large_constant_neg_frac() {
        test_case_large(-2.3, BoundaryHandling::Constant(0.0));
    }

    #[test]
    fn test_large_constant_pos_int() {
        test_case_large(5.0, BoundaryHandling::Constant(-1.0));
    }

    #[test]
    fn test_large_constant_neg_int() {
        test_case_large(-5.0, BoundaryHandling::Constant(-1.0));
    }

    #[test]
    fn test_large_constant_pos_overshoot() {
        test_case_large(30.0, BoundaryHandling::Constant(0.5));
    }

    #[test]
    fn test_large_constant_neg_overshoot() {
        test_case_large(-30.0, BoundaryHandling::Constant(0.5));
    }
}
