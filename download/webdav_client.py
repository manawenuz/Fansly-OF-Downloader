"""WebDAV client for streaming downloads directly to a WebDAV server."""

import os
from pathlib import Path
from urllib.parse import quote

try:
    import httpx
except ImportError:
    httpx = None


def _load_env():
    candidates = [
        Path(__file__).parent.parent / ".env",
        Path.cwd() / ".env",
    ]
    for p in candidates:
        if p.exists():
            for line in p.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())
            break


_load_env()


class WebDAVClient:
    def __init__(self, url: str, username: str, password: str):
        if not url.startswith("http"):
            url = "https://" + url
        self.base = url.rstrip("/")
        self.client = httpx.Client(auth=(username, password), timeout=600)

    def _url(self, rel: str, trailing_slash: bool = False) -> str:
        parts = [quote(p, safe="") for p in Path(rel).parts]
        url = self.base + "/" + "/".join(parts)
        if trailing_slash and not url.endswith("/"):
            url += "/"
        return url

    def exists(self, rel: str) -> bool:
        try:
            r = self.client.request("HEAD", self._url(rel), follow_redirects=True)
            return r.status_code != 404
        except Exception:
            return False

    def mkcol(self, rel: str):
        r = self.client.request("MKCOL", self._url(rel, trailing_slash=True))
        if r.status_code not in (200, 201, 204, 405, 409):
            r.raise_for_status()

    def ensure_dirs(self, rel: str, known: set):
        for parent in reversed(list(Path(rel).parents)):
            key = str(parent)
            if key in (".", "/", "") or key in known:
                continue
            self.mkcol(key)
            known.add(key)

    def put(self, rel: str, local_path: Path):
        with open(local_path, "rb") as f:
            data = f.read()
        r = self.client.put(self._url(rel), content=data,
                            headers={"Content-Type": "application/octet-stream"},
                            follow_redirects=True)
        r.raise_for_status()


_client: "WebDAVClient | None" = None
_known_dirs: set = set()


def get_client() -> "WebDAVClient | None":
    global _client
    if _client is not None:
        return _client
    if httpx is None:
        return None
    url = os.environ.get("WEBDAV_URL", "")
    username = os.environ.get("WEBDAV_USERNAME", "")
    password = os.environ.get("WEBDAV_PASSWORD", "")
    if url and username and password:
        _client = WebDAVClient(url, username, password)
    return _client
