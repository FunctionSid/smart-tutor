export interface HandsFreeSettings {
  enabled: boolean;
  wakeWord: "Hey Jarvis";
  wakeThreshold: number;
  minBargeInMs: number;
  minSpeechMs: number;
  silenceMs: number;
  maxCaptureMs: number;
  fillerMode: "minimal" | "off";
  fillerDelayMs: number;
  sapiVoice: string;
  speechRate: number;
  volume: number;
}

const STORAGE_KEY = "smarttutor:hands-free-settings";
export const HANDS_FREE_RUNTIME_EVENT = "smarttutor:hands-free-runtime";

export const DEFAULT_HANDS_FREE_SETTINGS: HandsFreeSettings = {
  enabled: false,
  wakeWord: "Hey Jarvis",
  wakeThreshold: 0.5,
  minBargeInMs: 450,
  minSpeechMs: 350,
  silenceMs: 1200,
  maxCaptureMs: 12000,
  fillerMode: "minimal",
  fillerDelayMs: 2200,
  sapiVoice: "",
  speechRate: 0,
  volume: 100,
};

export function readHandsFreeSettings(): HandsFreeSettings {
  if (typeof window === "undefined") return DEFAULT_HANDS_FREE_SETTINGS;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_HANDS_FREE_SETTINGS;
    const parsed = JSON.parse(raw) as Partial<HandsFreeSettings>;
    return {
      ...DEFAULT_HANDS_FREE_SETTINGS,
      ...parsed,
      wakeWord: "Hey Jarvis",
    };
  } catch {
    return DEFAULT_HANDS_FREE_SETTINGS;
  }
}

export function writeHandsFreeSettings(settings: HandsFreeSettings): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ ...settings, wakeWord: "Hey Jarvis" }),
  );
}

export { STORAGE_KEY as HANDS_FREE_SETTINGS_STORAGE_KEY };
