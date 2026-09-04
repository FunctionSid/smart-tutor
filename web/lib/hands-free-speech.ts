import { parseModelThinkingSegments } from "./think-segments";

const SENTENCE_BOUNDARY = /([.!?])(\s+|$)/;
const CLAUSE_BOUNDARY = /([,;:])(\s+|$)/;

export function textForSpeech(markdown: string): string {
  const withoutThinking = parseModelThinkingSegments(markdown)
    .filter((segment) => segment.kind === "text")
    .map((segment) => segment.content)
    .join(" ");
  return withoutThinking
    .replace(/```[\s\S]*?```/g, " code block omitted. ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/!\[[^\]]*]\([^)]+\)/g, "")
    .replace(/\[([^\]]+)]\([^)]+\)/g, "$1")
    .replace(/\[[A-Za-z]?\s*(?:p\.|page)?\s*\d+(?:[-,]\s*\d+)*]/gi, "")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/[*_~>#-]+/g, " ")
    .replace(/https?:\/\/\S+/g, " link ")
    .replace(/\s+/g, " ")
    .trim();
}

export function takeSpeechChunk(
  text: string,
  forcePartial = false,
  minChars = 24,
  maxChars = 220,
): { chunk: string; remaining: string } | null {
  const trimmed = text.trimStart();
  if (!trimmed) return null;
  const sentence = SENTENCE_BOUNDARY.exec(trimmed);
  if (sentence && sentence.index + sentence[0].length >= minChars) {
    const end = sentence.index + sentence[1].length;
    return { chunk: trimmed.slice(0, end).trim(), remaining: trimmed.slice(end).trimStart() };
  }
  if (!forcePartial && trimmed.length < maxChars) return null;
  const window = trimmed.slice(0, Math.min(trimmed.length, maxChars));
  const clause = CLAUSE_BOUNDARY.exec(window);
  if (clause && clause.index + clause[0].length >= minChars) {
    const end = clause.index + clause[1].length;
    return { chunk: trimmed.slice(0, end).trim(), remaining: trimmed.slice(end).trimStart() };
  }
  if (window.length < minChars) return null;
  const breakAt = Math.max(window.lastIndexOf(" "), minChars);
  return {
    chunk: trimmed.slice(0, breakAt).trim(),
    remaining: trimmed.slice(breakAt).trimStart(),
  };
}

export function shouldBargeIn(
  speechMs: number,
  wakeDetected = false,
  minimumSpeechMs = 450,
): boolean {
  return wakeDetected || speechMs >= minimumSpeechMs;
}
