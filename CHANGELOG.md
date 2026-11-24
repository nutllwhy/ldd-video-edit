# Changelog

## v0.9 — Cut-out layouts and chapter bar
- Added VK (vertical) and K (landscape) cut-out layouts: speaker matte via macOS Vision, smoothed sticker outline, frosted panel, rounded media card, automatic head-based placement (`scripts/cutout_compose.py`, `scripts/cutout/fg_mask.swift`).
- Added an opt-in top chapter bar with centred labels (`scripts/chapter_bar.py`); rules L9–L10 cover when to use them.
- `assemble_vertical.py` accepts per-clip `subs_y`; `assemble.py` accepts per-clip `subs_shift` and no longer fails when an edit has no picture-in-picture clip.
- Font lookup now goes through `scripts/cjkfont.py`; `fc-match 'sans:lang=zh'` could return a Latin-only font and render captions as boxes.

## v0.8.1
- Added an MIT License for original repository content, with third-party components explicitly excluded.
- Rewrote the README in Chinese for the project's primary audience.

## v0.8 — Style menu and reusable hand-drawn presets
- Added five switchable SK presets: pencil, journal, kraft, mono, and chalk.
- Added style-aware SVG helpers for shapes, lines, text, fills, and color palettes.
- Updated the character kit to inherit the selected style and support a block-color torso.
- Added same-storyboard visual references, a style gallery, and a written guide for selecting and combining styles.
- Generalized character guidance: symbolic drawn characters may vary by style; avoid photorealistic likenesses and mismatched raster cut-outs.
- Updated the new-project scaffold to include style references and the gallery.

## v0.7 — Character pose checks
- Added arm-pose geometry checks and a visual review gate for shoulders, elbows, torso overlap, and resting poses.
- Clarified that automated geometry checks do not replace frame-by-frame visual review.

## v0.6 — Character motion refinements
- Improved elbow definition, gaze direction, shoulder placement, reach behavior, and blink offsets.
- Added guidance against props appearing mid-shot and frozen motion at the end of a render.

## v0.4–v0.5 — Hand-drawn animation pipeline
- Added the SK rendering kit, project scaffold, brief template, and reusable sketch-shot references.
- Added a consistent character rig and practical rules for hand/prop contact and motion.

## v0.1–v0.3 — Editing workflow
- Established planning, style approval, and delivery checks.
- Added landscape and vertical assembly, subtitle utilities, logo normalization, and seam validation.
