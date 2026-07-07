# Whisper.cpp Workflow

## Transcript Source Decision

Before downloading media or running whisper.cpp, choose the cheapest reliable transcript source:

1. **User-provided subtitle file**: If the input includes `.srt`, `.vtt`, `.ass`, `.ssa`, or another subtitle file, use it directly. Normalize it to `transcript.srt` and generate `transcript.txt`. Do not download video or run whisper.cpp unless the user explicitly asks for audio re-transcription or the subtitle file is clearly unusable.
2. **Platform subtitles/captions**: For YouTube, Bilibili, Feishu, or similar URL sources, inspect metadata for official subtitles or usable automatic captions before downloading media. Prefer official subtitles over auto captions; prefer the source language unless the user requests translation. If a usable subtitle track exists, download it and skip media download, WAV extraction, model search, and whisper.cpp.
3. **Audio transcription**: Only download media, extract WAV, and run whisper.cpp when no usable subtitle source exists, when subtitles are materially incomplete/low quality, or when the user explicitly asks for whisper.cpp transcription.

When using subtitles as the transcript source, report that choice in the final answer and in the Feishu SRT note.

## Tool Checks

For audio transcription, run these first:

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$MEDIA"
which -a ffmpeg
which -a ffprobe
which whisper-cli
whisper-cli --help
```

For subtitle-first URL handling, `yt-dlp` may be enough:

```bash
yt-dlp -J --no-playlist "$URL"
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "$LANG" --sub-format srt -o "$OUT/source_subtitles.%(ext)s" "$URL"
```

Use browser cookies only when the site requires authentication or bot verification and the user has authorized it.

Find models with targeted searches before broad searches:

```bash
find /usr/local /opt/local "$HOME/Downloads" "$HOME/Documents" "$HOME/.cache" \
  -type f \( -name 'ggml-*.bin' -o -name '*.gguf' \) -print
```

Prefer multilingual models for unknown or non-English media:

1. `ggml-large-v3*.bin`
2. `ggml-large*.bin`
3. `ggml-medium*.bin`
4. `ggml-small*.bin`
5. `ggml-base.bin`

Avoid `*.en.bin` unless the audio is definitely English.

## Audio Extraction

Skip this section when `transcript.srt` came from a provided or platform subtitle file.

Use WAV for whisper.cpp:

```bash
ffmpeg -y -i "$MEDIA" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$OUT/audio.wav"
```

If `ffmpeg` reports AAC decode errors but still creates a file:

- Check WAV duration with `ffprobe`.
- Compare against source audio stream duration.
- Try another installed `ffmpeg` if available, such as `/usr/local/bin/ffmpeg`.
- If the WAV is shorter than source duration, cut the suspected tail segment and run whisper on it separately to see whether useful speech exists.
- Report the limitation if the source stream has bad frames.

## Transcription

Skip this section when `transcript.srt` came from a provided or platform subtitle file.

Raw pass:

```bash
whisper-cli -m "$MODEL" -f "$OUT/audio.wav" -l auto -t 8 \
  -osrt -otxt -of "$OUT/transcript"
```

Prompted pass when important terms are known:

```bash
whisper-cli -m "$MODEL" -f "$OUT/audio.wav" -l en -t 8 \
  --prompt "$PROMPT" --carry-initial-prompt \
  -osrt -otxt -of "$OUT/transcript_prompted"
```

Use `-l auto` for unknown language. Use a fixed language if auto-detection is correct and repeated runs should be stable.

## Cleaning

If using subtitle input, copy or convert it to `transcript.srt`, generate `transcript.txt`, then clean into `transcript_cleaned.srt` and `transcript_cleaned.txt`.

Use the prompted whisper output when it is better:

```bash
python3 scripts/clean_transcript.py "$OUT/transcript_prompted.srt" "$OUT/transcript_cleaned.srt"
python3 scripts/clean_transcript.py "$OUT/transcript_prompted.txt" "$OUT/transcript_cleaned.txt"
```

For task-specific terms, create a JSON glossary:

```json
[
  {"pattern": "\\bQuad Code\\b", "replacement": "Claude Code"},
  {"pattern": "\\bClaud\\b", "replacement": "Claude"}
]
```

Then pass `--glossary glossary.json`.

## Verification

Check:

```bash
ls -lh "$OUT"
sed -n '1,80p' "$OUT/transcript_cleaned.srt"
tail -n 40 "$OUT/transcript_cleaned.srt"
```

For subtitle-source runs, additionally check the first and last subtitle timestamps against the source metadata duration when available, and note if the subtitle track ends early.

Scan for obvious task-specific residuals using `rg` or `perl`. Keep this scan specific enough that valid terms do not produce false alarms.
