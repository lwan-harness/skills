# Feishu Document Workflow

## Required lark-cli Skill Reads

Before using docs operations, follow the CLI's embedded guidance:

```bash
lark-cli skills read lark-doc
lark-cli skills read lark-shared/SKILL.md
lark-cli skills read lark-doc/references/lark-doc-xml.md
lark-cli skills read lark-doc/references/style/lark-doc-create-workflow.md
lark-cli skills read lark-doc/references/lark-doc-create.md
```

Before fetching for validation:

```bash
lark-cli skills read lark-doc/references/lark-doc-fetch.md
```

Use `--as user` unless the user explicitly requests bot-owned docs.

## Save a Local SRT Copy

After `transcript_cleaned.srt` is final, save a user-facing copy before publishing to Feishu:

```bash
LOCAL_SRT="$HOME/Downloads/${SAFE_SLUG}_transcript_cleaned.srt"
cp "$OUT/transcript_cleaned.srt" "$LOCAL_SRT"
```

If the Codex sandbox cannot write to `~/Downloads`, request elevated permission. If the user provides a different local target, use that path instead. Report the exact copied path in the final response.

## Create the Summary Parent Document

Prepare an article in a local text file and an SVG file. The SVG must be self-contained and simple. Convert:

```bash
python3 scripts/article_to_feishu_xml.py \
  --article "$OUT/article.txt" \
  --svg "$OUT/summary.svg" \
  --title "$ARTICLE_TITLE" \
  --output "$OUT/article.xml"
```

Create the summary in personal library:

```bash
lark-cli docs +create --api-version v2 --as user \
  --parent-position my_library \
  --content @"$OUT/article.xml"
```

Create the summary under a known wiki/doc parent:

```bash
lark-cli wiki +node-get --as user --node-token "$PARENT_URL_OR_TOKEN"
lark-cli docs +create --api-version v2 --as user \
  --parent-token "$PARENT_NODE_TOKEN" \
  --content @"$OUT/article.xml"
```

If given a `docx` URL, `wiki +node-get` can usually resolve the backing wiki node.

Validate summary content:

```bash
lark-cli docs +fetch --api-version v2 --as user --doc "$ARTICLE_DOC_URL" \
  --detail with-ids --doc-format xml --jq '.data.document.content'
```

Confirm the fetched XML includes `<whiteboard ...>` and representative article text.

## Create the SRT Child Document

Convert SRT to XML:

```bash
python3 scripts/srt_to_feishu_xml.py \
  --srt "$OUT/transcript_cleaned.srt" \
  --title "$TITLE" \
  --source-name "$MEDIA_BASENAME" \
  --note "Generated with whisper.cpp; cleaned deterministic domain terms." \
  --output "$OUT/feishu_srt_doc.xml"
```

If `transcript_cleaned.srt` came from provided or platform subtitles, set `--note` to say that subtitles were used directly and that media download/whisper.cpp was skipped. If media download failed and subtitles were used as fallback, state both facts.

Resolve the summary document's wiki node:

```bash
lark-cli wiki +node-get --as user --node-token "$ARTICLE_DOC_URL"
```

Create the SRT under the summary:

```bash
lark-cli docs +create --api-version v2 --as user \
  --parent-token "$ARTICLE_DOC_NODE_TOKEN" \
  --content @"$OUT/feishu_srt_doc.xml"
```

Validate SRT content and parentage:

```bash
lark-cli docs +fetch --api-version v2 --as user --doc "$DOC_URL" \
  --scope keyword --keyword "$KEY_TERM|$LAST_TIMESTAMP" --doc-format markdown
lark-cli wiki +node-get --as user --node-token "$SRT_DOC_URL"
```

Confirm the SRT node's `parent_node_token` matches the summary node token.

## Fix Existing Inverted Hierarchies

If a previous run created `SRT parent -> summary child`, flip it to `summary parent -> SRT child`:

```bash
lark-cli wiki +node-get --as user --node-token "$SRT_DOC_URL"
lark-cli wiki +node-list --as user --space-id "$SPACE_ID" --parent-node-token "$SRT_NODE_TOKEN"
lark-cli wiki +move --as user \
  --node-token "$SUMMARY_NODE_TOKEN" \
  --source-space-id "$SPACE_ID" \
  --target-space-id "$SPACE_ID" \
  --target-parent-token "$SRT_PARENT_NODE_TOKEN"
lark-cli wiki +move --as user \
  --node-token "$SRT_NODE_TOKEN" \
  --source-space-id "$SPACE_ID" \
  --target-space-id "$SPACE_ID" \
  --target-parent-token "$SUMMARY_NODE_TOKEN"
```

Validate by listing the summary's children:

```bash
lark-cli wiki +node-list --as user --space-id "$SPACE_ID" --parent-node-token "$SUMMARY_NODE_TOKEN"
```

## Network and Permissions

`lark-cli` calls reach Feishu APIs and should be treated as networked side effects. In sandboxed Codex, request elevated permissions for create/fetch/inspect calls. Do not use live API calls during skill self-tests unless the user explicitly asks to execute the SOP.
