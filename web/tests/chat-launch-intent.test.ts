import test from "node:test";
import assert from "node:assert/strict";

import {
  newMasteryPathChatUrl,
  newReaderChatUrl,
  readChatLaunchIntent,
} from "../lib/chat-launch-intent";

test("continuing a mastery path opens a fresh associated chat", () => {
  assert.equal(
    newMasteryPathChatUrl("calculus/path 1"),
    "/home?capability=mastery_path&mastery_path_id=calculus%2Fpath+1",
  );
});

test("the mastery continue URL round-trips into a launch intent", () => {
  const url = newMasteryPathChatUrl("calculus/path 1");
  const intent = readChatLaunchIntent(url.slice(url.indexOf("?")));
  assert.equal(intent.capability, "mastery_path");
  assert.equal(intent.masteryPathId, "calculus/path 1");
  assert.deepEqual(intent.tools, []);
  assert.deepEqual(intent.knowledgeBases, []);
});

test("an absent capability stays unspecified, an empty one means plain chat", () => {
  assert.equal(readChatLaunchIntent("?tool=web_search").capability, null);
  assert.equal(readChatLaunchIntent("?capability=").capability, "");
});

test("tools are collected verbatim for the caller to validate", () => {
  assert.deepEqual(
    readChatLaunchIntent("?tool=web_search&tool=+reason+").tools,
    ["web_search", "reason"],
  );
});

test("a blank mastery path id is dropped rather than bound", () => {
  assert.equal(
    readChatLaunchIntent("?mastery_path_id=%20%20").masteryPathId,
    null,
  );
  assert.deepEqual(readChatLaunchIntent(""), {
    capability: null,
    tools: [],
    knowledgeBases: [],
    masteryPathId: null,
    readerMaterialId: null,
  });
});

test("a reader launch opens the material and attaches its source knowledge base", () => {
  const url = newReaderChatUrl({
    materialId: "mat 1",
    knowledgeBase: "physics/kb",
  });
  assert.equal(
    url,
    "/home?capability=immersive_reading&reader_material_id=mat+1&kb=physics%2Fkb",
  );
  const intent = readChatLaunchIntent(url.slice(url.indexOf("?")));
  assert.equal(intent.capability, "immersive_reading");
  assert.equal(intent.readerMaterialId, "mat 1");
  assert.deepEqual(intent.knowledgeBases, ["physics/kb"]);
});
