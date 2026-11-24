# Cinematic dossier style (from the user's 23-second reference recording)

The user's main editing look. Apply it by default to long videos unless asked otherwise. Recreate the techniques with our own assets, fonts and colors; never reuse another channel's footage, graphics, logo or music.

## Overall feel

- Every shot is a photoreal, film-lit still (AI-generated or licensed) that is never static: slow push-in, drift or parallax on every frame.
- Beat length about 2.5-3.5 seconds; a new visual event (photo drops, text types, circle draws, wipe) every 1-1.5 seconds inside a beat.
- Few hard cuts. Most changes are continuous camera moves or object-driven transitions (a book slides in, paper tears, the camera pulls back).
- Color grade: warm amber/gold for "public life" scenes, teal-and-orange for power or meeting rooms, desaturated black-and-white for secret or hidden identity. Light film grain and soft vignette throughout.
- Small "AI-generated illustration" label in the bottom-left corner on every generated image, about 1.5% of frame height, 60% white.

## Signature moves (in the order they appear in the reference)

1. **Photo collage on a desk.** Dark wood table with a faint world-map texture. Printed photos with a white border drop in one by one (scale 1.15 -> 1, rotate +-2-6 degrees, soft shadow, paper-slap sound), stacking into a 2x2 collage while the camera drifts.
2. **Pull-back reveal.** Camera pulls back from the collage to show it pinned on a studio wall; the main character sits in a wooden chair in a lit room beside it.
3. **Image-filled title.** Huge bold condensed title (the subject's name) where the letters are a mask filled with a photo collage, slight 3D extrude and shadow. Letters push in, then the camera flies through a letter into the next scene.
4. **Dossier book.** An old open book or file slides up from the bottom, held by a hand at the edge. Left page: big stencil label typing in ("PRESIDENT CONTENDERS"). Right page: list with small portraits.
5. **Hand-drawn circle.** Orange marker circle draws around the key name over 12-18 frames with a marker sound, slight wobble.
6. **Passport photo pop.** A vintage portrait photo pops out of the page toward camera, then the camera dives into the page to the next detail (name, rank, "UNDER CONSIDERATION"), which gets its own circle.
7. **Portrait name card.** Tight cinematic portrait on one side; on the other, white bold condensed name types in letter by letter with grain and a small glow, two lines.
8. **Torn-paper split reveal.** A ragged torn-paper edge wipes in from the side, revealing a black-and-white "other identity" version of the same person. A gritty yellow stencil word ("SPY") slams in with a thud and dust.
9. **Flag sweep.** A waving flag sweeps across the frame as a wipe to the next scene.
10. **Typographic portrait.** Final hero shot: black-and-white portrait built from newspaper text and clippings (double exposure), big distressed headline text on the left, waving flag on the right, slow push-in.

## Build notes (Remotion)

- Stills: `Img` in a container with `scale` 1 -> 1.08 and small x/y drift over the shot; 2.5D layers from `effects-recipes.md` for hero shots.
- Collage: array of photo cards with staggered `spring` entries (8-10 frames apart).
- Image-filled title: SVG `<text>` as a `clipPath` (or CSS `background-clip: text`) over a collage; add a darker offset copy for extrusion.
- Book and hand: pre-made book and hand PNGs with alpha; page content is live text and images so names can change.
- Marker circle: SVG ellipse path with `strokeDasharray`/`strokeDashoffset`, rough edge via a small `feTurbulence` displacement (pre-render if slow).
- Torn paper: an SVG mask with a jagged edge path, translated across the frame over 10-14 frames; paper-tear sound.
- Stencil word: distressed texture masked into the text, scale 1.6 -> 1 with 3 frames of shake.
- Typographic portrait: high-contrast grayscale portrait multiplied over a newspaper-text texture.

## Sound

Low cinematic drone bed under the voice; risers before reveals; paper slap for photo drops; marker squeak for circles; whoosh for camera dives; heavy hit for title and stencil slams; paper tear for split reveals.

## Content rules

- Generated images of real historical people or events are illustrative reconstructions: label them on screen, keep them to documented events, and never present a generated "document" or photo as a genuine archive record.
- Text on generated documents must match the research dossier exactly; generated text is re-typed as live text, never left as AI-rendered lettering.
