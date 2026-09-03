import assert from "node:assert/strict";
import test from "node:test";

import { invalidateLLMOptionsCache, listLLMOptions } from "../lib/llm-options";

test("a timed-out model catalog request can be retried", async () => {
  const originalFetch = globalThis.fetch;
  (globalThis as { window?: unknown }).window = {
    setTimeout,
    clearTimeout,
    location: { pathname: "/home", href: "" },
  };
  let calls = 0;
  globalThis.fetch = async (_input, init) => {
    calls += 1;
    if (calls === 1) {
      return new Promise<Response>((_resolve, reject) => {
        init?.signal?.addEventListener("abort", () => {
          reject(new DOMException("The operation was aborted", "AbortError"));
        });
      });
    }
    return new Response(JSON.stringify({ active: null, options: [] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };

  try {
    await assert.rejects(
      listLLMOptions({ force: true, timeoutMs: 5 }),
      (error: unknown) =>
        error instanceof DOMException && error.name === "AbortError",
    );
    const result = await listLLMOptions({ force: true, timeoutMs: 50 });
    assert.deepEqual(result, { active: null, options: [] });
    assert.equal(calls, 2);
  } finally {
    invalidateLLMOptionsCache();
    globalThis.fetch = originalFetch;
    delete (globalThis as { window?: unknown }).window;
  }
});

test("local model refresh asks the backend to discover local providers", async () => {
  const originalFetch = globalThis.fetch;
  (globalThis as { window?: unknown }).window = {
    setTimeout,
    clearTimeout,
    location: { pathname: "/home", href: "" },
  };
  let requested = "";
  globalThis.fetch = async (input) => {
    requested = String(input);
    return new Response(JSON.stringify({ active: null, options: [] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };

  try {
    await listLLMOptions({ force: true, refreshLocal: true });
    assert.match(requested, /refresh_local=true/);
  } finally {
    invalidateLLMOptionsCache();
    globalThis.fetch = originalFetch;
    delete (globalThis as { window?: unknown }).window;
  }
});
