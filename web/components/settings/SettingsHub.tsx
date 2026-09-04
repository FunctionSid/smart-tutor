"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslation } from "react-i18next";
import {
  AudioLines,
  Bot,
  Boxes,
  Brain,
  Check,
  ChevronRight,
  Database,
  Eye,
  FileScan,
  Library,
  MessagesSquare,
  Mic,
  Network,
  Palette,
  Paperclip,
  Rocket,
  Search,
  Sparkles,
  Trash2,
  Volume2,
  Wrench,
  type LucideIcon,
} from "lucide-react";

import { apiFetch, apiUrl } from "@/lib/api";
import { setPendingPrompt } from "@/lib/pending-prompt";
import {
  getActiveModel,
  getActiveProfile,
  serviceReadiness,
  useSettings,
  type ServiceReadiness,
} from "@/components/settings/SettingsContext";
import SettingsStatusPanel from "@/components/settings/SettingsStatusPanel";
import {
  SETTINGS_CATEGORIES,
  type Lang,
  type SettingsCategory,
} from "@/lib/settings-nav";
import { useVoiceAutoplayPreference } from "@/hooks/useVoiceAutoplay";
import { inputClass, selectClass, selectOptionClass } from "@/components/settings/shared";
import {
  DEFAULT_HANDS_FREE_SETTINGS,
  readHandsFreeSettings,
  writeHandsFreeSettings,
  type HandsFreeSettings,
} from "@/lib/hands-free-settings";

type NetworkPreview = {
  apiBase: string;
};

type SapiVoice = {
  id: string;
  name: string;
  culture?: string;
};

export default function SettingsHub() {
  const { i18n } = useTranslation();
  const router = useRouter();
  const zh = i18n.language?.toLowerCase().startsWith("zh");
  const tr = useCallback((l: Lang) => (zh ? l.zh : l.en), [zh]);

  const {
    theme,
    updateTheme,
    language,
    updateLanguage,
    catalog,
    draft,
    mutateCatalog,
    applyCatalog,
    catalogEditable,
    diagnosticsResults,
    startTour,
  } = useSettings();

  const { value: autoplay, setValue: setAutoplay, loading: autoplayLoading } = useVoiceAutoplayPreference();
  const [handsFree, setHandsFree] = useState<HandsFreeSettings>(
    DEFAULT_HANDS_FREE_SETTINGS,
  );
  const [sapiVoices, setSapiVoices] = useState<SapiVoice[]>([]);
  const [sapiVoiceError, setSapiVoiceError] = useState("");

  // Tab State: "student" is default
  const [activeTab, setActiveTab] = useState<"student" | "advanced">("student");
  const studentTabRef = useRef<HTMLButtonElement>(null);
  const advancedTabRef = useRef<HTMLButtonElement>(null);

  // Memory Clear status state
  const [clearingMemory, setClearingMemory] = useState(false);
  const [memoryMessage, setMemoryMessage] = useState<string | null>(null);

  // Keyboard navigation between tabs
  const handleTabKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
      e.preventDefault();
      if (activeTab === "student") {
        setActiveTab("advanced");
        advancedTabRef.current?.focus();
      } else {
        setActiveTab("student");
        studentTabRef.current?.focus();
      }
    }
  };

  // Model preview for advanced tab
  const modelStats = useMemo(() => {
    const cat = SETTINGS_CATEGORIES.find((c) => c.key === "models");
    const services = (cat?.children ?? []).filter((l) => l.service);
    if (catalogEditable !== true) {
      return {
        total: services.length,
        configured: -1,
        passed: 0,
        failed: 0,
        states: [] as ServiceReadiness[],
      };
    }
    const states = services.map((leaf) =>
      serviceReadiness(catalog, leaf.service!, diagnosticsResults)
    );
    return {
      total: services.length,
      configured: states.filter((state) => state !== "not_configured").length,
      passed: states.filter((state) => state === "passed").length,
      failed: states.filter((state) => state === "failed").length,
      states,
    };
  }, [catalog, catalogEditable, diagnosticsResults]);

  // Network preview
  const [network, setNetwork] = useState<NetworkPreview | null>(null);
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch(apiUrl("/api/v1/settings/network"));
        if (!res.ok) return;
        const data = (await res.json()) as {
          effective?: { browser_api_base?: string };
        };
        if (cancelled) return;
        setNetwork({ apiBase: data.effective?.browser_api_base || "" });
      } catch {
        /* ignore */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    setHandsFree(readHandsFreeSettings());
    let cancelled = false;
    void (async () => {
      try {
        const resp = await apiFetch(apiUrl("/api/v1/voice/sapi/voices"));
        if (!resp.ok) throw new Error(await resp.text());
        const payload = (await resp.json()) as { voices?: SapiVoice[] };
        if (!cancelled) setSapiVoices(payload.voices ?? []);
      } catch (exc) {
        if (!cancelled) {
          setSapiVoiceError(
            exc instanceof Error ? exc.message : "Could not discover SAPI voices.",
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const updateHandsFree = useCallback((patch: Partial<HandsFreeSettings>) => {
    setHandsFree((current) => {
      const next = { ...current, ...patch, wakeWord: "Hey Jarvis" as const };
      writeHandsFreeSettings(next);
      return next;
    });
  }, []);

  const handleClearChatMemory = async () => {
    if (!window.confirm(tr({
      zh: "确定要清除所有对话记忆吗？此操作不可逆。",
      en: "Are you sure you want to clear chat memory? This cannot be undone.",
    }))) {
      return;
    }

    setClearingMemory(true);
    setMemoryMessage(null);
    try {
      const res = await apiFetch(apiUrl("/api/v1/memory/trace/chat"), { method: "DELETE" });
      if (res.ok) {
        setMemoryMessage(tr({
          zh: "已成功清除对话记忆痕迹。",
          en: "Chat memory trace cleared successfully.",
        }));
      } else {
        setMemoryMessage(tr({
          zh: "清除记忆失败，请稍后再试。",
          en: "Failed to clear memory. Please try again later.",
        }));
      }
    } catch {
      setMemoryMessage(tr({
        zh: "清除记忆时发生错误。",
        en: "Error occurred while clearing memory.",
      }));
    } finally {
      setClearingMemory(false);
    }
  };

  const activeLlmProfile = getActiveProfile(draft, "llm");
  const activeLlmModel = getActiveModel(draft, "llm");
  const llmProfiles = draft.services.llm.profiles || [];
  const llmModels = activeLlmProfile?.models || [];

  const activeTtsProfile = getActiveProfile(draft, "tts");
  const activeTtsModel = getActiveModel(draft, "tts");
  const ttsProfiles = draft.services.tts.profiles || [];

  const activeSttProfile = getActiveProfile(draft, "stt");
  const sttProfiles = draft.services.stt.profiles || [];

  return (
    <div>
      <header className="mb-7 flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h1 className="font-serif text-[24px] font-semibold leading-tight tracking-tight text-[var(--foreground)]">
            {tr({ zh: "设置", en: "Settings" })}
          </h1>
          <p className="mt-1.5 max-w-xl text-[13px] leading-relaxed text-[var(--muted-foreground)]">
            {tr({
              zh: "为学生学习个性化配置主题、语音与对话模型，或在高级模式下管理系统连接。",
              en: "Personalize theme, voice, and models for student learning, or manage system connections in Advanced mode.",
            })}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            onClick={() => {
              setPendingPrompt(
                tr({
                  zh: "帮我配置一下 Smart Tutor，先看看现在缺什么。",
                  en: "Help me configure Smart Tutor — start by checking what's missing.",
                })
              );
              router.push("/home");
            }}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-[var(--border)]/60 px-3 py-1.5 text-[12.5px] font-medium text-[var(--muted-foreground)] transition-colors hover:border-[var(--border)] hover:text-[var(--foreground)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            <Sparkles size={13} />
            {tr({ zh: "让 Smart Tutor 帮我配", en: "Set up with Smart Tutor" })}
          </button>
          <button
            type="button"
            onClick={startTour}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-[var(--border)]/60 px-3 py-1.5 text-[12.5px] font-medium text-[var(--muted-foreground)] transition-colors hover:border-[var(--border)] hover:text-[var(--foreground)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            <Rocket size={13} />
            {tr({ zh: "引导", en: "Tour" })}
          </button>
        </div>
      </header>

      {/* Accessible Tab List with role="tablist" */}
      <div
        role="tablist"
        aria-label={tr({ zh: "设置类别", en: "Settings Categories" })}
        className="mb-8 flex gap-3 border-b border-[var(--border)] pb-3"
      >
        <button
          ref={studentTabRef}
          id="tab-student"
          role="tab"
          type="button"
          aria-selected={activeTab === "student"}
          aria-controls="panel-student"
          tabIndex={activeTab === "student" ? 0 : -1}
          onClick={() => setActiveTab("student")}
          onKeyDown={handleTabKeyDown}
          className={`flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
            activeTab === "student"
              ? "bg-blue-600 text-white shadow-sm"
              : "border border-[var(--border)]/60 bg-[var(--card)] text-[var(--muted-foreground)] hover:border-[var(--border)] hover:text-[var(--foreground)]"
          }`}
        >
          <Sparkles size={16} />
          {tr({ zh: "学生设置", en: "Student Settings" })}
        </button>

        <button
          ref={advancedTabRef}
          id="tab-advanced"
          role="tab"
          type="button"
          aria-selected={activeTab === "advanced"}
          aria-controls="panel-advanced"
          tabIndex={activeTab === "advanced" ? 0 : -1}
          onClick={() => setActiveTab("advanced")}
          onKeyDown={handleTabKeyDown}
          className={`flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
            activeTab === "advanced"
              ? "bg-blue-600 text-white shadow-sm"
              : "border border-[var(--border)]/60 bg-[var(--card)] text-[var(--muted-foreground)] hover:border-[var(--border)] hover:text-[var(--foreground)]"
          }`}
        >
          <Wrench size={16} />
          {tr({ zh: "高级设置", en: "Advanced Settings" })}
        </button>
      </div>

      {/* ──────────────────────────────────────────────────────────────────────── */}
      {/* Tab 1: Student Settings Panel                                            */}
      {/* ──────────────────────────────────────────────────────────────────────── */}
      <div
        id="panel-student"
        role="tabpanel"
        aria-labelledby="tab-student"
        tabIndex={0}
        hidden={activeTab !== "student"}
        className="space-y-6 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded-2xl"
      >
        {/* Section 1: Appearance & Interface Language */}
        <section className="rounded-2xl border border-[var(--border)]/70 bg-[var(--card)] p-6 shadow-sm">
          <div className="flex items-center gap-2 border-b border-[var(--border)]/50 pb-4">
            <Palette size={18} className="text-blue-600" />
            <h2 className="text-base font-bold text-[var(--foreground)]">
              {tr({ zh: "外观与语言", en: "Appearance & Language" })}
            </h2>
          </div>

          <div className="mt-5 grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
                {tr({ zh: "界面主题", en: "Interface Theme" })}
              </label>
              <div className="mt-2 flex flex-wrap gap-2">
                {(["light", "dark", "glass", "snow"] as const).map((tMode) => (
                  <button
                    key={tMode}
                    type="button"
                    onClick={() => updateTheme(tMode)}
                    className={`rounded-lg border px-3.5 py-1.5 text-xs font-semibold capitalize transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                      theme === tMode
                        ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                        : "border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                    }`}
                  >
                    {tMode}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
                {tr({ zh: "界面语言", en: "Interface Language" })}
              </label>
              <div className="mt-2 flex gap-2">
                <button
                  type="button"
                  onClick={() => updateLanguage("en")}
                  className={`rounded-lg border px-4 py-1.5 text-xs font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                    language === "en"
                      ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                      : "border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                  }`}
                >
                  {tr({ zh: "English", en: "English" })}
                </button>
                <button
                  type="button"
                  onClick={() => updateLanguage("zh")}
                  className={`rounded-lg border px-4 py-1.5 text-xs font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                    language === "zh"
                      ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                      : "border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                  }`}
                >
                  {tr({ zh: "中文 (Chinese)", en: "中文 (Chinese)" })}
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Section 2: Active Chat / Tutor Model */}
        <section className="rounded-2xl border border-[var(--border)]/70 bg-[var(--card)] p-6 shadow-sm">
          <div className="flex items-center gap-2 border-b border-[var(--border)]/50 pb-4">
            <Brain size={18} className="text-violet-600" />
            <h2 className="text-base font-bold text-[var(--foreground)]">
              {tr({ zh: "当前对话模型 (Tutor Model)", en: "Active Chat / Tutor Model" })}
            </h2>
          </div>

          <div className="mt-5 grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
                {tr({ zh: "提供商配置", en: "LLM Profile" })}
              </label>
              <select
                className={`mt-2 ${selectClass}`}
                value={activeLlmProfile?.id || ""}
                onChange={(e) => {
                  const pId = e.target.value;
                  mutateCatalog((next) => {
                    next.services.llm.active_profile_id = pId;
                    const p = next.services.llm.profiles.find((item) => item.id === pId);
                    if (p && p.models.length > 0) {
                      next.services.llm.active_model_id = p.models[0].id;
                    }
                  });
                  void applyCatalog();
                }}
              >
                {llmProfiles.map((p) => (
                  <option key={p.id} value={p.id} className={selectOptionClass}>
                    {p.name || p.id} ({p.binding || "openai"})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
                {tr({ zh: "模型名称", en: "Active Model" })}
              </label>
              <select
                className={`mt-2 ${selectClass}`}
                value={activeLlmModel?.id || ""}
                onChange={(e) => {
                  const mId = e.target.value;
                  mutateCatalog((next) => {
                    next.services.llm.active_model_id = mId;
                  });
                  void applyCatalog();
                }}
              >
                {llmModels.map((m) => (
                  <option key={m.id} value={m.id} className={selectOptionClass}>
                    {m.name || m.model || m.id}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>

        {/* Section 3: Speech & Voice (STT & TTS) */}
        <section className="rounded-2xl border border-[var(--border)]/70 bg-[var(--card)] p-6 shadow-sm">
          <div className="flex items-center gap-2 border-b border-[var(--border)]/50 pb-4">
            <Volume2 size={18} className="text-emerald-600" />
            <h2 className="text-base font-bold text-[var(--foreground)]">
              {tr({ zh: "语音与听觉 (Voice & Speech)", en: "Voice & Speech (STT & TTS)" })}
            </h2>
          </div>

          <div className="mt-5 grid grid-cols-1 gap-6 md:grid-cols-2">
            {/* STT */}
            <div>
              <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
                <Mic size={14} /> {tr({ zh: "语音输入 (STT)", en: "Speech-to-Text (STT)" })}
              </div>
              <select
                className={`mt-2 ${selectClass}`}
                value={activeSttProfile?.id || ""}
                onChange={(e) => {
                  const pId = e.target.value;
                  mutateCatalog((next) => {
                    next.services.stt.active_profile_id = pId;
                  });
                  void applyCatalog();
                }}
              >
                {sttProfiles.map((p) => (
                  <option key={p.id} value={p.id} className={selectOptionClass}>
                    {p.name || p.id}
                  </option>
                ))}
              </select>
            </div>

            {/* TTS */}
            <div>
              <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
                <AudioLines size={14} /> {tr({ zh: "语音朗读 (TTS)", en: "Text-to-Speech (TTS)" })}
              </div>
              <select
                className={`mt-2 ${selectClass}`}
                value={activeTtsProfile?.id || ""}
                onChange={(e) => {
                  const pId = e.target.value;
                  mutateCatalog((next) => {
                    next.services.tts.active_profile_id = pId;
                  });
                  void applyCatalog();
                }}
              >
                {ttsProfiles.map((p) => (
                  <option key={p.id} value={p.id} className={selectOptionClass}>
                    {p.name || p.id}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Autoplay toggle */}
          <div className="mt-6 flex items-center justify-between rounded-xl border border-[var(--border)]/60 bg-[var(--card)]/40 p-4">
            <div>
              <div className="text-sm font-semibold text-[var(--foreground)]">
                {tr({ zh: "自动朗读回复 (Voice Autoplay)", en: "Auto-play replies aloud" })}
              </div>
              <p className="mt-0.5 text-xs text-[var(--muted-foreground)]">
                {tr({
                  zh: "智能导师完成回答后自动朗读语音内容。",
                  en: "Read assistant replies aloud automatically when answers finish.",
                })}
              </p>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={autoplay}
              disabled={autoplayLoading}
              onClick={() => setAutoplay(!autoplay)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:opacity-50 ${
                autoplay ? "bg-blue-600" : "bg-[var(--border)]"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform ${
                  autoplay ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          <div className="mt-6 rounded-xl border border-[var(--border)]/60 bg-[var(--card)]/40 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-[var(--foreground)]">
                  {tr({ zh: "免手动语音 (Hands-Free)", en: "Hands-Free" })}
                </div>
                <p className="mt-0.5 text-xs text-[var(--muted-foreground)]">
                  {tr({
                    zh: "使用本地 Hey Jarvis 唤醒词、语音输入和朗读。仅在浏览器窗口聚焦时监听。",
                    en: "Use local Hey Jarvis wake detection, voice input, and speech. Listening only runs while the browser window is focused.",
                  })}
                </p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={handsFree.enabled}
                onClick={() => updateHandsFree({ enabled: !handsFree.enabled })}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                  handsFree.enabled ? "bg-blue-600" : "bg-[var(--border)]"
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform ${
                    handsFree.enabled ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>

            <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
              <label className="block">
                <span className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
                  {tr({ zh: "唤醒词", en: "Wake word" })}
                </span>
                <input className={`mt-2 ${inputClass}`} value="Hey Jarvis" readOnly />
              </label>
              <label className="block">
                <span className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
                  {tr({ zh: "SAPI 声音", en: "SAPI Voice" })}
                </span>
                <select
                  className={`mt-2 ${selectClass}`}
                  value={handsFree.sapiVoice}
                  onChange={(event) => updateHandsFree({ sapiVoice: event.target.value })}
                >
                  <option value="" className={selectOptionClass}>
                    {tr({ zh: "系统默认", en: "System default" })}
                  </option>
                  {sapiVoices.map((voice) => (
                    <option key={voice.id} value={voice.name} className={selectOptionClass}>
                      {voice.name}
                      {voice.culture ? ` (${voice.culture})` : ""}
                    </option>
                  ))}
                </select>
                {sapiVoiceError ? (
                  <span className="mt-1 block text-[11px] text-[var(--destructive)]">
                    {sapiVoiceError}
                  </span>
                ) : null}
              </label>
              <label className="block">
                <span className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
                  {tr({ zh: "最短插话时长", en: "Minimum barge-in speech" })}
                </span>
                <input
                  className={`mt-2 ${inputClass}`}
                  type="number"
                  min={200}
                  max={2000}
                  step={50}
                  value={handsFree.minBargeInMs}
                  onChange={(event) =>
                    updateHandsFree({ minBargeInMs: Number(event.target.value) })
                  }
                />
              </label>
              <label className="block">
                <span className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
                  {tr({ zh: "朗读音量", en: "Volume" })}
                </span>
                <input
                  className="mt-3 w-full accent-blue-600"
                  type="range"
                  min={0}
                  max={100}
                  value={handsFree.volume}
                  onChange={(event) => updateHandsFree({ volume: Number(event.target.value) })}
                />
              </label>
            </div>
          </div>
        </section>

        {/* Section 4: Memory Privacy & Clear Controls */}
        <section className="rounded-2xl border border-[var(--border)]/70 bg-[var(--card)] p-6 shadow-sm">
          <div className="flex items-center gap-2 border-b border-[var(--border)]/50 pb-4">
            <Brain size={18} className="text-amber-600" />
            <h2 className="text-base font-bold text-[var(--foreground)]">
              {tr({ zh: "记忆与隐私 (Memory Privacy)", en: "Memory Privacy & Data Controls" })}
            </h2>
          </div>

          <div className="mt-4 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <p className="text-sm text-[var(--foreground)] font-medium">
                {tr({
                  zh: "本地对话记忆是您私有的学习记录，保存在本机项目中。",
                  en: "Chat memory is stored locally inside your project folder and kept private.",
                })}
              </p>
              <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                {tr({
                  zh: "您可以随时清除对话记忆痕迹以重新开始学习画像。",
                  en: "You can clear chat memory traces at any time to reset your student profile.",
                })}
              </p>
            </div>

            <button
              type="button"
              disabled={clearingMemory}
              onClick={handleClearChatMemory}
              className="inline-flex shrink-0 items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-xs font-semibold text-red-700 shadow-sm transition hover:bg-red-100 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-300 disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
            >
              <Trash2 size={14} />
              {clearingMemory ? tr({ zh: "正在清除...", en: "Clearing..." }) : tr({ zh: "清除对话记忆", en: "Clear Chat Memory" })}
            </button>
          </div>

          {memoryMessage && (
            <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50/60 p-3 text-xs font-medium text-blue-800 dark:border-blue-900/40 dark:bg-blue-950/30 dark:text-blue-300">
              {memoryMessage}
            </div>
          )}
        </section>

        {/* Section 5: Basic Attachment Preferences */}
        <section className="rounded-2xl border border-[var(--border)]/70 bg-[var(--card)] p-6 shadow-sm">
          <div className="flex items-center gap-2 border-b border-[var(--border)]/50 pb-4">
            <Paperclip size={18} className="text-teal-600" />
            <h2 className="text-base font-bold text-[var(--foreground)]">
              {tr({ zh: "附件首选项", en: "Attachment Preferences" })}
            </h2>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-[var(--foreground)]">
                {tr({
                  zh: "支持向对话中拖入 PDF、TXT、DOCX 学习文档作为临时附件。",
                  en: "Upload PDFs, text, and documents into chat as study attachments.",
                })}
              </p>
              <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                {tr({
                  zh: "系统自动提取文本并匹配当前学习上下文预算。",
                  en: "Text is extracted within the configured context budget.",
                })}
              </p>
            </div>
            <Link
              href="/settings/attachments"
              className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:underline dark:text-blue-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
            >
              {tr({ zh: "附件详情配置", en: "Configure limits" })} <ChevronRight size={14} />
            </Link>
          </div>
        </section>
      </div>

      {/* ──────────────────────────────────────────────────────────────────────── */}
      {/* Tab 2: Advanced Settings Panel                                           */}
      {/* ──────────────────────────────────────────────────────────────────────── */}
      <div
        id="panel-advanced"
        role="tabpanel"
        aria-labelledby="tab-advanced"
        tabIndex={0}
        hidden={activeTab !== "advanced"}
        className="space-y-6 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded-2xl"
      >
        <SettingsStatusPanel />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {SETTINGS_CATEGORIES.map((category) => (
            <CategoryBlock
              key={category.key}
              category={category}
              tr={tr}
              modelStats={category.key === "models" ? modelStats : undefined}
              network={category.key === "network" ? network : undefined}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function CategoryBlock({
  category,
  tr,
  modelStats,
  network,
}: {
  category: SettingsCategory;
  tr: (l: Lang) => string;
  modelStats?: {
    total: number;
    configured: number;
    passed: number;
    failed: number;
    states: ServiceReadiness[];
  };
  network?: NetworkPreview | null;
}) {
  const Icon: LucideIcon = category.icon;

  return (
    <Link
      href={category.href}
      data-tour={`tour-cat-${category.key}`}
      className="group relative flex min-h-[120px] flex-col justify-between rounded-2xl border border-[var(--border)]/70 bg-[var(--card)] p-5 transition-all duration-150 hover:border-[var(--foreground)]/20 hover:shadow-[0_4px_24px_-16px_rgba(0,0,0,0.3)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <Icon
            size={19}
            strokeWidth={1.6}
            className="text-[var(--muted-foreground)] transition-colors group-hover:text-[var(--foreground)]"
          />
          <h3 className="text-[15.5px] font-medium tracking-tight text-[var(--foreground)]">
            {tr(category.label)}
          </h3>
        </div>
        <ChevronRight
          size={16}
          className="mt-0.5 shrink-0 text-[var(--muted-foreground)]/30 transition-all group-hover:translate-x-0.5 group-hover:text-[var(--muted-foreground)]"
        />
      </div>

      <div className="mt-4">
        {modelStats ? (
          <ModelPreview stats={modelStats} blurb={tr(category.blurb)} tr={tr} />
        ) : network !== undefined && network !== null ? (
          <NetworkPreviewRow network={network} tr={tr} />
        ) : (
          <p className="text-[12.5px] leading-relaxed text-[var(--muted-foreground)]">
            {tr(category.blurb)}
          </p>
        )}
      </div>
    </Link>
  );
}

function ModelPreview({
  stats,
  blurb,
  tr,
}: {
  stats: {
    total: number;
    configured: number;
    passed: number;
    failed: number;
    states: ServiceReadiness[];
  };
  blurb: string;
  tr: (l: Lang) => string;
}) {
  if (stats.configured < 0) {
    return (
      <p className="text-[12.5px] leading-relaxed text-[var(--muted-foreground)]">
        {blurb}
      </p>
    );
  }
  return (
    <div className="flex items-center gap-2.5">
      <div className="flex items-center gap-1">
        {stats.states.map((state, i) => (
          <span
            key={i}
            className={`h-1.5 w-1.5 rounded-full ${
              state === "passed"
                ? "bg-emerald-500"
                : state === "failed"
                  ? "bg-red-500"
                  : state === "untested"
                    ? "bg-zinc-400 dark:bg-zinc-500"
                    : "bg-zinc-300/60 dark:bg-zinc-700"
            }`}
          />
        ))}
      </div>
      <span className="text-[12px] font-medium text-[var(--foreground)]">
        {stats.configured} / {stats.total}
      </span>
    </div>
  );
}

function NetworkPreviewRow({
  network,
  tr,
}: {
  network: NetworkPreview;
  tr: (l: Lang) => string;
}) {
  const base = network.apiBase.trim();
  if (!base) {
    return (
      <p className="text-[12.5px] leading-relaxed text-[var(--muted-foreground)]">
        {tr({ zh: "端口与跨域配置", en: "Ports & CORS" })}
      </p>
    );
  }
  return (
    <div className="truncate font-mono text-[11.5px] text-[var(--muted-foreground)]">
      {base}
    </div>
  );
}
