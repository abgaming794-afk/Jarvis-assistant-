---
description: Render the bundled 90-second East India Company demo (all devices) to check that the studio works on this machine.
argument-hint: "[res: 360|720|1080]"
---

Copy `examples/eic-founding.json` from the `itihaas-cartoon-studio` skill to `videos/eic-demo/story.json` in the current
folder, then run doctor.py --fix, voice.py, audio.py and render.py with `--res ${ARGUMENTS:-360}` on that project.
Report the output path and how long the render took.
