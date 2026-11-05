# Tutorial video

An 18m44s narrated walkthrough of the whole engagement (requirements, tools, each day, eight challenges and
their solutions, results, teardown, lessons). 28 scenes, 1080p, soft subtitles and chapters.

## Rebuild
```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build.py                  # frames, narration, video
.venv/bin/python build.py --scenes 1,5     # only some scenes (checking visuals)
.venv/bin/python build.py --frames-only    # screenshots only
```
Needs Google Chrome (`/usr/bin/google-chrome`), ffmpeg, and network access for the neural voice.
Output goes to `output/` (not committed): the `.mp4`, an `.srt`, and `chapters.txt` for a YouTube description.

## How it works
- `scenes.py` is the storyboard: each scene is a visual plus one narration line per beat.
- `lib.py` holds the HTML components. Every element has a beat number and appears when that line starts.
- `build.py` screenshots one frame per beat, enlarges each scene to fill the frame, narrates with edge-tts
  (`en-GB-RyanNeural`), assembles with ffmpeg, and normalises loudness to -16 LUFS.
- `pronunciations.yaml` fixes how acronyms are spoken (audio only; subtitles keep the original spelling).

## Notes
- Needs edge-tts 7.3.1 or newer: older versions get a 403 from Microsoft's service.
- The AWS account ID is never shown or spoken, so the video can be shared.
- Figures match `docs/day9_verification.md` (62 to 38 counted failures).
