# Herbal oil advertisement frames

The active sequence uses `Herbal_oil_bottle_advertisement_3860f7b0_1080p_gwr_video_mvp.mp4`. Every native frame is in the new `public/scenes/herbal-oil-advertisement/` folder, at 1920 x 1080 and 24 fps, encoded as lossless WebP. No resizing, retouching, sharpening, watermark removal, interpolation or generated artwork is applied. Every exported image's decoded RGB hash is checked against an independent source decode before activation. The source video already contains the desired bottle and assembly animation.

The animation, poster and shop image follow `src/sequenceManifest.json`, including its source-hash cache revision. The poster copies the first frame and the shop image copies the final frame. The canvas supports up to 2x display density and high-quality smoothing. Previous frame folders and uploaded ZIPs remain intact.

Reproduce with `python -B scripts/import_herbal_video.py`; `--source <path>` changes the input and `--resume` reuses completed images while still auditing every frame. See [the current source review](analysis/herbal-oil-advertisement/README.md) for frame counts, native timestamps, hashes and all-frame contact sheets.

## Previous retained cinematic source

The historical notes below describe the previous video and its retained assets. The current sequence above supersedes those paths and processing steps.

## Assets and fidelity

- `public/scenes/cinematic-hair-oil/frame_0001.webp` through `frame_0240.webp`: all 240 native frames, retained in source order at 1920 × 1080.
- `poster.webp`: exact copy of the first exported frame, showing the empty white ceramic bowl.
- `product.webp`: exact copy of the last exported frame, showing the source bottle and label.
- `src/sequenceManifest.json`: native count, dimensions, source name and scene ranges.

The video runs 10 seconds at 24 fps. There is no frame-rate conversion, interpolation, synthesized artwork, global sharpening or resizing. Lossless WebP preserves the processed RGB image without another lossy encoding stage. Original H.264 compression and video-to-RGB color conversion still apply.

The fixed lower-right sparkle is removed with FFmpeg's local video filter at x=1696, y=854, w=90, h=91. Only that background region is reconstructed from neighboring pixels. Other source details, highlights and printed label text are preserved. Prior frame sets and artwork are removed from public assets.

## Playback

`src/ProductSequence.jsx` maps all 240 frames onto the long scroll section, including reverse scrolling. The original camera motion comes from the video. Centered cover framing fills desktop and mobile viewports; portrait screens crop landscape edges around the bowl and bottle. Text windows follow the source actions.

Nearby native-resolution images load on demand. The decoded cache holds at most 24 images on desktop and 16 on mobile; the prefetch window fits within that budget and settles when idle. Reduced motion displays the first frame without the extended scroll section.

## Reproduce and audit

```powershell
python scripts/import_cinematic_video.py
```

The import validates every decoded output before switching the live manifest. [The current review](analysis/cinematic-hair-oil/README.md) documents processing and all-frame coverage. Its `frames.csv`, source hash, decoded timestamps and eight numbered contact sheets provide an audit trail.

If Vite was running while new public files were created, restart it after import so its public-file index includes the entire completed sequence.

Older scripts and analysis documents describe superseded sequences and are not loaded by the application.
