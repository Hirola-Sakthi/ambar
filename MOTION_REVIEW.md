# Latest cinematic video motion

The current sequence imports every frame of the user's new 1080p video. It replaces the previous generated-art animation. Detailed processing and provenance are in [the current video review](analysis/cinematic-hair-oil/README.md).

| Phase | Native frames, one-based | Source time |
| --- | --- | --- |
| Empty bowl | 1–24 | 0–1 s |
| Falling ingredients | 25–72 | 1–3 s |
| Bowl lift and pour | 73–108 | 3–4.5 s |
| Bottle filling and label | 109–180 | 4.5–7.5 s |
| Cap placement | 181–204 | 7.5–8.5 s |
| Product reveal | 205–240 | 8.5–10 s |

No native samples are omitted or replaced. The video is continuous; camera movement and transitions remain as supplied. The fixed corner sparkle is removed locally, then each processed sample is encoded as lossless WebP at 1920 × 1080. There is no artificial frame inflation or motion interpolation.

The scroll film uses the same sequence in reverse when scrolling upward. Full-screen mobile framing follows the centered bowl and bottle. Text fades align with the source ingredient, pouring, packaging and final product actions. Reduced motion keeps the empty-bowl poster and shortens the section to one viewport.
