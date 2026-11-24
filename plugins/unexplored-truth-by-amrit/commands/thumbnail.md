---
description: Premium photoreal thumbnail banao (Nitish Rajput / Dhruv Rathee / Saqlain Khan style, 4K)
argument-hint: "[video ka title ya topic]"
---

Load and follow the `thumbnail-maker` skill of this plugin, section "Photoreal style".
Video / title from the user: $ARGUMENTS

First ask with AskUserQuestion (recommended option first): whose face (own photo / photoreal AI key person / none),
background (photoreal AI scene / real-photo collage / both), headline (2-3 words ending in "?").
Then give the ChatGPT prompts, wait for the images, cut out the face with `engine/thumbnail/cutout.py`, build it with
`engine/thumbnail/thumb_photoreal.py`, check at 360 px, and send the 4K JPG. Put it on YouTube only after approval.
