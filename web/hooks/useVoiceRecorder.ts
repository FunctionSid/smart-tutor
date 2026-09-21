"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { apiFetch, apiUrl } from "@/lib/api";

export type RecorderState = "idle" | "recording" | "transcribing";

/**
 * Microphone capture → backend transcription. Records via MediaRecorder, posts
 * the clip to ``/api/v1/voice/stt`` (which uses the admin-configured STT
 * provider), and hands the transcript back through ``onTranscript``.
 */
export function useVoiceRecorder(onTranscript: (text: string) => void) {
  const [state, setState] = useState<RecorderState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [announcement, setAnnouncement] = useState("");
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const onTranscriptRef = useRef(onTranscript);
  onTranscriptRef.current = onTranscript;

  const releaseStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }, []);

  const start = useCallback(async () => {
    if (state !== "idle") return;
    setError(null);
    if (
      typeof navigator === "undefined" ||
      !navigator.mediaDevices?.getUserMedia ||
      typeof MediaRecorder === "undefined"
    ) {
      setError("Recording is not supported in this browser.");
      setAnnouncement("Transcription failed.");
      return;
    }
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setError("Microphone permission denied.");
      setAnnouncement("Transcription failed.");
      return;
    }
    streamRef.current = stream;
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];
    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) chunksRef.current.push(event.data);
    };
    recorder.onstop = async () => {
      const mimeType = recorder.mimeType || "audio/webm";
      releaseStream();
      const blob = new Blob(chunksRef.current, { type: mimeType });
      chunksRef.current = [];
      if (!blob.size) {
        setState("idle");
        setAnnouncement("Recording stopped. No audio was captured.");
        return;
      }
      setState("transcribing");
      setAnnouncement("Recording stopped. Transcribing voice input.");
      try {
        const ext = mimeType.includes("ogg")
          ? "ogg"
          : mimeType.includes("mp4")
            ? "mp4"
            : "webm";
        const form = new FormData();
        form.append("file", blob, `recording.${ext}`);
        const resp = await apiFetch(apiUrl("/api/v1/voice/stt"), {
          method: "POST",
          body: form,
        });
        if (!resp.ok) {
          const detail = (await resp.json().catch(() => null)) as {
            detail?: string;
          } | null;
          throw new Error(
            detail?.detail || `Transcription failed (HTTP ${resp.status}).`,
          );
        }
        const data = (await resp.json()) as { text?: string };
        const text = (data.text || "").trim();
        if (text) {
          onTranscriptRef.current(text);
          setAnnouncement("Transcription complete.");
        } else {
          setError("No speech detected.");
          setAnnouncement("No speech detected.");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Transcription failed.");
        setAnnouncement("Transcription failed.");
      } finally {
        setState("idle");
      }
    };
    recorder.start();
    recorderRef.current = recorder;
    setState("recording");
    setAnnouncement("Recording started.");
  }, [releaseStream, state]);

  const stop = useCallback(() => {
    const recorder = recorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop(); // fires onstop → transcribe
    }
  }, []);

  const toggle = useCallback(() => {
    if (state === "recording") stop();
    else if (state === "idle") void start();
  }, [start, state, stop]);

  // Stop the mic if the component unmounts mid-recording.
  useEffect(() => {
    return () => {
      const recorder = recorderRef.current;
      if (recorder && recorder.state !== "inactive") recorder.stop();
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  return { state, error, announcement, toggle, start, stop };
}
