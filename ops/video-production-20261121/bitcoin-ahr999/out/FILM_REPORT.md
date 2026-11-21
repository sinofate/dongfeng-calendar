# 2026-11-21 比特币抄底指数成片

Native `python3 -m recovery_us3day produce` encoded this film. Exit 0 is not a viewing pass. The parent run still does the local re-run and videoReview.

## Clock

- Locked script stays v4. Cover and the three-piece stay v3. Body copy was not rewritten.
- VO file `vo_p1_s16le.wav` is 109.050604s at the supplied 1.1 speed. Timeline total is 109.051s. The obsolete 178s estimate was not used.
- Output container 109.051s. Video 3271 frames, 109.033s at 30fps. Audio 109.051s. The last syllable is on the audio; the picture ends one frame earlier because 109.051 × 30 is not an integer.

## Picture

- Canvas 1080×1920. Stage x0 y312 w1080 h1128, ending at y1440. Matte `#071829`.
- Title band, from cover v3, not the semiconductor title: L1 `是买点吗` 88 gold, L2 `见底还看有没有人接` 64 white. Tops 72 and 188. L/R 90.
- Subtitles: Noto Sans CJK SC, 76, fill `#FFD700`, outline black, secondary `&H000000FF`, Alignment 2, MarginV 370, L/R 90. Two empty `{\alpha&HFF&}` events removed. The 18-character line is split, characters unchanged, into `快到二零二零年三一二` (13.86–14.91) and `币灾时的位置了。` (14.91–15.96).
- No source corner badge.
- Data plates are fitted inside the stage, then pushed 3.5% through a matte margin, so the ETF table and the S21 spec are not cropped. Cover is a separate full-frame zoom from 1.00 to 1.03 over 1.5s, then a hard cut.
- S21 uses the ordinary Bitmain spec table plus the electricity line. No XP or Hyd photo.

## Components actually called

| Shot | Id | How it rendered |
| --- | --- | --- |
| s01-cover | cover-push-3 | zoompan 1.00→1.03, one input frame, full frame |
| s01, s03, s07 | number-pop-in | catalog variables, values 55,298 / 0.228 / 约 5.8 亿 |
| s02, s08 | kinetic-center-build | catalog variables, phrase builds in place; s08 wraps at `／` without changing characters |
| s04, s06, s09 | panel-reveal | catalog variables |
| s05 | price-decline-56000-44800 | attached cubic M165 280 C320 315 375 385 505 435 S685 625 875 780, gold stroke, guides, 56000 then 44800 at 72% |

`number-pop-in`, `kinetic-center-build`, and `panel-reveal` have catalog entries and no HTML snippet on this machine. The report marks them `catalog_variables_rendered`. The two new components have their HTML and registry and are marked `resolved`.

## Audio

Voice stays the supplied WAV. No second TTS pass. BGM segments are the five supplied excerpts at −18 dB, fades measured on the trimmed clip. SFX at the supplied peaks, −10 dB.

Loudness is one linear gain on the finished mix.

| | I | True peak | LRA | Duration |
| --- | --- | --- | --- | --- |
| Before | −16.23 LUFS | −2.91 dBTP | 2.4 | 109.051s |
| Gain | +0.23 dB | | | |
| After | −16.01 LUFS | −2.69 dBTP | 2.4 | 109.051s |

True peak stays under −1.5 dBTP. Video stream hash is unchanged by the loudness mux (`video_unchanged_from_pre_loudness_encode: true`).

## Font

`fontselect: (Noto Sans CJK SC, 700, 0) -> NotoSansCJKsc-Bold, 2, NotoSansCJKsc-Bold`

- Regular sha256 `b76b0433203017ca80401b2ee0dd69350349871c4b19d504c34dbdd80541690a`
- Bold sha256 `faa5f3656a78b2e2d450d27fe8382c778bc2b6bb5ea29c986664a6a435056ceb`

No substitute face was used.

## Re-run

From `ops/video-production-20261121/bitcoin-ahr999`, with the supplied VO wav, BGM, SFX, plates, and the Noto TTC files already used by the recovery package:

```sh
PYTHONPATH=../recovery python3 -m recovery_us3day produce \
  --project project.bitcoin-ahr999.json \
  --catalog ../recovery/inputs/asset_catalog.json \
  --out out/native
```

## What this is not

- Not a recovered HyperFrames master, and not a claim that the catalog HTML snippets were present.
- Not a clearance of the old 22-shot semiconductor film. `qualified` and `recovered_master` stay false.
- The price line is the component's pressure graphic, not a new market series.
