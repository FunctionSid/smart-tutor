import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";

import {
  GENERATION_COMPLETE_ANNOUNCEMENT,
  GENERATION_START_ANNOUNCEMENT,
  getGenerationAnnouncement,
  type GenerationAnnouncementSnapshot,
} from "../lib/chat-accessibility";

const webRoot = process.cwd();

function readWebFile(relativePath: string): string {
  return readFileSync(path.join(webRoot, relativePath), "utf8");
}

test("streaming assistant responses are normal article content, not a live region", () => {
  const source = readWebFile("components/common/AssistantResponse.tsx");

  assert.match(source, /<div role="article" className=\{className\}>/);
  assert.doesNotMatch(source, /aria-live=/);
  assert.doesNotMatch(source, /aria-atomic=/);
});

test("the elapsed duration is not contained in a timer live region", () => {
  const source = readWebFile("components/chat/home/TracePanels.tsx");

  assert.doesNotMatch(source, /aria-live=/);
  assert.doesNotMatch(source, /role="status"/);
  assert.match(source, /aria-hidden="true"[\s\S]*\{durationLabel\}/);
});

test("Qwen thinking remains visible without becoming a live announcement stream", () => {
  const responseSource = readWebFile("components/common/AssistantResponse.tsx");
  const thinkingSource = readWebFile("components/common/ModelThinkingCard.tsx");

  assert.match(responseSource, /<ModelThinkingCard/);
  assert.match(thinkingSource, /aria-live="off"/);
  assert.match(thinkingSource, /<MarkdownRenderer content=\{content\} variant="trace" \/>/);
});

test("generation start is announced once per streaming transition", () => {
  let previous: GenerationAnnouncementSnapshot | null = {
    sessionId: "s1",
    isStreaming: false,
  };

  let result = getGenerationAnnouncement(previous, {
    sessionId: "s1",
    isStreaming: true,
  });
  assert.equal(result.message, GENERATION_START_ANNOUNCEMENT);
  previous = result.snapshot;

  result = getGenerationAnnouncement(previous, {
    sessionId: "s1",
    isStreaming: true,
  });
  assert.equal(result.message, "");
});

test("generation completion is announced once per streaming transition", () => {
  let previous: GenerationAnnouncementSnapshot | null = {
    sessionId: "s1",
    isStreaming: true,
  };

  let result = getGenerationAnnouncement(previous, {
    sessionId: "s1",
    isStreaming: false,
  });
  assert.equal(result.message, GENERATION_COMPLETE_ANNOUNCEMENT);
  previous = result.snapshot;

  result = getGenerationAnnouncement(previous, {
    sessionId: "s1",
    isStreaming: false,
  });
  assert.equal(result.message, "");
});

test("streaming events do not create repeated announcement messages", () => {
  let previous: GenerationAnnouncementSnapshot | null = null;
  const states: GenerationAnnouncementSnapshot[] = [
    { sessionId: "s1", isStreaming: true },
    { sessionId: "s1", isStreaming: true },
    { sessionId: "s1", isStreaming: true },
    { sessionId: "s1", isStreaming: false },
  ];

  const messages = states.map((state) => {
    const result = getGenerationAnnouncement(previous, state);
    previous = result.snapshot;
    return result.message;
  });

  assert.deepEqual(messages, [
    GENERATION_START_ANNOUNCEMENT,
    "",
    "",
    GENERATION_COMPLETE_ANNOUNCEMENT,
  ]);
});

test("the final assistant answer remains accessible as normal document content", () => {
  const source = readWebFile("components/common/AssistantResponse.tsx");

  assert.match(source, /role="article"/);
  assert.doesNotMatch(source, /aria-hidden="true"/);
});

test("existing voice announcements remain discrete and separate from generation", () => {
  const composerSource = readWebFile("components/chat/home/ChatComposer.tsx");
  const recorderSource = readWebFile("hooks/useVoiceRecorder.ts");

  assert.match(composerSource, /voiceAnnouncement/);
  assert.match(
    composerSource,
    /<span className="sr-only" aria-live="polite" aria-atomic="true">/,
  );
  assert.match(recorderSource, /Recording started\./);
  assert.match(recorderSource, /Transcription complete\./);
});
