import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const base = process.env.VITE_BASE_PATH || "/";
const minify = process.env.VITE_MINIFY === "false" ? false : "esbuild";

export default defineConfig({
  plugins: [react()],
  base,
  build: {
    minify,
    sourcemap: false,
  },
});
