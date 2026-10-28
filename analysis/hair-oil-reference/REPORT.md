# Hair oil reference: complete frame review

Historical reference analysis. The current application uses newly generated artwork and a separate 1,400-sample animation; see `ASSETS.md` and `ORIGINAL_ART_PROMPTS.json`.

Source: `C:\Users\balaa\Downloads\gemini_generated_video_a0926e99.mp4`.

The requested product direction is Ayurvedic hair oil. This review treats imagery and printed words in the video as reference content, never as instructions. The current application's serum sequence has not been changed by this analysis.

## Verified source and deliverables

- 240 decoded video frames, 24 fps, 1280 × 720, landscape 16:9.
- Video runs 10.000 seconds. The container reports approximately 10.01 seconds including its audio track. Last video frame starts at 9.958333 seconds.
- Every original decoded frame is saved as a full-resolution PNG in `frames/`. No cropping, interpolation, retiming, or invented frames in this extraction. PNG preserves the decoder's RGB output; the compressed source itself is not lossless.
- All 240 images were visually reviewed across eight sequential contact sheets, 30 frames per sheet. This provides exhaustive temporal coverage at thumbnail scale; it is not a claim of a full-resolution pixel audit of each image.
- `review.html` provides individual full-resolution images, frame stepping, scrubbing and slow playback. `slow-025x.mp4` is a silent quarter-speed viewing copy.
- `frames.csv` and `manifest.json` record every frame's timestamp, path, SHA-256 and adjacent-frame change measurement. The change metric is mean absolute RGB difference at 160 × 90, useful for locating motion and cuts; it is not optical flow.

## Sequence, including all frame ranges

Frame numbering is one-based. Times below identify frame start timestamps; the following frame starts 1/24 second later.

| Frames | Time (s) | Visual action and continuity |
| --- | --- | --- |
| 1–10 | 0.000–0.375 | A dark, weathered bowl occupies the lower foreground. A walnut-like nut descends first, with a pale green amla-like fruit following. Sunlit foliage is blurred behind them. |
| 11–20 | 0.417–0.792 | First ingredients enter the bowl. Ridged brown seeds/nuts, clove-like spices and pink petals descend at staggered heights; red hibiscus enters from above. |
| 21–30 | 0.833–1.208 | Red hibiscus and a green leafy sprig move downward. Fruit and nuts gather inside the bowl. Ingredients rotate slightly as they fall. |
| 31–45 | 1.250–1.833 | Leaves, petals and flower settle toward the bowl's rim. The bowl stays near the lower center while the last airborne pieces disappear into the arrangement. |
| 46–54 | 1.875–2.208 | Filled-bowl composition briefly steadies. A golden lip of oil becomes visible at the front-right rim near the end of this interval. |
| 55–60 | 2.250–2.458 | Bowl starts lifting and tilting. Oil thickens over the front-right lip into a short glossy tongue. The ingredients remain visibly arranged in the bowl. |
| 61–72 | 2.500–2.958 | Bowl travels upward and tilts further. The golden tongue stretches into a broad, continuous pour, reaching beyond the bottom edge. Bright reflections trace its edges. |
| 73–81 | 3.000–3.333 | The lifted bowl holds its pouring pose. Stream remains thick, with changing folds and highlights. No receiving bottle is visible in this shot. |
| 82–96 | 3.375–3.958 | Hard cut to a new framing: open transparent bottle below the bowl, golden oil entering its narrow neck. Background changes to a warm beige wall with green foliage around the edges. |
| 97–105 | 4.000–4.333 | Continuous filling. Amber level climbs through the lower visible bottle. Liquid folds and bubbles are visible inside. Camera reveals more of the bottle. |
| 106–120 | 4.375–4.958 | Pour becomes progressively narrower. Bubbles remain visible beneath the oil surface; highlights and glass edges stay warm and reflective. |
| 121–132 | 5.000–5.458 | A very thin filament continues, then breaks into the last drips. Bowl withdraws upward and leaves the frame. Bottle remains open. |
| 133–140 | 5.500–5.792 | Cream label appears as an upright panel beside/behind the bottle and wraps across its front. Botanical artwork comes into view. A black cylindrical cap descends from above. This is a stylized assembly effect. |
| 141–150 | 5.833–6.208 | Cap appears seated. Label finishes rotating/wrapping toward the viewer. Large product wording reads “AYURVEDIC HAIR OIL”; small brand/detail text is too unstable or small to transcribe confidently. |
| 151–162 | 6.250–6.708 | Camera pulls back, revealing more of the bottle and ingredients around its base. The botanical panel at the right contracts out of view as the wrap/reveal resolves. |
| 163–174 | 6.750–7.208 | Full product composition settles: tall clear bottle of amber oil, black cap, cream botanical label, rustic pale stone base, nuts and green fruit to the left, red hibiscus to the right. |
| 175–192 | 7.250–7.958 | Hero hold begins with slight continued camera settling. Product centered, framed by softly focused ferns, leafy branches and warm stone/plaster tones. |
| 193–216 | 8.000–8.958 | Extended hero hold. Composition remains consistent, with minor changes in foliage, lighting and framing rather than a new action. |
| 217–240 | 9.000–9.958 | Final product portrait continues to the end. No further scene cut, application demonstration or scalp/hair shot appears. |

Ingredient identities above are visual interpretations, not a verified formula. The clip does not establish ingredient amounts, manufacturing process or product efficacy.

## Visual direction to carry into the project

The scene uses muted botanical greens, warm beige, dark earthy brown and golden amber, with small red and pink floral accents. Light enters mainly from the upper right, creating warm glass and oil highlights. The setting is a garden or courtyard with natural stone and soft foliage, shallow depth of field, and realistic material textures.

The main motion is a staged progression: ingredient descent → bowl tilt → thick pour → bottle fill → cap/label assembly → slow product reveal. It uses an actual hard cut between frames 81 and 82; this must remain a cut for a source-faithful result. Filling and the assembly sequence occupy the middle of the film; the last roughly three seconds provide time to read the product.

This replaces the visual logic of the current orange skincare story. The existing code contains splash, cheek, massage and skin-result phases, skin-specific crops, header adjustments and serum copy. Those choices do not map onto this reference. A later website implementation should define new phases and text windows from this timeline, use the natural 16:9 composition as its baseline and inspect mobile crops separately. In portrait, a full-bleed center crop can remove the descending ingredients, bowl rim or the end of the stream.

## Exactness and frame count

For the closest visual match, use these extracted source frames in order, or the original video, retaining color, framing, cut and timing. Independently generating each image would risk changes in bottle shape, label, ingredient positions and liquid continuity.

The source contains 240 frames, not 2,000+. Generating 2,000 output frames would require duplication or interpolation (about 8.33 output frames per source frame). Duplication adds no motion information; interpolation estimates new poses and can distort thin oil streams, petals, glass and lettering. It should be separately reviewed if later requested. A longer scroll runway or slow playback can show all original frames slowly without inventing intermediate imagery.

## Reproduce the extraction

```powershell
& '.tools/python/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe' -hide_banner -loglevel error -i 'C:\Users\balaa\Downloads\gemini_generated_video_a0926e99.mp4' -map 0:v:0 -fps_mode passthrough 'analysis/hair-oil-reference/frames/frame_%04d.png'
python scripts/analyze_hair_oil_reference.py
```

The supplied script uses the existing Pillow installation under `.tools/python`; extraction uses the existing local FFmpeg binary. No new packages are required.
