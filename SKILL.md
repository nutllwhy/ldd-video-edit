---
name: ldd-video-edit
description: A reusable editing workflow for creator-led talking-head videos, including shot planning, hand-drawn and collage MG, subtitles, assembly, and visual quality checks. Supports 4:3 landscape and 9:16 vertical projects.
---

# Creator Video Editing Workflow

This skill turns a finished recording and its supporting assets into a coherent edit. The narration is the source of truth; the edit decides what the viewer sees at each moment.

Before starting, read `references/rules.md`. Keep client briefs, private project notes, direct user quotations, and machine-specific paths outside this reusable repository.

```text
<project>/
  footage/       source recordings (read-only)
  work/          transcript, subtitle cues, and asset inventory
  plan.md        shot-by-shot edit plan
  look/          style references and selected-style notes
  anim/          animation source and rendered shots
  edit/          edit decision lists and frame checks
  deliverables/  versioned exports
```

## Review gates

| Gate | When | Required approval/check |
|---|---|---|
| G1 — Edit plan | Before assembly | Review the shot-by-shot plan, aspect ratio, music status, and any segments that should not show the speaker. |
| G2 — Style sample | Before rendering animation in volume | For an established series, render one frame from a key shot. For a new series, show the style gallery, select a few directions, then render the same key shot in each selected style. Record the chosen direction in the project workspace. |
| G3 — Final review | Before delivery | Run plan and seam checks, inspect representative frames and every edit point, and review character poses and prop contact where applicable. Automated checks do not replace visual inspection. |

If a required reviewer is unavailable, stop after the plan and sample rather than making a style decision on their behalf.

## Workflow

Set `SK` to the root directory of this cloned skill repository before running commands.

| Step | Work | Output / reference |
|---|---|---|
| 0 | Check dependencies | `scripts/check_env.sh` |
| 1 | Inventory media | `work/assets.md`: resolution, duration, aspect ratio, burned-in captions, sensitive content, and intended use. Re-check the folder before each revision pass — files are often added mid-project. See `references/materials.md`. |
| 2 | Transcribe and prepare speaker footage | `scripts/prep.sh` for landscape; `scripts/vertical_prep.sh` for vertical. |
| 3 | Correct transcript | Maintain a correction table and verify names, product terms, and English phrases before using them on screen. |
| 4 | Build the shot plan | `plan.md`: time, spoken line, layout, visual medium, on-screen content, and source for factual claims. Pass G1. |
| 5 | Create a style sample | Pass G2. |
| 6 | Make animation | Hand-drawn SK pipeline: `scripts/new_sketch.sh`; follow `references/sketch.md`. Paper-cut or dossier collage: `scripts/new_animation.sh`; follow `references/animation.md`. |
| 7 | Prepare subtitles | `scripts/cues.py`; verify semantic line breaks and timing. |
| 8 | Add music only if the approved plan calls for it | `scripts/bed.py` |
| 8b | Cut-out shots (VK / K), if planned | `scripts/cutout_compose.py`; copy the printed `subs_y` / `subs_shift` into the edit list. macOS only. |
| 9 | Assemble | Landscape: `scripts/assemble.py`; vertical: `scripts/assemble_vertical.py`. |
| 10 | Validate | `scripts/plan_check.py`, `scripts/seam_check.py`, then inspect frames. Pass G3. |
| 11 | Deliver | Versioned video, concise change notes, and any requested standalone animation clips. |

## Revisions

- Each round produces a new file (`v1`, `v2`, …); never overwrite the previous export.
- Cut on the assembled timeline so picture, captions, and effects move together. Choose cut points in the silence on either side of the removed line and add a short (~20 ms) audio fade at each join to avoid a click.
- Apply a correction everywhere the same problem occurs, not only at the timestamp that was pointed at. Fixing one face-covered caption but leaving the other split shots means another round.
- After each change, pull frames from the changed sections and from every layout boundary, and tile them into one contact sheet. State plainly in the delivery note which parts were checked this way and that the whole film was not watched second by second.

## Layout quick reference

### 4:3 landscape

- A — speaker full frame
- B — speaker with a restrained overlay
- P — picture-in-picture
- C — full-frame animation or media

### 9:16 vertical

- VA — speaker full frame
- VS — full-frame vertical media with a small circular speaker portrait
- VG — generated image shown whole, centred on a frosted copy of itself (default for demo-style edits)
- VC — full-bleed video with a small reference card lower left, no portrait
- VQ — 2×2 grid for an opening guess-the-shot sequence
- VH — 1:1 split: landscape media above, square speaker crop below, captions near the seam
- VK — cut-out: media card above, outlined speaker cut-out lower left on a frosted panel, optional chapter bar (`scripts/cutout_compose.py`)

Splits (VH) are for interface captures only; never split a plain image or product still.

The landscape equivalent is K (media card fills the frame below the chapter bar, cut-out overlaps its lower-left corner). See the cut-out section of `references/layouts.md`.

Use hard cuts between layout types unless the approved plan specifies an exception. Keep faces, captions, and important information inside safe areas; Crop portraits tight and centred with little headroom (L14); the only place that keeps space above the head is the lower half of a split, because the captions go there.

## Style selection

For a new series, start with `templates/sketch/styles/preview/menu.html`. The gallery includes five SK styles—pencil, journal, kraft, mono, and chalk—plus paper-cut and dossier collage. A–E share the same rendering kit and can be changed with `SK.page(svg, {style: 'journal'})`; see `references/sketch-styles.md`.

Characters should be symbolic drawings that use the same visual medium as the rest of the frame. The shared rig is a starting point; other vector characters are allowed when they are stylistically consistent. Avoid photorealistic likenesses and raster character cut-outs with separately programmed limbs.

## Updating the reusable skill

Generalize reusable lessons into `references/rules.md` and document implementation changes in `CHANGELOG.md`. Keep project-specific retrospectives, quotations, briefs, and source paths in the private project workspace, not in this public skill repository.

## Reference index

- `references/rules.md` — production and quality rules
- `references/layouts.md` — landscape and vertical layout dimensions
- `references/materials.md` — asset handling, verification, and privacy checks
- `references/edit-rules.md` — pacing, timing, captions, audio, and platform-neutral delivery
- `references/sketch-styles.md` — style gallery and SK presets
- `references/sketch.md` — SK pipeline, character motion, and checks
- `references/house-style.md`, `animation.md`, `motion.md`, `anti-ai-look.md`, `styles.md` — animation approaches
- `references/troubleshooting.md` — render, ffmpeg, dependency, and network failures
- `CREDITS.md` — source projects and license notes
