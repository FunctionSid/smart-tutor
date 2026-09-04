import assert from "node:assert/strict";
import test from "node:test";

import {
  handsFreeAnnouncement,
  reduceHandsFreeState,
  type HandsFreeState,
} from "../lib/hands-free-state";
import {
  shouldBargeIn,
  takeSpeechChunk,
  textForSpeech,
} from "../lib/hands-free-speech";
import {
  DEFAULT_HANDS_FREE_SETTINGS,
  readHandsFreeSettings,
} from "../lib/hands-free-settings";

test("Hands-Free defaults to Hey Jarvis and starts disabled", () => {
  assert.equal(DEFAULT_HANDS_FREE_SETTINGS.enabled, false);
  assert.equal(DEFAULT_HANDS_FREE_SETTINGS.wakeWord, "Hey Jarvis");
});

test("state machine follows the happy path back to wake waiting", () => {
  let state: HandsFreeState = "OFF";
  state = reduceHandsFreeState(state, { type: "ENABLE", focused: true });
  state = reduceHandsFreeState(state, { type: "WAKE_DETECTED" });
  state = reduceHandsFreeState(state, { type: "CAPTURE_STARTED" });
  state = reduceHandsFreeState(state, { type: "CAPTURE_COMPLETE" });
  state = reduceHandsFreeState(state, { type: "TRANSCRIPT_READY", text: "Explain RAG" });
  state = reduceHandsFreeState(state, { type: "FIRST_SPEECH" });
  state = reduceHandsFreeState(state, { type: "SPEECH_DONE" });

  assert.equal(state, "WAKE_WAITING");
});

test("state machine pauses on focus loss and resumes wake waiting on focus gain", () => {
  let state: HandsFreeState = "WAKE_WAITING";
  state = reduceHandsFreeState(state, { type: "FOCUS_LOST" });
  assert.equal(state, "RECOVERY");
  state = reduceHandsFreeState(state, { type: "FOCUS_GAINED" });
  assert.equal(state, "WAKE_WAITING");
});

test("barge-in immediately accepts Hey Jarvis but rejects short ordinary noise", () => {
  assert.equal(shouldBargeIn(0, true, 450), true);
  assert.equal(shouldBargeIn(200, false, 450), false);
  assert.equal(shouldBargeIn(500, false, 450), true);
});

test("speech text strips Qwen thinking and Markdown before TTS", () => {
  assert.equal(
    textForSpeech("<think>private reasoning</think>## Answer\nGraph **RAG** uses [sources](https://example.com)."),
    "Answer Graph RAG uses sources.",
  );
});

test("adaptive chunking prefers full sentences over token chunks", () => {
  const result = takeSpeechChunk("This is a complete sentence. This remains.");
  assert.deepEqual(result, {
    chunk: "This is a complete sentence.",
    remaining: "This remains.",
  });
  assert.equal(takeSpeechChunk("tiny words")?.chunk, undefined);
});

test("adaptive chunking can emit a sensible partial chunk after a pause", () => {
  const result = takeSpeechChunk(
    "This clause is long enough, and the model has paused without a final period",
    true,
  );
  assert.equal(result?.chunk, "This clause is long enough,");
});

test("Hands-Free announcements are coarse state messages", () => {
  assert.equal(handsFreeAnnouncement("WAKE_WAITING"), "Listening for Hey Jarvis.");
  assert.equal(handsFreeAnnouncement("CAPTURING"), "Listening.");
  assert.equal(handsFreeAnnouncement("SPEAKING"), "Speaking.");
});

test("stored settings cannot replace the locked wake word", () => {
  (globalThis as { window?: unknown }).window = {
    localStorage: {
      getItem: () => JSON.stringify({ wakeWord: "Alexa", enabled: true }),
    },
  };
  try {
    assert.equal(readHandsFreeSettings().wakeWord, "Hey Jarvis");
  } finally {
    delete (globalThis as { window?: unknown }).window;
  }
});
