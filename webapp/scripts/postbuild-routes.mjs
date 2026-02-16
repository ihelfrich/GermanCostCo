import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.resolve(__dirname, "../dist");
const indexPath = path.resolve(distDir, "index.html");

if (!existsSync(indexPath)) {
  throw new Error(`Missing ${indexPath}. Run build first.`);
}

for (const route of ["regulatory", "map"]) {
  const dir = path.resolve(distDir, route);
  mkdirSync(dir, { recursive: true });
  copyFileSync(indexPath, path.resolve(dir, "index.html"));
}

console.log("Created static route entry points: /regulatory and /map");
