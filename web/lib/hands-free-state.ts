export type HandsFreeState =
  | "OFF"
  | "WAKE_WAITING"
  | "WAKE_DETECTED"
  | "CAPTURING"
  | "TRANSCRIBING"
  | "THINKING"
  | "SPEAKING"
  | "RECOVERY";

export type HandsFreeEvent =
  | { type: "ENABLE"; focused: boolean }
  | { type: "DISABLE" }
  | { type: "FOCUS_LOST" }
  | { type: "FOCUS_GAINED" }
  | { type: "WAKE_DETECTED" }
  | { type: "CAPTURE_STARTED" }
  | { type: "CAPTURE_COMPLETE" }
  | { type: "TRANSCRIPT_READY"; text: string }
  | { type: "FIRST_SPEECH" }
  | { type: "SPEECH_DONE" }
  | { type: "INTERRUPT" }
  | { type: "ERROR" }
  | { type: "RECOVER" };

export function reduceHandsFreeState(
  state: HandsFreeState,
  event: HandsFreeEvent,
): HandsFreeState {
  if (event.type === "DISABLE") return "OFF";
  if (event.type === "FOCUS_LOST") return state === "OFF" ? "OFF" : "RECOVERY";
  if (event.type === "FOCUS_GAINED") return state === "OFF" ? "OFF" : "WAKE_WAITING";
  if (event.type === "ERROR") return state === "OFF" ? "OFF" : "RECOVERY";
  if (event.type === "RECOVER") return state === "OFF" ? "OFF" : "WAKE_WAITING";
  if (event.type === "INTERRUPT") return state === "OFF" ? "OFF" : "CAPTURING";

  switch (state) {
    case "OFF":
      return event.type === "ENABLE" && event.focused ? "WAKE_WAITING" : "OFF";
    case "WAKE_WAITING":
      return event.type === "WAKE_DETECTED" ? "WAKE_DETECTED" : state;
    case "WAKE_DETECTED":
      return event.type === "CAPTURE_STARTED" ? "CAPTURING" : state;
    case "CAPTURING":
      return event.type === "CAPTURE_COMPLETE" ? "TRANSCRIBING" : state;
    case "TRANSCRIBING":
      return event.type === "TRANSCRIPT_READY" && event.text.trim() ? "THINKING" : state;
    case "THINKING":
      return event.type === "FIRST_SPEECH" ? "SPEAKING" : state;
    case "SPEAKING":
      return event.type === "SPEECH_DONE" ? "WAKE_WAITING" : state;
    case "RECOVERY":
      return state;
  }
}

export function handsFreeAnnouncement(state: HandsFreeState): string {
  if (state === "OFF") return "Hands-Free mode disabled.";
  if (state === "WAKE_WAITING") return "Listening for Hey Jarvis.";
  if (state === "WAKE_DETECTED") return "Hey Jarvis detected.";
  if (state === "CAPTURING") return "Listening.";
  if (state === "TRANSCRIBING") return "Transcribing.";
  if (state === "THINKING") return "Thinking.";
  if (state === "SPEAKING") return "Speaking.";
  return "Hands-Free paused.";
}
