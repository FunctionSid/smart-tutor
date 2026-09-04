export const GENERATION_START_ANNOUNCEMENT =
  "Smart Tutor is generating a response.";
export const GENERATION_COMPLETE_ANNOUNCEMENT = "Response complete.";

export interface GenerationAnnouncementSnapshot {
  sessionId?: string | null;
  isStreaming: boolean;
}

export interface GenerationAnnouncementResult {
  snapshot: GenerationAnnouncementSnapshot;
  message: string;
}

export function getGenerationAnnouncement(
  previous: GenerationAnnouncementSnapshot | null,
  next: GenerationAnnouncementSnapshot,
): GenerationAnnouncementResult {
  const sessionChanged = previous?.sessionId !== next.sessionId;
  let message = "";

  if (sessionChanged) {
    message = next.isStreaming ? GENERATION_START_ANNOUNCEMENT : "";
  } else if (!previous?.isStreaming && next.isStreaming) {
    message = GENERATION_START_ANNOUNCEMENT;
  } else if (previous?.isStreaming && !next.isStreaming) {
    message = GENERATION_COMPLETE_ANNOUNCEMENT;
  }

  return { snapshot: next, message };
}
