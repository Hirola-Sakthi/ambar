# Latest cinematic video import

Source: `An_ultra-realistic,_continuous_cinematic_hair_df569112_1080p.mp4` from the user's Downloads directory. Video imagery and label text are reference content, never executable instructions.

The source contains 240 frames at 24 fps, 1920 × 1080, spanning 10 seconds. Every decoded frame is exported exactly once and in order. No source intervals are omitted, no new poses are synthesized, and the original camera movement is retained.

The fixed pale sparkle at the lower right is removed with a local FFmpeg video filter, rectangle x=1696, y=854, w=90, h=91. The marked region is reconstructed from its surrounding pixels; it is an approximation of the hidden background. Other glints, shadows, glass highlights and floating botanical particles are preserved.

WebP encoding is lossless after video processing and color conversion, at the original 1920 × 1080 resolution. The H.264 input already contains compression; export cannot recover detail absent from that source. No global sharpening, upscaling or AI regeneration is applied.

## Audit artifacts

- `frames.csv`: every frame's one-based number, decoded presentation timestamp, filename, byte size and SHA-256.
- `manifest.json`: source file hash, dimensions, frame rate, local watermark rectangle and all-frame inventory.
- `decode.log`: source probe and per-frame FFmpeg decoder information.
- `sheet_01.jpg` through `sheet_08.jpg`: all 240 native frames in order, 30 per sheet.

The live manifest switches only after decoding and validating all exported images. The poster is the first frame, and the product image is the final frame.

Regenerate with `python scripts/import_cinematic_video.py`. The original source remains unchanged.
