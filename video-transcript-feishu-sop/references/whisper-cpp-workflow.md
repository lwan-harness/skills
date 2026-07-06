# Whisper.cpp Workflow

## Tool Checks

Run these first:

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$MEDIA"
which -a ffmpeg
which -a ffprobe
which whisper-cli
whisper-cli --help
```

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

Use the prompted output when it is better:

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

Scan for obvious task-specific residuals using `rg` or `perl`. Keep this scan specific enough that valid terms do not produce false alarms.
