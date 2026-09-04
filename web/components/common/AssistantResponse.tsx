"use client";

import { Fragment, memo, useMemo } from "react";

import MarkdownRenderer from "@/components/common/MarkdownRenderer";
import ModelThinkingCard from "@/components/common/ModelThinkingCard";
import { useReading } from "@/context/ReadingContext";
import {
  hasVisibleMarkdownContent,
  repairMalformedStrongEmphasis,
  stripArtifactAnnotations,
} from "@/lib/markdown-display";
import { linkifyLocatorCitations } from "@/lib/reading-citations";
import { parseModelThinkingSegments } from "@/lib/think-segments";
import { useSmoothStreamText } from "@/hooks/useSmoothStreamText";

interface AssistantResponseProps {
  content: string;
  className?: string;
  /**
   * When true, the renderer drives the visible text through a rAF
   * typewriter (``useSmoothStreamText``) so the markdown grows at a
   * steady, frame-aligned pace even when the upstream LLM emits
   * uneven chunks. Pass ``false`` for completed turns and any non-
   * streaming surface — the hook short-circuits to a pass-through
   * in that case.
   */
  isStreaming?: boolean;
}

function AssistantResponseImpl({
  content,
  className = "text-[16px] leading-[1.75]",
  isStreaming = false,
}: AssistantResponseProps) {
  const displayContent = useSmoothStreamText(content, isStreaming);
  // Immersive reading only: turn `[p.12]` citations into anchors the reader
  // pane intercepts. Outside that mode `material` is null (there is no
  // provider on most surfaces, and none when no document is open), so this is a
  // no-op and every other chat surface renders byte-identically to before.
  const { material } = useReading();
  const citedContent = useMemo(
    () =>
      material
        ? linkifyLocatorCitations(displayContent, {
            maxLocator: material.unit_count,
          })
        : displayContent,
    [displayContent, material],
  );
  const segments = useMemo(
    () => parseModelThinkingSegments(stripArtifactAnnotations(citedContent)),
    [citedContent],
  );

  // Decide whether the message has anything worth rendering. We consider both
  // ordinary markdown segments and model-thinking blocks: a turn that only
  // ever produced a <think> scratchpad should still render the collapsed card
  // instead of dropping the assistant bubble entirely.
  const hasRenderableSegment = useMemo(() => {
    return segments.some((segment) => {
      if (segment.kind === "think") return segment.content.trim().length > 0;
      return hasVisibleMarkdownContent(segment.content);
    });
  }, [segments]);

  if (!hasRenderableSegment) return null;

  // Keep the assistant turn as normal navigable document content. Streaming
  // updates happen here visually, while coarse screen-reader announcements
  // live in ChatMessages so token/chunk updates do not become speech.
  return (
    <div role="article" className={className}>
      {segments.map((segment, index) => {
        if (segment.kind === "think") {
          return (
            <ModelThinkingCard
              key={`think-${index}`}
              content={segment.content}
              closed={segment.closed}
            />
          );
        }
        const repairedContent = repairMalformedStrongEmphasis(segment.content);

        if (!hasVisibleMarkdownContent(repairedContent)) {
          return <Fragment key={`text-${index}`} />;
        }

        return (
          <MarkdownRenderer
            key={`text-${index}`}
            content={repairedContent}
            variant="prose"
            className="text-[var(--foreground)]"
          />
        );
      })}
    </div>
  );
}

// Memoize so completed messages don't re-parse markdown when an
// unrelated streaming sibling updates the parent — the streaming
// message gets a fresh ``msg.content`` per delta and re-renders
// naturally, but every other bubble keeps its previous render output.
const AssistantResponse = memo(AssistantResponseImpl);
AssistantResponse.displayName = "AssistantResponse";
export default AssistantResponse;
