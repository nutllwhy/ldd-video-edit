# Production rules

These are reusable checks for the editing and animation workflow. Keep case-specific findings and source material in the private project workspace; do not add client briefs, personal quotations, or identifying project details here.

Before each edit, review the relevant rules below. At delivery, verify them against the final render rather than relying on memory.

## How to add a rule

1. Add a short, executable rule to the relevant section and keep numbering stable.
2. Record the general failure mode and a reproducible self-check; do not copy private project notes into this repository.
3. If a rule changes, mark the older guidance as superseded and explain the implementation change in `CHANGELOG.md`.
4. Automate checks where reliable; retain visual review for anything involving aesthetics, contact, or anatomy.

## S · Narration and sound

| ID | Rule | Self-check |
|---|---|---|
| S1 | Preserve the approved narration and delivery. Only remove stumbles, repeated takes, or clear mistakes; do not reorder sentences or change speed without approval. Re-transcribe after cuts. | List every removed range in delivery notes; compare transcript to the final audio. |
| S2 | Let the final spoken phrase finish. Fade music independently; avoid cutting speech at the end. | Listen to the final three seconds. |
| S3 | State whether music is included in the G1 plan and obtain approval before generating or adding it. | Confirm the plan records music: yes/no. |
| S4 | Keep voice loudness consistent; target approximately -16 LUFS integrated and no higher than -1 dBFS true peak unless the delivery spec says otherwise, and put a limiter last in the chain. | Measure with `ffmpeg` loudness analysis. |
| S5 | Maintain a transcript correction table. Verify names, product terms, and foreign-language phrases before using them in captions or graphics. | Review corrected text against the approved script and audio. |
| S6 | Keep sound effects sparse: roughly one every 15–20 seconds in a short explainer is already a lot, and one signature accent (a single reveal chime) per film. Do not attach an effect to every graphic that appears. | Count effect cues in the edit list; listen once with the voice muted, then together. |
| S7 | Inserted material clips, screen recordings, and b-roll carry no audio — mute them instead of pulling the voice down to match. | Check every imported clip's audio state in the edit list. |

## H · Opening and ending

| ID | Rule | Self-check |
|---|---|---|
| H1 | Give the opening three seconds a clear hook: a meaningful action, contrast, reveal, or verified visual. Avoid a slow generic title fade. | Review the opening without sound; ask what creates the reason to keep watching. |
| H2 | If the format relies on a speaker-led opening, keep the first spoken phrase visually connected to the speaker before moving to supporting visuals. | Check the first phrase and first layout change. |
| H3 | End on a meaningful human or visual beat, not an unmotivated quote card. | Inspect the final shot in context. |
| H4 | When an approved, relevant finished example is the strongest hook, show it before explaining it. | Confirm it is authorized and immediately understandable. |

## F · Speaker visibility

| ID | Rule | Self-check |
|---|---|---|
| F1 | Cover segments where the speaker is visibly reading, not looking at the intended audience, or holding an unusable expression, if the approved plan calls for a visual cover. | Sample the recording regularly and list excluded intervals in the plan. |
| F2 | Avoid long uninterrupted speaker shots; vary the visual treatment when the narration supports it. | Run `scripts/plan_check.py`. |
| F3 | Do not expose a very brief sliver of a face between two visual sections. Join shots cleanly or hold the speaker long enough to read as intentional. | Run `scripts/plan_check.py` and `scripts/seam_check.py`. |

## L · Layout

See `layouts.md` for dimensions and safe areas.

| ID | Rule | Self-check |
|---|---|---|
| L1 | Use a small, explicit set of layout codes in the edit plan; choose the layout based on whether the speaker, an artifact, or an animated idea is the focal point. | Every planned shot has a layout code. |
| L2 | Vertical media can fill a 9:16 frame; keep captions clear of the speaker portrait and interface-safe areas. | Inspect the portrait and captions at phone size. |
| L3 | For landscape media inside a vertical video, use a deliberate split or crop; do not leave accidental empty bars. | Inspect the frame at delivery size. |
| L4 | Keep circular portraits centered with headroom and shoulders visible where possible (for the small portrait of a demo-style edit see L14). | Enlarge several frames from each portrait section. |
| L5 | Use hard cuts between distinct layouts unless a transition is approved and motivated. | Inspect every layout boundary. |
| L6 | Vary framing or position across consecutive shots so a sequence does not become a static template. | Review three consecutive shots together. |
| L7 | Do not place large text cards over a speaker's mouth when the spoken subject is the focus. | Inspect captions and graphic overlays against the face. |
| L8 | Keep captions and important graphics inside the delivery format's safe areas. | Check all edges and platform interface zones. |
| L9 | Cut-out layouts (VK / K) put the speaker in front of the media card, offset to one side, on a frosted panel; the speaker never covers the card's key content, and captions move into the free zone the script reports (`subs_y` / `subs_shift`). | Inspect the outline at 200% on hair, hands and held props; check captions do not touch the face or the card. |
| L10 | A top chapter bar is an opt-in element for structured explainers with 3–5 chapters, never a default; equal-width segments, labels centred over their segment, the current segment highlighted. Do not combine it with page numbers or chapter counters. | Confirm the brief asked for it; check each switch time against the narration. |
| L11 | Present generated images and effect outputs whole. Never crop them to fill a ratio or to fit a layout — the cropped edge is often the exact thing being shown. Change the layout or add a matte instead. | Compare the displayed area with the source image; confirm no edge content is lost. |
| L12 | In a demo-style edit the artifact is the subject: show the effect before the person, and bring the speaker in only where the narration is personal — as a small portrait in the lower-left corner. Reserve full-frame speaker shots for emphasis and the closing line. | Measure how much runtime the speaker is visible; check the artifact is never shrunk to make room for a large face. |
| L13 | Reserve the split layout for interface captures (screen recordings, web pages, app UI). Do not split a plain generated image or a product still. | List every split shot and name the interface it shows. |
| L14 | When a face has to be cropped out of a wider frame for a small portrait, crop toward the centre: more face, only a little headroom. Empty space above the head is wasted inside a small circle. | Inspect the portrait at phone size; the face should read at a glance. |

## M · Source media and factual claims

| ID | Rule | Self-check |
|---|---|---|
| M1 | Do not add unrequested vignettes, gradients, masks, or filters to source footage. | Compare a rendered frame with the source at the same timestamp. |
| M2 | Avoid doubling burned-in captions with new captions; crop, scale, or select another source segment. | Inspect every source segment with embedded text. |
| M3 | Use the current, correct product mark when a logo is required. Normalize transparent bounds and visual size; do not substitute an unrelated parent mark or favicon. | Review a logo comparison sheet at full size. |
| M4 | Keep codes, QR codes, and calls to action subordinate to the main scene and within approved platform rules. | Inspect their size, placement, and duration. |
| M5 | For cross-platform delivery, remove irrelevant platform UI, watermarks, account handles, and identifiers from source captures unless explicitly required and approved. | Review every screenshot, recording, and export. |
| M6 | Every factual number shown on screen must have a source in the plan. Do not put invented values into illustrative diagrams. | Trace each displayed number to a source. |
| M7 | Check unfamiliar proper nouns, product modes, and functions against an authoritative source or the approved script before drawing them. If unresolved, omit them or ask for clarification. | Maintain a source/check column in the plan. |
| M8 | Treat internal, event, or partner-provided figures as unpublished until permission is confirmed. | Mark each such figure as approved, withheld, or pending. |

## A · Animation and visual design

| ID | Rule | Self-check |
|---|---|---|
| A1 | Before rendering animation in volume, produce a frame or style options and pass the G2 review. | Store the chosen direction in the project workspace. |
| A2 | Pick one primary medium per shot. If a sequence changes medium, make the transition deliberate. | Review adjacent shots together. |
| A3 | Avoid default template palettes and generic effects. Follow `anti-ai-look.md` and the chosen style specification. | Compare the render with the style reference at phone size. |
| A4 | Keep full-frame animated shots concise; split a long argument into meaningful visual beats. | Run `scripts/plan_check.py`. |
| A5 | Use labels and decorative text sparingly. Avoid chapter counters, source badges, ornamental rules, and labels pasted over source footage. | Inspect every frame for unneeded annotations. |
| A6 | Use brief source flashes only when they support the argument; alternate media and avoid repeating the same image without a reason. | Review the source sequence in context. |
| A7 | Export requested standalone MG segments in sequence, without audio, at their original dimensions. | Compare the standalone exports against the final edit. |
| A8 | Let spoken structure and the scene itself provide section changes; avoid slide-like chapter markers and decorative bars. | Inspect corners, title areas, and overlays. |
| A9 | For hand-drawn scenes, use the SK pipeline and show a representative frame before scaling production. | Check paper/line texture, motion, and restrained accent use. |
| A10 | Draw characters symbolically in the same medium as the scene. The shared stick-figure rig is a default, not a limit; simple vector characters are acceptable when stylistically consistent. Avoid photorealistic likenesses and raster characters with separately programmed limbs. | Inspect line, fill, texture, and character-to-prop contact in rendered frames. |
| A11 | Make shoulders, elbows, and resting poses readable. Do not let the upper arm merge with the torso or the forearm cross the waist without a clear action. | Run `scripts/arm_pose_check.mjs`, then inspect key poses and transitions visually. |
| A12 | In a footage-led edit (real product images, recordings, generated stills), keep backgrounds, cards, and captions in a restrained, designed register; reserve hand-drawn or cartoon treatments for short accent captions. A notebook doodle across the whole frame reads as a different genre. | Compare a rendered frame with the approved style sample; ask whether the type, card, and background look designed or drawn. |
| A13 | Do not add annotations of your own (circles, arrows, labels) on top of a source frame that already carries marks. Reuse the existing marks or pick a clean frame. | Inspect each source frame for pre-existing annotations before drawing anything. |

## E · Assembly and captions

| ID | Rule | Self-check |
|---|---|---|
| E1 | Add a small overlap/hold at joins where needed to avoid a missing frame from timing precision. | Run `scripts/seam_check.py`. |
| E2 | Inspect frame differences around each cut; multiple consecutive isolated flashes indicate a seam problem. | Run `scripts/seam_check.py` and review flagged frames. |
| E3 | Break captions by meaning and keep line length appropriate to the frame size. | Inspect at phone size and listen against the narration. |
| E4 | Save each revision under a new versioned filename; do not overwrite the previous deliverable. | Confirm versions exist in the project folder. |
| E5 | Captions follow the layout that is on screen. When one spoken sentence crosses a layout change, split the cue at the cut so each part sits in the new layout's caption zone. A cue positioned once from the layout at its start will end up over a face. | Check every cue that spans a layout boundary against the frame at that moment. |
| E6 | When a source clip is much longer or shorter than its line (e.g. 9.6 s of recording for 3.1 s of narration), do not silently speed it up. Offer three options — extend the shot, use only the best segment, accept the speed change — and wait for the decision. | List mismatched clips with both durations in the plan. |

## D · Delivery

| ID | Rule | Self-check |
|---|---|---|
| D1 | Summarize edits in terms of visible changes, removed ranges, and corrected text; avoid burying the outcome in implementation detail. | Compare delivery notes with the approved feedback and final render. |
| D2 | Inspect a representative frame from every shot, frames around every cut, and any specifically flagged timestamps. | Keep a contact sheet and full-resolution checks in the project workspace. |
