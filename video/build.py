#!/usr/bin/env python3
"""Build the project tutorial video: HTML scenes -> frames, edge-tts narration, ffmpeg assembly.

    .venv/bin/python build.py                 # everything
    .venv/bin/python build.py --scenes 1,5    # only these scenes (for checking visuals)
    .venv/bin/python build.py --frames-only   # screenshots only, no audio or video

Outputs in output/: aws_cis_assessment_tutorial.mp4 (soft subtitles + chapters), .srt, chapters.txt
"""
import argparse
import asyncio
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import edge_tts
import yaml
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
BUILD, OUT = ROOT / "build", ROOT / "output"
FRAMES, TTS, SEG = BUILD / "frames", BUILD / "tts", BUILD / "seg"
VOICE, RATE = "en-GB-RyanNeural", "+0%"
LEAD, TAIL, FPS = 0.45, 0.75, 24
PRON = yaml.safe_load((ROOT / "pronunciations.yaml").read_text()) or {}
NAME = "aws_cis_assessment_tutorial"
# Enlarge each scene's body until it just fills the frame (text stays readable on a phone).
FIT = """() => { const b = document.querySelector('.body'); if (!b) return 1;
  const ok = () => { let mb = 0, mr = 0;
    b.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect();
      if (r.width > 0) { mb = Math.max(mb, r.bottom); mr = Math.max(mr, r.right); } });
    return mb <= 985 && mr <= 1835; };
  for (let z = 1.6; z >= 1.0; z -= 0.05) { b.style.zoom = z; if (ok()) return z; }
  b.style.zoom = 1; return 1; }"""


def sha(*parts):
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:16]


def spoken(text):
    for k in sorted(PRON, key=len, reverse=True):
        text = re.sub(rf"(?<![\w]){re.escape(k)}(?![\w])", str(PRON[k]), text)
    return text


def page_html(scene_html):
    from lib import CSS
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{scene_html}</body></html>"


def render_frames(scenes, force=False):
    FRAMES.mkdir(parents=True, exist_ok=True)
    todo = []
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        page = br.new_page(viewport={"width": 1920, "height": 1080})
        for sc in scenes:
            key = sha(sc["html"])
            paths = [FRAMES / f"{sc['id']:02d}_{key}_{n}.png" for n in range(1, len(sc["beats"]) + 1)]
            sc["frames"] = paths
            if not force and all(x.exists() for x in paths):
                continue
            page.set_content(page_html(sc["html"]))
            page.evaluate(FIT)
            for n, path in enumerate(paths, 1):
                page.evaluate("""n => document.querySelectorAll('[data-b]').forEach(
                    e => e.classList.toggle('on', Number(e.dataset.b) <= n))""", n)
                page.screenshot(path=str(path))
            todo.append(sc["id"])
        br.close()
    return todo


async def tts_all(jobs):
    TTS.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(4)

    async def one(text, path):
        if path.exists() and path.stat().st_size > 1000:
            return
        async with sem:
            for attempt in range(5):
                try:
                    tmp = path.with_suffix(".part")
                    await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(tmp))
                    tmp.rename(path)
                    return
                except Exception as e:  # network hiccup: back off and retry
                    if attempt == 4:
                        raise
                    await asyncio.sleep(2 + attempt * 2)

    await asyncio.gather(*(one(t, p) for t, p in jobs))


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def build_segment(png, mp3, dur_audio, first, out):
    total = LEAD + dur_audio + TAIL
    vf = "scale=1920:1080,format=yuv420p" + (f",fade=t=in:st=0:d={LEAD}" if first else "")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-i", str(png), "-i", str(mp3),
           "-af", f"adelay={int(LEAD * 1000)}:all=1,apad", "-t", f"{total:.3f}", "-vf", vf,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-tune", "stillimage", "-g", str(FPS * 2),
           "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2", str(out)]
    subprocess.run(cmd, check=True)
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", help="comma-separated scene ids")
    ap.add_argument("--frames-only", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, str(ROOT))
    from scenes import SCENES
    scenes = [s for s in SCENES if not a.scenes or str(s["id"]) in a.scenes.split(",")]
    done = render_frames(scenes, a.force)
    print(f"frames: {len(scenes)} scenes, rendered {len(done)} new")
    if a.frames_only:
        return
    jobs = []
    for sc in scenes:
        sc["mp3"] = []
        for text in sc["beats"]:
            p = TTS / f"{sha(VOICE, RATE, spoken(text))}.mp3"
            sc["mp3"].append(p)
            jobs.append((spoken(text), p))
    asyncio.run(tts_all(jobs))
    print("narration ready")

    SEG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)
    t, srt, chapters, segs, idx = 0.0, [], [], [], 1
    for sc in scenes:
        chapters.append((t, sc["title"]))
        for n, (text, mp3, png) in enumerate(zip(sc["beats"], sc["mp3"], sc["frames"]), 1):
            da = duration(mp3)
            seg = SEG / f"{sc['id']:02d}_{n}_{sha(png.name, mp3.name)}.mp4"
            if not seg.exists():
                build_segment(png, mp3, da, n == 1, seg)
            segs.append(seg)
            sents = [s for s in re.split(r"(?<=[.!?])\s+", text) if s]
            total_chars = sum(len(s) for s in sents)
            cur = t + LEAD
            for s in sents:
                d = da * len(s) / total_chars
                srt.append((cur, cur + d, s))
                cur += d
            t += LEAD + da + TAIL
    (OUT / f"{NAME}.srt").write_text("".join(
        f"{i}\n{srt_time(s)} --> {srt_time(e)}\n{x}\n\n" for i, (s, e, x) in enumerate(srt, 1)))
    (OUT / "chapters.txt").write_text("\n".join(
        f"{int(c // 60):02d}:{int(c % 60):02d} {name}" for c, name in chapters) + "\n")
    meta = [";FFMETADATA1"]
    for i, (c, name) in enumerate(chapters):
        end = chapters[i + 1][0] if i + 1 < len(chapters) else t
        meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(c * 1000)}", f"END={int(end * 1000)}", f"title={name}"]
    (BUILD / "chapters.ffmeta").write_text("\n".join(meta) + "\n")
    (BUILD / "list.txt").write_text("".join(f"file '{s}'\n" for s in segs))
    out = OUT / f"{NAME}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(BUILD / "list.txt"),
                    "-i", str(OUT / f"{NAME}.srt"), "-i", str(BUILD / "chapters.ffmeta"),
                    "-map", "0:v", "-map", "0:a", "-map", "1:0", "-map_metadata", "2", "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                    "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-movflags", "+faststart", str(out)], check=True)
    print(f"video: {out}  {int(t // 60)}m{int(t % 60):02d}s  {out.stat().st_size / 1e6:.0f} MB")


if __name__ == "__main__":
    main()
