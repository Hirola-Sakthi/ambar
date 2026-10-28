# Historical full-screen remaster

Superseded by the newly generated artwork documented in `ASSETS.md` and `ORIGINAL_ART_PROMPTS.json`. These notes describe the previous video-derived version, which is no longer used by the application.

The production sequence is rendered by `scripts/render_hair_oil_hq.py` from the original 10-second video. This is a source-derived video remaster. It is not a collection of 1,400 independently generated photographs, and 1080p upscaling does not recover new captured detail from the 720p source.

## Processing

- Corner sparkle removed with FFmpeg's video `delogo` filter at source rectangle x=1129, y=568, w=64, h=65. Surrounding pixels reconstruct the marked background; this region is an approximation.
- Shots split at 3.375 seconds, the original hard cut. First shot becomes 473 frames; second becomes 927. Motion estimation never crosses the cut.
- Adaptive overlapped block motion interpolation, bilateral estimation, EPZS search and variable block sizes create intermediate poses. The original shot endpoints are retained. Optical flow can produce local edge artifacts around petals, nuts, thin liquid and lettering; it is not a new fluid simulation or a guarantee of added realism.
- Lanczos upscale to 1920 × 1080, gentle sharpening, WebP quality 95. This replaces the earlier 240-frame lossless source export for delivery.
- Full-screen `cover` framing, centered on the bottle and bowl, replaces letterboxing. Portrait devices intentionally crop the landscape edges.
- Decoded frame cache limited to 32 desktop frames / 24 mobile frames; mobile bitmap decodes at 1280 pixels wide. The full 1,400-frame set is not loaded into decoded memory at once.

Assets are in `public/scenes/hair-oil-hq/`. `hair-oil-poster-hq.webp` is the remastered first frame. Original extracted PNGs remain in the analysis folder for reproducibility.

## Generated product photograph

Built-in imagegen edit, saved to `public/scenes/hair-oil-product-hq.png`; used only in the product section so an independently generated still does not create a jump inside the source-derived animation. The model returned a 1672 × 941 image. Fine label lettering is generated and should be replaced with final approved packaging artwork before commercial use.

Final prompt:

> Use case: precise-object-edit. Edit target: the provided Ayurvedic hair oil product reference still. Create a high-quality 1920x1080 landscape product photograph, preserving this exact composition, bottle silhouette, black cap, amber oil, cream botanical label artwork and visible label text, red hibiscus, amla fruit, nuts, stone plinth, sunlit botanical garden backdrop and warm natural lighting. Remove ONLY the small pale four-point sparkle watermark near the lower right (around x1160,y600 in the 1280x720 input), replacing it with continuous natural foliage/background. Improve fine photographic clarity gently without invented wording or changes to the product. Preserve the centered bottle scale and framing. No watermark, no added symbols, no UI.

Regenerate the video frames with:

```powershell
python scripts/render_hair_oil_hq.py
```

The script renders into a versioned directory and switches `src/sequenceManifest.json` only after verifying that all 1,400 numbered output paths exist.
