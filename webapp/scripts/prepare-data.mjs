import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const source = path.resolve(__dirname, "../../presentation/data/presentation_data.json");
const targetDir = path.resolve(__dirname, "../public/data");
const target = path.resolve(targetDir, "presentation_data.json");

if (!existsSync(source)) {
  throw new Error(
    `Missing source payload at ${source}. Run: python3 scripts/build_presentation_data.py`
  );
}

mkdirSync(targetDir, { recursive: true });
copyFileSync(source, target);
console.log(`Copied payload to ${target}`);
