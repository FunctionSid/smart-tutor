import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";

const source = readFileSync(
  path.join(process.cwd(), "components/chat/home/KnowledgeSelector.tsx"),
  "utf8",
);

test("knowledge selector opens into the option list for keyboard users", () => {
  assert.match(source, /aria-haspopup="listbox"/);
  assert.match(source, /role="listbox"/);
  assert.match(source, /role="option"/);
  assert.match(source, /itemRefs\.current\[focusIndex\]\?\.focus\(\)/);
});

test("knowledge selector keeps focus stable after selecting an option", () => {
  assert.match(source, /const wasOpen = wasOpenRef\.current;/);
  assert.match(
    source,
    /if \(!open \|\| wasOpen \|\| knowledgeBases\.length === 0\) return;/,
  );
  assert.match(source, /onClick=\{\(\) => onToggle\(kb\.name\)\}/);
});

test("knowledge selector returns focus to the trigger on Escape", () => {
  assert.match(source, /const triggerRef = useRef<HTMLButtonElement>\(null\);/);
  assert.match(source, /ref=\{triggerRef\}/);
  assert.match(
    source,
    /event\.key === "Escape"[\s\S]*setOpen\(false\);[\s\S]*triggerRef\.current\?\.focus\(\)/,
  );
});
