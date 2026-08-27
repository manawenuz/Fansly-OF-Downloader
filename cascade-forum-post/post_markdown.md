# Cascade Viewer

![Hero](https://via.placeholder.com/900x450.png?text=Cascade+Viewer+Hero)

**⬇ Download:** https://github.com/manawenuz/cascade-viewer

---

Cascade Viewer is a lightweight, self-hosted gallery for local creator archives. Justified grid, full-screen lightbox, search and date navigation — all in a single Docker image.

No cloud. No tracking. No editing knowledge required. Point it at your archive folder and browse.

---

## 🖼️ Justified Gallery

- Flickr-style justified rows — no cropping, consistent gaps
- Lazy-loaded thumbnails for fast scrolling
- Responsive — desktop, tablet and mobile
- Dark theme

![grid](screenshots/01_grid.jpg) ![grid2](screenshots/02_grid2.jpg)

## 🔍 Lightbox + Search

- Full-screen lightbox with keyboard and swipe navigation
- Full-text search inside archive metadata
- Date navigation and timeline view
- Direct serving from Timeline / Messages / Stories

![lightbox](screenshots/05_lightbox.jpg)

## Features

- ✔ Justified layout with sharp previews
- ✔ Lightbox with on-demand video thumbnails (ffmpeg)
- ✔ Search + date navigation
- ✔ Read-only — never writes to source archive
- ✔ Thumb cache in separate volume, concurrency=2
- ✔ Two JSON APIs: `/api/creators` and `/api/metadata/:creator`
- ✔ Single container: `node:22-alpine` + `ffmpeg`

## Run Modes

- **DOCKER** – Recommended
- **NATIVE** – Node 22 + `npm ci`
- **SIDECAR** – Pair with sync container for auto-updates

## Folder Structure

```
/data/
  alice-of/
    metadata.json
    Timeline/
    Messages/
    Stories/
```

## Docker Quick Start

```yaml
services:
  viewer:
    image: ghcr.io/manawenuz/cascade-viewer:latest
    ports: ["3102:3102"]
    environment:
      OF_BASE: /data
      OF_THUMBS: /thumbs
    volumes:
      - /mnt/pool1/archives:/data:ro
      - /mnt/pool1/thumbs:/thumbs
```

## Source + Image

- GitHub: https://github.com/manawenuz/cascade-viewer
- GHCR: `ghcr.io/manawenuz/cascade-viewer:latest`
