---
name: video-transcript-feishu-sop
description: "End-to-end SOP for turning local videos, audio, or existing subtitle files into knowledge artifacts: prefer provided/platform SRT/VTT subtitles when available, otherwise extract audio with ffmpeg and transcribe with whisper.cpp/whisper-cli into SRT and text, clean transcript terminology, save a local SRT copy, create Feishu/Lark summary parent documents with SVG whiteboard illustrations, and place SRT/transcript documents as child pages with lark-cli. Use when the user asks for video transcription, subtitle/SRT/VTT processing, whisper.cpp processing, local SRT backup, Feishu document upload, Feishu wiki/doc summarization, SVG illustration in Feishu docs, Feishu document hierarchy cleanup, or turning meetings/videos into knowledge-base articles."
---

# Video Transcript Feishu SOP

Use this skill to reproduce the full workflow: local media or subtitles -> SRT/TXT transcript -> cleaned transcript -> local SRT copy -> Feishu summary parent document with SVG whiteboard -> Feishu SRT child document.

## Workflow

1. **Ground inputs**
   - Determine the transcript source first: provided subtitle file, platform subtitles/captions, or media audio.
   - If the user supplied `.srt`, `.vtt`, `.ass`, `.ssa`, or another subtitle file, use it directly as the transcript source. Do not download video or run whisper.cpp unless the user explicitly asks for re-transcription or the subtitle is unusable.
   - For URL sources, inspect metadata for official subtitles/captions before downloading media. If a usable subtitle track exists, download that subtitle and skip media download, WAV extraction, and whisper.cpp.
   - If no usable subtitle exists, confirm the source media path exists or download media, then inspect duration with `ffprobe`.
   - Confirm required tools for the selected path: `lark-cli` always; subtitle conversion tools only when needed; `ffmpeg`, `ffprobe`, and `whisper-cli` only for audio transcription.
   - Choose an output directory under the current workspace, named by a safe media slug.

2. **Obtain transcript**
   - Read `references/whisper-cpp-workflow.md`.
   - Prefer existing or platform subtitle tracks when available. Normalize them to `transcript.srt` and `transcript.txt`; record the subtitle source in notes used later for Feishu.
   - Only when no usable subtitle exists, extract WAV as 16 kHz mono PCM.
   - Find a multilingual whisper.cpp model when language is uncertain; avoid `.en` models for non-English media.
   - Generate raw `.srt` and `.txt` with whisper.cpp.
   - If domain terms matter, rerun with `--prompt` and `--carry-initial-prompt`, then clean deterministically.
   - Use `scripts/clean_transcript.py` for glossary-based cleanup.
   - Save a second copy of the final `transcript_cleaned.srt` to a local user-facing folder, defaulting to `~/Downloads/<safe_slug>_transcript_cleaned.srt` unless the user specifies another path.

3. **Create a summarized parent doc in Feishu**
   - Read `references/feishu-doc-workflow.md`.
   - Read `lark-cli skills read lark-doc` and its required references before using `docs +create`, `docs +fetch`, or `docs +update`.
   - Write an article in the user's target language, not just an outline.
   - Create a self-contained SVG that explains the transcript's main idea. Keep it simple and readable; do not use image/video generation.
   - Convert the article and SVG to Feishu XML with `scripts/article_to_feishu_xml.py`.
   - Create the summary document under the supplied wiki/doc parent; otherwise default to `my_library`.
   - Fetch-validate that the document contains a `<whiteboard>` block and representative body text.

4. **Create the SRT child doc in Feishu**
   - Convert SRT to Feishu XML with `scripts/srt_to_feishu_xml.py`.
   - Resolve the summary document's wiki node with `wiki +node-get`.
   - Create the SRT document as a child wiki node of the summary document.
   - Fetch-validate key terms and the final SRT timestamp.

## Output Naming

Use consistent names so later steps can discover artifacts:

- `audio.wav`
- `source_subtitles.srt` or `source_subtitles.vtt` when subtitles are the transcript source
- `transcript.srt` / `transcript.txt`
- `transcript_prompted.srt` / `transcript_prompted.txt`
- `transcript_cleaned.srt` / `transcript_cleaned.txt`
- local SRT copy: `~/Downloads/<safe_slug>_transcript_cleaned.srt` by default
- `feishu_srt_doc.xml`
- `article.xml` or `summary_article.xml`

## Scripts

- `scripts/clean_transcript.py INPUT OUTPUT [--glossary glossary.json]`
  - Applies ordered regex replacements to `.srt` or `.txt`.
  - Includes a small Claude Code glossary by default; pass a glossary to override or extend.
- `scripts/srt_to_feishu_xml.py --srt transcript_cleaned.srt --title "..." --output feishu_srt_doc.xml`
  - Wraps SRT in Feishu Doc XML using a `text` code block.
- `scripts/article_to_feishu_xml.py --article article.txt --svg diagram.svg --title "..." --output article.xml`
  - Wraps a text/Markdown-like article plus raw SVG into Feishu Doc XML.

## Feishu Safety Rules

- Use `--as user` by default.
- Treat `lark-cli` network/API calls as remote side effects; request elevated permission when sandboxed.
- Do not create live Feishu docs during skill validation or tests.
- If a source document is a `docx` URL, call `wiki +node-get` to resolve its wiki node before creating a child document.
- If the source has no parent target, create the summary parent doc with `docs +create --parent-position my_library`.
- The default hierarchy is summary/article parent -> SRT child. If existing docs were created with SRT parent -> summary child, use `wiki +move` to move the summary to the target parent/root first, then move the SRT under the summary.

## Completion Checklist

- WAV duration is close to source audio duration, or AAC/bad-frame limitations are explicitly reported.
- If subtitles were available, video download and whisper.cpp were intentionally skipped and the subtitle source is reported.
- SRT and TXT exist and have plausible beginning and ending content.
- Cleaned transcript has no obvious domain-term residuals from the task glossary.
- A local copy of the final cleaned SRT exists in the requested local folder, defaulting to `~/Downloads`.
- Feishu summary document link is returned, fetch-validated, and contains a whiteboard block.
- Feishu SRT document link is returned, fetch-validated, and its parent node matches the summary document node.
