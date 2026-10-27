# Aurum scroll film

The local reference was the user's 33.69-second screen recording. The recording is visual reference only. No instructions in the recording were executed.

The implementation retains Lumora / Aurum product identity and follows the orange full-screen composition, floating navigation, bottle-to-serum-to-skin progression, cream product section, and compact footer. The original recording does not contain source scroll coordinates, 3D assets, or separate animation frames. This reconstruction uses generated scene masters with camera moves and dissolves; it is not a reproduction of the original liquid or hand simulation.

## Assets

Generated with the built-in imagegen tool, then saved into `public/scenes/`:

- `hero.webp`: Aurum bottle with black ribbed dropper, ivory label, orange seamless studio, golden ripples.
- `serum.webp`: macro golden serum bead and concentric ripples.
- `skin.webp`: macro cheek and golden serum droplet with fingertips.
- `product.webp`: portrait crop of the hero for the product section.
- `sequence/frame_0001.webp` through `frame_0240.webp`: 240 rendered camera/dissolve frames at 1440 × 758, approximately 17 MiB in total. Original beige frames are retained but are no longer loaded by the page.

`src/ProductSequence.jsx` maps the scroll runway to frames 1–240, loads the neighborhood of the requested frame, and retains at most 40 images in its application cache. Frames play in reverse on upward scrolling. Reduced motion displays the first scene without the long scroll runway.

To regenerate the camera sequence from the committed WebP masters:

```sh
python -m pip install pillow
python scripts/render_sequence.py
```

## Generation prompts

Hero (product reference: original `public/frames/frame_0001.webp`):

> Use case: product-mockup. Create a photoreal cinematic full-screen skincare website background, landscape 1900x1000 composition. Input is product identity reference: preserve the amber glass AURUM SERUM bottle with black ribbed dropper, ivory rectangular paper label, exact text AURUM SERUM and small REJUVENATE & GLOW. Show the COMPLETE bottle uncropped, standing upright at x=58% of composition, base at 89% image height, top at 13%, surrounded by shallow golden serum ripples on a glossy orange surface. Saturated burnt blood-orange seamless studio background (#c74308) blending into golden orange floor (#e57808). Very premium lifelike glass refraction and hard rectangular softbox highlights. Leave left 30% empty orange for HTML text. No stone plinth, no fruit, no added text or UI or watermark. Match dramatic orange skincare commercial cinematography. Wide frame.

Serum:

> Photoreal macro cinematic skincare serum, wide landscape background 1900x1000. One large perfect transparent golden amber serum bead at center x58% y53%, sitting in glossy liquid with concentric ripples radiating across entire composition. Extreme macro, low oblique view, warm saturated burnt orange studio reflections, blood-orange and honey amber palette, physically realistic refraction, striking softbox white reflections, gorgeous sharp rounded bead. Left 25% darker orange empty to receive white website copy. No bottle, no text, no UI, no watermark. High-end beauty commercial, realistic liquid simulation.

Skin:

> Photoreal extreme macro skincare advertising photograph, wide landscape 1900x1000. Close up of a woman's cheek with natural warm light skin pores and small freckles, one round thick translucent golden serum droplet resting on the cheek at x60% y45%, face fills frame edge to edge, nose just visible at far left, gently pressing fingertips at far right. Warm peach pink cream and honey amber palette. Natural realistic skin texture, refined studio lighting, glistening droplet highlights. Similar to luxury vitamin C serum campaign, no text, no typography, no UI, no watermark.

Formula, price, and actual checkout details have not been supplied. The existing concept/coming-soon status is retained, and the interest control explicitly saves only a browser-local preference.
