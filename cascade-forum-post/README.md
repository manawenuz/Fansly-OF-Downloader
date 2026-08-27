# Cascade Viewer — BitPorn Forum Post Kit

This folder contains a BitPorn-ready BBCode post for `Scripts, Programming and Coding`, modelled on `Thumbnail Maker v4` formatting.

**Contents:**
- `post_bbcode.txt` — paste directly into BitPorn (BBCode with [size]/[img]/[url]/[hr]/[list]/[code])
- `post_markdown.md` — same content in Markdown for GitHub/docs
- `screenshots/` — put your sanitized screenshots here (see below)

**How to use:**
1. Replace placeholder image URLs in `post_bbcode.txt` with your own uploads (e.g. imghost.dev, postimages.org). Keep `img=250` or `img=450` width as in template.
2. Update download URLs to your GitHub / GHCR links.
3. Paste `post_bbcode.txt` content as a new topic in `The Lab -> Scripts / Code` on BitPorn.

**Screenshots — do NOT use creator content:**
I did not fetch `of.tbs.manko.yoga/creator/cherrylovebombb` (explicit archive). Instead, create 6-8 sanitized screenshots yourself:
- `01_grid.jpg` — justified gallery grid (blur/crop any explicit thumbs)
- `02_lightbox.jpg` — lightbox open
- `03_search.jpg` — search / date navigation
- `04_mobile.jpg` — mobile view
- `05_api.jpg` — optional API response
- `06_docker.jpg` — `docker compose up` log

Save them as `screenshots/*.jpg|webp` and upload to your image host. Keep each under ~1MB.

**Forum title suggestion:**
`[TOOL] Cascade Viewer — Self-Hosted Justified Gallery + Lightbox + Docker`

**Tags:** `gallery`, `viewer`, `docker`, `ffmpeg`, `self-hosted`
