// Entry point for the news-image-20261120 competition.
//
// The front page is drawn by generate.py (Pillow) and shipped in this
// repository as entry.png. This program only copies that file to the
// output directory, so both grading runs produce byte-identical output
// with no network, no clock and no randomness involved.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = dirname(fileURLToPath(import.meta.url));
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outputDir, { recursive: true });
copyFileSync(join(repoRoot, "entry.png"), join(outputDir, "entry.png"));
