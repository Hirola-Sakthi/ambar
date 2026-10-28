# Herbal oil advertisement source frames

Source: `Herbal_oil_bottle_advertisement_3860f7b0_1080p_gwr_video_mvp.mp4`
from the user's Downloads directory. The imported sequence is in its own
folder, `public/scenes/herbal-oil-advertisement/`.

Every native video frame is exported in order at the source's 1920 x 1080
resolution and 24 fps, using lossless WebP. No frame-rate conversion,
interpolation, resizing, retouching, sharpening, watermark removal or generated
artwork is applied. The source video's H.264 compression is already present;
the export preserves the decoded RGB pixels without adding lossy compression.

An independent FFmpeg RGB decode writes `source-rgb.framemd5`. Every exported
image is decoded with Pillow and its RGB MD5 compared with the matching video
frame. Import fails without activating the sequence if any pixel hash, frame
count, filename or dimension differs. `manifest.json` records the source hash,
native frame count, timestamps and per-file SHA-256 hashes. `frames.csv` is a
compact index. Numbered contact sheets cover every frame; `storyboard.jpg`
is a lightweight overview rather than a delivery asset.

`poster.webp` is an exact copy of the first frame. `product.webp` is an exact
copy of the final frame. The animation, poster and shop image all read the new
active directory from `src/sequenceManifest.json`, with a source-hash revision
to invalidate old browser caches. The canvas supports up to 2x display density
and high-quality image smoothing. Prior frame folders remain intact.

Reproduce with `python -B scripts/import_herbal_video.py`. The script uses
Pillow and imageio-ffmpeg, available in this checkout's `.tools/python`.
`--source <path>` selects the input. An interrupted import can use `--resume`;
every reused image is still checked against the independently decoded video.

Completed import: 239 native frames, 1920 x 1080, 24 fps, 9.958333 seconds.
Every RGB hash matches the source. Frame files total 215.7 MiB; the poster
and product still are additional exact endpoint copies. All 239 frames are
included in the production build.

Validation passed: `npm.cmd run build`, forward and reverse Chromium playback
at 1440 x 810 and 390 x 844 with 2x display density, poster and shop image
loading, and reduced-motion playback on frame 1. Only the new source folder
was requested for scene assets; no JavaScript errors or failed scene requests
occurred. `browser-qa.json` and `browser-*.png` contain the browser evidence.
