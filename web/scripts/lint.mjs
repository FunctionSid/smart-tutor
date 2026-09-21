#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HEAP_CEILING_MB = 4096;
const WEB_DIR = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const ESLINT_BIN = path.join(WEB_DIR, "node_modules", "eslint", "bin", "eslint.js");

function memoryBudgetMB() {
  let bytes = os.totalmem();
  try {
    const limit = Number(readFileSync("/sys/fs/cgroup/memory.max", "utf8").trim());
    if (Number.isFinite(limit) && limit > 0) bytes = Math.min(bytes, limit);
  } catch {
    // No cgroup v2 limit on Windows/macOS or unconstrained containers.
  }
  return Math.floor(bytes / 1024 / 1024);
}

const inherited = process.env.NODE_OPTIONS ?? "";
const nodeOptions = /--max[-_]old[-_]space[-_]size/.test(inherited)
  ? inherited
  : `${inherited} --max-old-space-size=${Math.min(
      HEAP_CEILING_MB,
      Math.floor(memoryBudgetMB() * 0.5),
    )}`.trim();

const result = spawnSync(process.execPath, [ESLINT_BIN, ".", ...process.argv.slice(2)], {
  cwd: WEB_DIR,
  stdio: "inherit",
  env: { ...process.env, NODE_OPTIONS: nodeOptions },
});

if (result.error) {
  console.error(result.error);
  process.exit(1);
}
process.exit(result.status ?? 1);
