"use client";

import React, { useState, useEffect } from "react";
import { Plus, Loader2, Sparkles, Database, BookOpen, Clock, BarChart } from "lucide-react";
import Modal from "@/components/common/Modal";

interface ExamGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerated: (examId: string) => void;
}

export default function ExamGeneratorModal({ isOpen, onClose, onGenerated }: ExamGeneratorModalProps) {
  const [topic, setTopic] = useState("");
  const [kbName, setKbName] = useState("");
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState("medium");
  const [timeLimit, setTimeLimit] = useState<number | null>(15);
  const [availableKbs, setAvailableKbs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    fetch("/api/v1/knowledge/list")
      .then((res) => res.json())
      .then((data: any[]) => {
        if (Array.isArray(data)) {
          const names = data.map((d) => d.name).filter(Boolean);
          setAvailableKbs(names);
          if (names.length > 0 && !kbName) {
            setKbName(names[0]);
          }
        }
      })
      .catch((err) => console.error("Failed to load knowledge bases", err));
  }, [isOpen]);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError("Please specify an exam topic.");
      return;
    }
    if (!kbName.trim()) {
      setError("Please select a knowledge base.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/v1/exam/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic.trim(),
          kb_name: kbName.trim(),
          num_questions: numQuestions,
          difficulty,
          time_limit_minutes: timeLimit,
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || "Failed to generate exam.");
      }

      const exam = await res.json();
      onGenerated(exam.exam_id);
      onClose();
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred during exam generation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={loading ? () => {} : onClose}
      title="Create Autonomous Exam"
      titleIcon={<Sparkles size={16} className="text-blue-600" />}
      width="md"
      footer={
        <div className="flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-40"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleGenerate}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white shadow hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Generating Exam...
              </>
            ) : (
              <>
                <Sparkles size={16} />
                Generate Exam
              </>
            )}
          </button>
        </div>
      }
    >
      <div className="space-y-4 p-5">
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-300">
            {error}
          </div>
        )}

        {/* Knowledge base selector */}
        <div>
          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-gray-400">
            Knowledge Base Source
          </label>
          <select
            value={kbName}
            onChange={(e) => setKbName(e.target.value)}
            disabled={loading}
            className="w-full rounded-xl border border-gray-200 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 dark:border-gray-800 dark:bg-gray-900"
          >
            {availableKbs.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>

        {/* Topic Input */}
        <div>
          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-gray-400">
            Exam Topic or Subject Focus
          </label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={loading}
            placeholder="e.g. Wave Optics, Biology, or Chemical Reactions"
            className="w-full rounded-xl border border-gray-200 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 dark:border-gray-800 dark:bg-gray-900"
          />
        </div>

        {/* Number of Questions and Difficulty */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-gray-400">
              Questions
            </label>
            <select
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
              disabled={loading}
              className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500 dark:border-gray-800 dark:bg-gray-900"
            >
              <option value={5}>5 Questions</option>
              <option value={10}>10 Questions</option>
              <option value={15}>15 Questions</option>
              <option value={20}>20 Questions</option>
            </select>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-gray-400">
              Difficulty
            </label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              disabled={loading}
              className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500 dark:border-gray-800 dark:bg-gray-900"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        {/* Time Limit */}
        <div>
          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-gray-400">
            Time Limit
          </label>
          <select
            value={timeLimit === null ? "none" : timeLimit}
            onChange={(e) => setTimeLimit(e.target.value === "none" ? null : Number(e.target.value))}
            disabled={loading}
            className="w-full rounded-xl border border-gray-200 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 dark:border-gray-800 dark:bg-gray-900"
          >
            <option value="none">No Time Limit</option>
            <option value={10}>10 Minutes</option>
            <option value={15}>15 Minutes</option>
            <option value={30}>30 Minutes</option>
            <option value={60}>60 Minutes</option>
          </select>
        </div>

        <div className="rounded-xl bg-blue-50/60 p-3.5 text-xs text-blue-900 dark:bg-blue-950/30 dark:text-blue-300">
          <p className="font-semibold">Autonomous Guardrails Active:</p>
          <ul className="mt-1 list-disc space-y-0.5 pl-4">
            <li>Strictly exactly 1 correct answer per question.</li>
            <li>No &quot;all of the above&quot; or &quot;none of the above&quot; distractors.</li>
            <li>Verbatim grounded citation attached to every question.</li>
          </ul>
        </div>
      </div>
    </Modal>
  );
}
