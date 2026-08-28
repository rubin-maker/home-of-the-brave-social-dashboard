"""Serve the generated HOTB dashboard on Railway without extra dependencies."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
ROUTES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/dashboard.html": "dashboard.html",
    "/summary.pdf": "summary.pdf",
    "/all_posts.csv": "all_posts.csv",
}


class DashboardHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        pathname = urlsplit(path).path
        filename = ROUTES.get(pathname)
        if filename is None:
            return str(ROOT / "__not_found__")
        return str(ROOT / filename)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        if self.path in ("/", "/index.html", "/dashboard.html"):
            self.send_header("Cache-Control", "no-cache")
        else:
            self.send_header("Cache-Control", "public, max-age=3600")
        super().end_headers()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), DashboardHandler)
    print(f"HOTB social dashboard listening on port {port}", flush=True)
    server.serve_forever()
