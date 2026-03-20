use numpy::PyArray3;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use ntsc_rs::{
    settings::standard::{
        ChromaDemodulationFilter, ChromaLowpass, FbmNoiseSettings, FilterType,
        HeadSwitchingMidLineSettings, HeadSwitchingSettings, LumaLowpass, PhaseShift,
        RingingSettings, ScaleSettings, TrackingNoiseSettings, UseField, VHSEdgeWaveSettings,
        VHSSettings, VHSSharpenSettings, VHSTapeSpeed,
    },
    yiq_fielding::{pixel_bytes_for, BlitInfo, DeinterlaceMode, Rgb, YiqView},
    NtscEffect,
};

fn parse_use_field(s: &str) -> UseField {
    match s {
        "Alternating" => UseField::Alternating,
        "Upper" => UseField::Upper,
        "Lower" => UseField::Lower,
        "Both" => UseField::Both,
        "InterleavedUpper" => UseField::InterleavedUpper,
        "InterleavedLower" => UseField::InterleavedLower,
        _ => UseField::InterleavedUpper,
    }
}

fn parse_filter_type(s: &str) -> FilterType {
    match s {
        "ConstantK" => FilterType::ConstantK,
        "Butterworth" => FilterType::Butterworth,
        _ => FilterType::Butterworth,
    }
}

fn parse_luma_lowpass(s: &str) -> LumaLowpass {
    match s {
        "None" => LumaLowpass::None,
        "Box" => LumaLowpass::Box,
        "Notch" => LumaLowpass::Notch,
        _ => LumaLowpass::Notch,
    }
}

fn parse_chroma_lowpass(s: &str) -> ChromaLowpass {
    match s {
        "None" => ChromaLowpass::None,
        "Light" => ChromaLowpass::Light,
        "Full" => ChromaLowpass::Full,
        _ => ChromaLowpass::Full,
    }
}

fn parse_chroma_demodulation(s: &str) -> ChromaDemodulationFilter {
    match s {
        "Box" => ChromaDemodulationFilter::Box,
        "Notch" => ChromaDemodulationFilter::Notch,
        "OneLineComb" => ChromaDemodulationFilter::OneLineComb,
        "TwoLineComb" => ChromaDemodulationFilter::TwoLineComb,
        _ => ChromaDemodulationFilter::Notch,
    }
}

fn parse_phase_shift(s: &str) -> PhaseShift {
    match s {
        "Degrees0" => PhaseShift::Degrees0,
        "Degrees90" => PhaseShift::Degrees90,
        "Degrees180" => PhaseShift::Degrees180,
        "Degrees270" => PhaseShift::Degrees270,
        _ => PhaseShift::Degrees180,
    }
}

fn parse_tape_speed(s: &str) -> VHSTapeSpeed {
    match s {
        "NONE" => VHSTapeSpeed::NONE,
        "SP" => VHSTapeSpeed::SP,
        "LP" => VHSTapeSpeed::LP,
        "EP" => VHSTapeSpeed::EP,
        _ => VHSTapeSpeed::LP,
    }
}

fn get_i32(dict: &PyDict, key: &str, default: i32) -> i32 {
    match dict.get_item(key) {
        Ok(Some(v)) => v.extract::<i32>().ok().unwrap_or(default),
        _ => default,
    }
}

fn get_f32(dict: &PyDict, key: &str, default: f32) -> f32 {
    match dict.get_item(key) {
        Ok(Some(v)) => v.extract::<f32>().ok().unwrap_or(default),
        _ => default,
    }
}

fn get_bool(dict: &PyDict, key: &str, default: bool) -> bool {
    match dict.get_item(key) {
        Ok(Some(v)) => v.extract::<bool>().ok().unwrap_or(default),
        _ => default,
    }
}

fn get_str(dict: &PyDict, key: &str, default: &str) -> String {
    match dict.get_item(key) {
        Ok(Some(v)) => v
            .extract::<String>()
            .ok()
            .unwrap_or_else(|| default.to_string()),
        _ => default.to_string(),
    }
}

fn build_ntsc_effect(dict: &PyDict) -> NtscEffect {
    let mut effect = NtscEffect::default();

    effect.random_seed = get_i32(dict, "random_seed", 0);
    effect.use_field = parse_use_field(&get_str(dict, "use_field", "InterleavedUpper"));
    effect.filter_type = parse_filter_type(&get_str(dict, "filter_type", "Butterworth"));
    effect.input_luma_filter = parse_luma_lowpass(&get_str(dict, "input_luma_filter", "Notch"));
    effect.chroma_lowpass_in = parse_chroma_lowpass(&get_str(dict, "chroma_lowpass_in", "Full"));
    effect.chroma_demodulation =
        parse_chroma_demodulation(&get_str(dict, "chroma_demodulation", "Notch"));
    effect.luma_smear = get_f32(dict, "luma_smear", 0.5);
    effect.composite_sharpening = get_f32(dict, "composite_sharpening", 1.0);
    effect.video_scanline_phase_shift =
        parse_phase_shift(&get_str(dict, "video_scanline_phase_shift", "Degrees180"));
    effect.video_scanline_phase_shift_offset =
        get_i32(dict, "video_scanline_phase_shift_offset", 0);
    effect.chroma_vert_blend = get_bool(dict, "chroma_vert_blend", true);
    effect.chroma_lowpass_out = parse_chroma_lowpass(&get_str(dict, "chroma_lowpass_out", "Full"));
    effect.snow_intensity = get_f32(dict, "snow_intensity", 0.00025);
    effect.snow_anisotropy = get_f32(dict, "snow_anisotropy", 0.5);
    effect.chroma_phase_noise_intensity = get_f32(dict, "chroma_phase_noise_intensity", 0.001);
    effect.chroma_phase_error = get_f32(dict, "chroma_phase_error", 0.0);
    effect.chroma_delay_horizontal = get_f32(dict, "chroma_delay_horizontal", 0.0);
    effect.chroma_delay_vertical = get_i32(dict, "chroma_delay_vertical", 0);

    if get_bool(dict, "head_switching_enabled", true) {
        effect.head_switching = Some(HeadSwitchingSettings {
            height: get_i32(dict, "head_switching_height", 8),
            offset: get_i32(dict, "head_switching_offset", 3),
            horiz_shift: get_f32(dict, "head_switching_horizontal_shift", 72.0),
            mid_line: if get_bool(dict, "head_switching_mid_line_enabled", true) {
                Some(HeadSwitchingMidLineSettings {
                    position: get_f32(dict, "head_switching_mid_line_position", 0.95),
                    jitter: get_f32(dict, "head_switching_mid_line_jitter", 0.03),
                })
            } else {
                None
            },
        });
    } else {
        effect.head_switching = None;
    }

    if get_bool(dict, "tracking_noise_enabled", true) {
        effect.tracking_noise = Some(TrackingNoiseSettings {
            height: get_i32(dict, "tracking_noise_height", 12),
            wave_intensity: get_f32(dict, "tracking_noise_wave_intensity", 15.0),
            snow_intensity: get_f32(dict, "tracking_noise_snow_intensity", 0.025),
            snow_anisotropy: get_f32(dict, "tracking_noise_snow_anisotropy", 0.25),
            noise_intensity: get_f32(dict, "tracking_noise_noise_intensity", 0.25),
        });
    } else {
        effect.tracking_noise = None;
    }

    if get_bool(dict, "composite_noise_enabled", true) {
        effect.composite_noise = Some(FbmNoiseSettings {
            frequency: get_f32(dict, "composite_noise_frequency", 0.5),
            intensity: get_f32(dict, "composite_noise_intensity", 0.05),
            detail: get_i32(dict, "composite_noise_detail", 1),
        });
    } else {
        effect.composite_noise = None;
    }

    if get_bool(dict, "luma_noise_enabled", true) {
        effect.luma_noise = Some(FbmNoiseSettings {
            frequency: get_f32(dict, "luma_noise_frequency", 0.5),
            intensity: get_f32(dict, "luma_noise_intensity", 0.01),
            detail: get_i32(dict, "luma_noise_detail", 1),
        });
    } else {
        effect.luma_noise = None;
    }

    if get_bool(dict, "chroma_noise_enabled", true) {
        effect.chroma_noise = Some(FbmNoiseSettings {
            frequency: get_f32(dict, "chroma_noise_frequency", 0.05),
            intensity: get_f32(dict, "chroma_noise_intensity", 0.1),
            detail: get_i32(dict, "chroma_noise_detail", 2),
        });
    } else {
        effect.chroma_noise = None;
    }

    if get_bool(dict, "ringing_enabled", true) {
        effect.ringing = Some(RingingSettings {
            frequency: get_f32(dict, "ringing_frequency", 0.45),
            power: get_f32(dict, "ringing_power", 4.0),
            intensity: get_f32(dict, "ringing_intensity", 4.0),
        });
    } else {
        effect.ringing = None;
    }

    if get_bool(dict, "vhs_enabled", true) {
        let mut vhs = VHSSettings {
            tape_speed: parse_tape_speed(&get_str(dict, "vhs_tape_speed", "LP")),
            chroma_loss: get_f32(dict, "vhs_chroma_loss", 0.000025),
            sharpen: None,
            edge_wave: None,
        };

        if get_bool(dict, "vhs_sharpen_enabled", true) {
            vhs.sharpen = Some(VHSSharpenSettings {
                intensity: get_f32(dict, "vhs_sharpen_intensity", 0.25),
                frequency: get_f32(dict, "vhs_sharpen_frequency", 1.0),
            });
        }

        if get_bool(dict, "vhs_edge_wave_enabled", true) {
            vhs.edge_wave = Some(VHSEdgeWaveSettings {
                intensity: get_f32(dict, "vhs_edge_wave_intensity", 0.5),
                speed: get_f32(dict, "vhs_edge_wave_speed", 4.0),
                frequency: get_f32(dict, "vhs_edge_wave_frequency", 0.05),
                detail: get_i32(dict, "vhs_edge_wave_detail", 2),
            });
        }

        effect.vhs_settings = Some(vhs);
    } else {
        effect.vhs_settings = None;
    }

    if get_bool(dict, "scale_enabled", true) {
        effect.scale = Some(ScaleSettings {
            horizontal_scale: get_f32(dict, "horizontal_scale", 1.0),
            vertical_scale: get_f32(dict, "vertical_scale", 1.0),
            scale_with_video_size: get_bool(dict, "scale_with_video_size", false),
        });
    } else {
        effect.scale = None;
    }

    effect
}

#[pyfunction]
pub fn apply_ntsc_filter(py: Python, image: &PyArray3<u8>, params: &PyDict) -> PyResult<Py<PyAny>> {
    let image_array = unsafe { image.as_array() };
    let (height, width, channels) = (
        image_array.shape()[0],
        image_array.shape()[1],
        image_array.shape()[2],
    );

    let mut rgb_buffer = vec![0u8; width * height * 3];
    for y in 0..height {
        for x in 0..width {
            let src_idx = (y * width + x) * channels;
            let dst_idx = (y * width + x) * 3;
            rgb_buffer[dst_idx] = image_array[[y, x, 0]];
            rgb_buffer[dst_idx + 1] = image_array[[y, x, 1.min(channels - 1)]];
            rgb_buffer[dst_idx + 2] = image_array[[y, x, 2.min(channels - 1)]];
        }
    }

    let effect = build_ntsc_effect(params);
    let frame_num = get_i32(params, "frame_num", 0);

    let scratch_len = YiqView::buf_length_for((width, height), effect.use_field.to_yiq_field(0));
    let mut scratch = vec![0f32; scratch_len];
    let mut yiq = YiqView::from_parts(
        &mut scratch,
        (width, height),
        effect.use_field.to_yiq_field(0),
    );

    let row_bytes = width * pixel_bytes_for::<Rgb, u8>();
    let blit_info = BlitInfo::from_full_frame(width, height, row_bytes);

    yiq.set_from_strided_buffer::<Rgb, u8, _>(&rgb_buffer, blit_info, ());

    effect.apply_effect_to_yiq(&mut yiq, frame_num as usize, [1.0, 1.0]);

    let mut output_buffer = vec![0u8; width * height * 3];
    yiq.write_to_strided_buffer::<Rgb, u8, _>(
        &mut output_buffer,
        blit_info,
        DeinterlaceMode::Bob,
        (),
    );

    let array = unsafe { PyArray3::new(py, (height, width, 3), false) };
    let slice = unsafe { array.as_slice_mut()? };
    slice.copy_from_slice(&output_buffer);
    Ok(array.to_object(py))
}

#[pymodule]
fn comfyui_ntsc_rs(_: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply_ntsc_filter, m)?)?;
    Ok(())
}
