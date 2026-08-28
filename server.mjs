import { createReadStream, existsSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join } from "node:path";

const root = new URL(".", import.meta.url).pathname;
const port = Number(process.env.PORT || 3000);
const routes = new Map([
  ["/", "index.html"],
  ["/index.html", "index.html"],
  ["/dashboard.html", "dashboard.html"],
  ["/summary.pdf", "summary.pdf"],
  ["/all_posts.csv", "all_posts.csv"],
]);
const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".pdf": "application/pdf",
  ".csv": "text/csv; charset=utf-8",
};

createServer((request, response) => {
  const pathname = new URL(request.url || "/", "http://localhost").pathname;
  const file = routes.get(pathname);
  if (!file) {
    response.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
    response.end("Not found\n");
    return;
  }
  const path = join(root, file);
  if (!existsSync(path)) {
    response.writeHead(503, { "content-type": "text/plain; charset=utf-8" });
    response.end("Dashboard has not been built yet.\n");
    return;
  }
  response.writeHead(200, {
    "content-type": contentTypes[extname(path)] || "application/octet-stream",
    "cache-control": file.endsWith(".html") ? "no-cache" : "public, max-age=3600",
    "x-content-type-options": "nosniff",
  });
  createReadStream(path).pipe(response);
}).listen(port, "0.0.0.0", () => {
  console.log(`HOTB social dashboard listening on port ${port}`);
});
