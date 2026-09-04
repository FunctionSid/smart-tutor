"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Ear, Loader2, Mic, Square, Volume2 } from "lucide-react";
import { useTranslation } from "react-i18next";

import { apiFetch, apiUrl } from "@/lib/api";
import {
  DEFAULT_HANDS_FREE_SETTINGS,
  HANDS_FREE_RUNTIME_EVENT,
  readHandsFreeSettings,
  writeHandsFreeSettings,
  type HandsFreeSettings,
} from "@/lib/hands-free-settings";
import {
  handsFreeAnnouncement,
  reduceHandsFreeState,
  type HandsFreeState,
} from "@/lib/hands-free-state";
import { shouldBargeIn } from "@/lib/hands-free-speech";

const TARGET_SAMPLE_RATE = 16_000;
const WAKE_CHUNK_SAMPLES = 12_800;
const WAKE_DEBOUNCE_MS = 1500;

function floatTo16BitPcm(samples: Float32Array): Int16Array {
  const output = new Int16Array(samples.length);
  for (let i = 0; i < samples.length; i += 1) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    output[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return output;
}

function resampleTo16k(input: Float32Array, sourceRate: number): Float32Array {
  if (sourceRate === TARGET_SAMPLE_RATE) return input;
  const ratio = sourceRate / TARGET_SAMPLE_RATE;
  const length = Math.floor(input.length / ratio);
  const output = new Float32Array(length);
  for (let i = 0; i < length; i += 1) {
    output[i] = input[Math.min(input.length - 1, Math.floor(i * ratio))];
  }
  return output;
}

function int16ToBase64(pcm: Int16Array): string {
  const bytes = new Uint8Array(pcm.buffer, pcm.byteOffset, pcm.byteLength);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function rms(samples: Float32Array): number {
  if (!samples.length) return 0;
  let total = 0;
  for (const sample of samples) total += sample * sample;
  return Math.sqrt(total / samples.length);
}

export default function HandsFreeControl({
  isStreaming,
  onSend,
  onCancelStreaming,
}: {
  isStreaming: boolean;
  onSend: (content: string) => void;
  onCancelStreaming: () => void;
}) {
  const { t } = useTranslation();
  const [settings, setSettings] = useState<HandsFreeSettings>(
    DEFAULT_HANDS_FREE_SETTINGS,
  );
  const [state, setState] = useState<HandsFreeState>("OFF");
  const [error, setError] = useState("");
  const [supported, setSupported] = useState<boolean | null>(null);
  const stateRef = useRef<HandsFreeState>("OFF");
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const wakeBufferRef = useRef<number[]>([]);
  const wakeBusyRef = useRef(false);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const speechStartedAtRef = useRef<number | null>(null);
  const bargeSpeechStartedAtRef = useRef<number | null>(null);
  const lastVoiceAtRef = useRef<number>(0);
  const lastWakeAtRef = useRef<number>(0);
  const captureTimerRef = useRef<number>(0);

  const enabled = state !== "OFF";
  const announcement = error || handsFreeAnnouncement(state);

  const transition = useCallback((event: Parameters<typeof reduceHandsFreeState>[1]) => {
    setState((current) => {
      const next = reduceHandsFreeState(current, event);
      stateRef.current = next;
      return next;
    });
  }, []);

  const cleanupAudio = useCallback(() => {
    if (captureTimerRef.current) window.clearTimeout(captureTimerRef.current);
    captureTimerRef.current = 0;
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      recorderRef.current.stop();
    }
    recorderRef.current = null;
    processorRef.current?.disconnect();
    sourceRef.current?.disconnect();
    void audioContextRef.current?.close();
    streamRef.current?.getTracks().forEach((track) => track.stop());
    processorRef.current = null;
    sourceRef.current = null;
    audioContextRef.current = null;
    streamRef.current = null;
    wakeBufferRef.current = [];
    wakeBusyRef.current = false;
  }, []);

  const transcribe = useCallback(async (blob: Blob) => {
    const form = new FormData();
    form.append("file", blob, "hands-free.webm");
    const resp = await apiFetch(apiUrl("/api/v1/voice/stt"), {
      method: "POST",
      body: form,
    });
    if (!resp.ok) throw new Error(await resp.text());
    const payload = (await resp.json()) as { text?: string };
    return (payload.text || "").trim();
  }, []);

  const finishCapture = useCallback(async () => {
    const recorder = recorderRef.current;
    if (!recorder || recorder.state === "inactive") return;
    transition({ type: "CAPTURE_COMPLETE" });
    recorder.stop();
  }, [transition]);

  const beginCapture = useCallback(() => {
    const stream = streamRef.current;
    if (!stream) return;
    chunksRef.current = [];
    const recorder = new MediaRecorder(stream);
    recorderRef.current = recorder;
    speechStartedAtRef.current = null;
    lastVoiceAtRef.current = Date.now();
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };
    recorder.onstop = () => {
      void (async () => {
        try {
          if (captureTimerRef.current) window.clearTimeout(captureTimerRef.current);
          captureTimerRef.current = 0;
          transition({ type: "CAPTURE_COMPLETE" });
          const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
          const text = await transcribe(blob);
          transition({ type: "TRANSCRIPT_READY", text });
          if (text) onSend(text);
        } catch (exc) {
          setError(exc instanceof Error ? exc.message : "Hands-Free transcription failed.");
          transition({ type: "ERROR" });
          window.setTimeout(() => transition({ type: "RECOVER" }), 1200);
        }
      })();
    };
    recorder.start();
    captureTimerRef.current = window.setTimeout(() => {
      void finishCapture();
    }, settings.maxCaptureMs);
    transition({ type: "CAPTURE_STARTED" });
  }, [finishCapture, onSend, settings.maxCaptureMs, transcribe, transition]);

  const scoreWake = useCallback(
    async (pcm: Int16Array) => {
      if (wakeBusyRef.current) return;
      wakeBusyRef.current = true;
      try {
        const resp = await apiFetch(apiUrl("/api/v1/voice/wake/hey-jarvis"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            pcm16_base64: int16ToBase64(pcm),
            sample_rate: TARGET_SAMPLE_RATE,
            threshold: settings.wakeThreshold,
          }),
        });
        if (!resp.ok) throw new Error(await resp.text());
        const payload = (await resp.json()) as { detected?: boolean };
        if (!payload.detected) return;
        const now = Date.now();
        if (now - lastWakeAtRef.current < WAKE_DEBOUNCE_MS) return;
        lastWakeAtRef.current = now;
        transition({ type: "WAKE_DETECTED" });
        window.dispatchEvent(
          new CustomEvent(HANDS_FREE_RUNTIME_EVENT, {
            detail: { enabled: true, interrupted: true },
          }),
        );
        if (isStreaming) onCancelStreaming();
        beginCapture();
      } catch (exc) {
        setError(exc instanceof Error ? exc.message : "Hey Jarvis detection failed.");
        transition({ type: "ERROR" });
      } finally {
        wakeBusyRef.current = false;
      }
    },
    [beginCapture, isStreaming, onCancelStreaming, settings.wakeThreshold, transition],
  );

  const startWakeListening = useCallback(async () => {
    try {
      setError("");
      const probe = await apiFetch(apiUrl("/api/v1/voice/wake/hey-jarvis/probe"));
      if (!probe.ok) throw new Error(await probe.text());
      setSupported(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      streamRef.current = stream;
      const context = new AudioContext();
      audioContextRef.current = context;
      const source = context.createMediaStreamSource(stream);
      sourceRef.current = source;
      const processor = context.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;
      processor.onaudioprocess = (event) => {
        if (document.hidden || !document.hasFocus()) return;
        const input = event.inputBuffer.getChannelData(0);
        const currentState = stateRef.current;
        const currentRms = rms(input);
        if (currentState === "CAPTURING") {
          const now = Date.now();
          if (currentRms > 0.018) {
            speechStartedAtRef.current ??= now;
            lastVoiceAtRef.current = now;
          }
          const speechStartedAt = speechStartedAtRef.current;
          if (
            speechStartedAt &&
            now - speechStartedAt >= settings.minSpeechMs &&
            now - lastVoiceAtRef.current >= settings.silenceMs
          ) {
            void finishCapture();
          }
          return;
        }
        if (currentState === "SPEAKING") {
          const now = Date.now();
          if (currentRms > 0.02) {
            bargeSpeechStartedAtRef.current ??= now;
          } else {
            bargeSpeechStartedAtRef.current = null;
          }
          const spokenMs = bargeSpeechStartedAtRef.current
            ? now - bargeSpeechStartedAtRef.current
            : 0;
          if (shouldBargeIn(spokenMs, false, settings.minBargeInMs)) {
            bargeSpeechStartedAtRef.current = null;
            window.dispatchEvent(
              new CustomEvent(HANDS_FREE_RUNTIME_EVENT, {
                detail: { enabled: true, interrupted: true },
              }),
            );
            onCancelStreaming();
            transition({ type: "INTERRUPT" });
            beginCapture();
          }
          return;
        }
        if (currentState !== "WAKE_WAITING") return;
        const resampled = resampleTo16k(input, context.sampleRate);
        wakeBufferRef.current.push(...resampled);
        if (wakeBufferRef.current.length < WAKE_CHUNK_SAMPLES) return;
        const chunk = new Float32Array(wakeBufferRef.current.splice(0, WAKE_CHUNK_SAMPLES));
        void scoreWake(floatTo16BitPcm(chunk));
      };
      source.connect(processor);
      processor.connect(context.destination);
      transition({ type: "ENABLE", focused: !document.hidden && document.hasFocus() });
    } catch (exc) {
      setSupported(false);
      setError(exc instanceof Error ? exc.message : "Hands-Free microphone setup failed.");
      transition({ type: "ERROR" });
      cleanupAudio();
    }
  }, [beginCapture, cleanupAudio, finishCapture, onCancelStreaming, scoreWake, settings.minBargeInMs, settings.minSpeechMs, settings.silenceMs, transition]);

  const stop = useCallback(() => {
    cleanupAudio();
    transition({ type: "DISABLE" });
  }, [cleanupAudio, transition]);

  const toggle = useCallback(() => {
    if (enabled) {
      stop();
      setSettings((current) => {
      const next = { ...current, enabled: false };
      writeHandsFreeSettings(next);
      window.dispatchEvent(
        new CustomEvent(HANDS_FREE_RUNTIME_EVENT, { detail: { enabled: false } }),
      );
      return next;
      });
      return;
    }
    setSettings((current) => {
      const next = { ...current, enabled: true };
      writeHandsFreeSettings(next);
      window.dispatchEvent(
        new CustomEvent(HANDS_FREE_RUNTIME_EVENT, { detail: { enabled: true } }),
      );
      return next;
    });
    void startWakeListening();
  }, [enabled, startWakeListening, stop]);

  useEffect(() => {
    setSettings(readHandsFreeSettings());
    return cleanupAudio;
  }, [cleanupAudio]);

  useEffect(() => {
    const handler = (event: Event) => {
      const detail = (event as CustomEvent<{ speaking?: boolean; speechDone?: boolean }>).detail;
      if (detail?.speaking) transition({ type: "FIRST_SPEECH" });
      if (detail?.speechDone) transition({ type: "SPEECH_DONE" });
    };
    window.addEventListener(HANDS_FREE_RUNTIME_EVENT, handler);
    return () => window.removeEventListener(HANDS_FREE_RUNTIME_EVENT, handler);
  }, [transition]);

  useEffect(() => {
    const onFocus = () => {
      if (enabled) transition({ type: "FOCUS_GAINED" });
    };
    const onBlur = () => {
      if (enabled) transition({ type: "FOCUS_LOST" });
    };
    window.addEventListener("focus", onFocus);
    window.addEventListener("blur", onBlur);
    const onVisibility = () => {
      if (document.hidden) onBlur();
      else onFocus();
    };
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      window.removeEventListener("focus", onFocus);
      window.removeEventListener("blur", onBlur);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [enabled, transition]);

  useEffect(() => {
    if (!enabled) return;
    if (isStreaming && state === "THINKING") transition({ type: "FIRST_SPEECH" });
    if (!isStreaming && (state === "THINKING" || state === "SPEAKING")) {
      transition({ type: "SPEECH_DONE" });
    }
  }, [enabled, isStreaming, state, transition]);

  const Icon =
    state === "WAKE_WAITING" ? Ear : state === "SPEAKING" ? Volume2 : state === "OFF" ? Mic : Loader2;
  const label = enabled ? t("Stop Hands-Free") : t("Hands-Free");
  const status =
    state === "OFF"
      ? t("Hands-Free")
      : state === "WAKE_WAITING"
        ? t('Waiting for "Hey Jarvis"')
        : t(handsFreeAnnouncement(state));

  return (
    <div className="flex min-w-0 items-center gap-1.5">
      <button
        type="button"
        onClick={toggle}
        className={`group inline-flex h-8 shrink-0 items-center gap-1.5 rounded-[10px] px-2.5 text-[12px] font-medium transition-[background-color,color,transform] duration-150 active:scale-95 ${
          enabled
            ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
            : "text-[var(--muted-foreground)] hover:bg-[var(--muted)]/55 hover:text-[var(--foreground)]"
        }`}
        aria-pressed={enabled}
        aria-label={label}
        title={label}
      >
        <Icon
          size={15}
          strokeWidth={1.9}
          className={state !== "OFF" && state !== "WAKE_WAITING" && state !== "SPEAKING" ? "animate-spin" : ""}
        />
        <span className="hidden max-w-[150px] truncate sm:inline">{status}</span>
      </button>
      {enabled && (
        <button
          type="button"
          onClick={stop}
          className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-[10px] text-[var(--muted-foreground)] transition hover:bg-[var(--muted)]/55 hover:text-[var(--foreground)]"
          aria-label={t("Stop Hands-Free")}
          title={t("Stop Hands-Free")}
        >
          <Square size={14} strokeWidth={2} />
        </button>
      )}
      <span className="sr-only" role="status" aria-live="polite" aria-atomic="true">
        {supported === false ? error : t(announcement)}
      </span>
    </div>
  );
}
