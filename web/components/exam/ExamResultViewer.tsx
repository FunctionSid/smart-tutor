"use client";

import React from "react";
import { CheckCircle2, XCircle, ArrowLeft, RefreshCw, FileText, Award, BookOpen } from "lucide-react";
import MarkdownRenderer from "@/components/common/MarkdownRenderer";

export interface QuestionResultUI {
  question_id: string;
  question: string;
  options: string[];
  selected_option: string | null;
  correct_option: string;
  is_correct: boolean;
  explanation: string;
  citation: {
    source: string;
    page?: number | null;
    quote: string;
  };
  topic: string;
  knowledge_point_id: string;
}

export interface ExamResultUI {
  attempt_id: string;
  exam_id: string;
  score: number;
  total: number;
  percentage: number;
  time_spent_seconds: number;
  results: QuestionResultUI[];
  topic_breakdown: Record<string, { correct: number; total: number }>;
  submitted_at: number;
}

interface ExamResultViewerProps {
  result: ExamResultUI;
  onRetakeMissed?: (missedQuestionIds: string[]) => void;
  onDone: () => void;
}

export default function ExamResultViewer({ result, onRetakeMissed, onDone }: ExamResultViewerProps) {
  const missed = result.results.filter((r) => !r.is_correct);
  const missedCount = missed.length;

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainder = secs % 60;
    return `${mins}m ${remainder}s`;
  };

  return (
    <div className="mx-auto max-w-4xl p-6">
      {/* Header Banner */}
      <div className="mb-8 rounded-2xl border bg-gradient-to-br from-blue-50 to-indigo-50 p-6 shadow-sm dark:from-blue-950/20 dark:to-indigo-950/20">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-700 dark:text-blue-300">
              <Award size={16} /> Exam Results
            </div>
            <h1 className="mt-1 text-3xl font-extrabold text-gray-900 dark:text-gray-100">
              Score: {result.score} / {result.total} ({result.percentage}%)
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Time completed: {formatTime(result.time_spent_seconds)}
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5">
            {missedCount > 0 && onRetakeMissed && (
              <button
                type="button"
                onClick={() => onRetakeMissed(missed.map((m) => m.question_id))}
                className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-blue-700"
              >
                <RefreshCw size={15} /> Retake {missedCount} Missed Questions
              </button>
            )}
            <button
              type="button"
              onClick={onDone}
              className="inline-flex items-center gap-2 rounded-xl border bg-white px-4 py-2 text-sm font-medium hover:bg-gray-50 dark:bg-gray-900 dark:hover:bg-gray-800"
            >
              <ArrowLeft size={15} /> Back to Library
            </button>
          </div>
        </div>
      </div>

      {/* Topic Mastery Breakdown Table (Excel-copy friendly) */}
      <section className="mb-8">
        <h2 className="mb-3 text-lg font-bold text-gray-900 dark:text-gray-100">Performance by Topic</h2>
        <div className="overflow-x-auto rounded-xl border">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs font-semibold uppercase text-gray-700 dark:bg-gray-800 dark:text-gray-300">
              <tr>
                <th className="px-4 py-3">Topic</th>
                <th className="px-4 py-3">Correct</th>
                <th className="px-4 py-3">Total</th>
                <th className="px-4 py-3">Accuracy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
              {Object.entries(result.topic_breakdown).map(([topic, stats]) => {
                const acc = stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) : 0;
                return (
                  <tr key={topic} className="hover:bg-gray-50/50 dark:hover:bg-gray-900/50">
                    <td className="px-4 py-3 font-medium">{topic}</td>
                    <td className="px-4 py-3">{stats.correct}</td>
                    <td className="px-4 py-3">{stats.total}</td>
                    <td className="px-4 py-3 font-semibold">{acc}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* Question Details with Grounded Citations */}
      <section className="space-y-6">
        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">Detailed Review & Explanations</h2>

        {result.results.map((q, idx) => {
          return (
            <div
              key={q.question_id}
              className={`rounded-2xl border p-6 transition-colors ${
                q.is_correct
                  ? "border-green-200 bg-green-50/20 dark:border-green-900/40"
                  : "border-red-200 bg-red-50/20 dark:border-red-900/40"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-gray-900 dark:text-gray-100">Question {idx + 1}</span>
                  <span className="text-xs text-gray-500">({q.topic})</span>
                </div>
                {q.is_correct ? (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800 dark:bg-green-950 dark:text-green-300">
                    <CheckCircle2 size={14} /> Correct
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-800 dark:bg-red-950 dark:text-red-300">
                    <XCircle size={14} /> Incorrect
                  </span>
                )}
              </div>

              <div className="mt-3 text-base font-medium text-gray-900 dark:text-gray-100">
                <MarkdownRenderer content={q.question} variant="compact" enableMath />
              </div>

              <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
                {q.options.map((optText, optIdx) => {
                  const letter = ["A", "B", "C", "D"][optIdx];
                  const isUser = q.selected_option === letter;
                  const isCorrectOpt = q.correct_option === letter;

                  let optClass = "border-gray-200 bg-white dark:bg-gray-900 dark:border-gray-800";
                  if (isCorrectOpt) {
                    optClass = "border-green-500 bg-green-100/60 font-semibold text-green-900 dark:bg-green-950/60 dark:text-green-200";
                  } else if (isUser && !isCorrectOpt) {
                    optClass = "border-red-400 bg-red-100/60 text-red-900 dark:bg-red-950/60 dark:text-red-200";
                  }

                  return (
                    <div key={letter} className={`flex items-center gap-2.5 rounded-xl border p-3 text-sm ${optClass}`}>
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-black/5 text-xs font-bold dark:bg-white/10">
                        {letter}
                      </span>
                      <span className="min-w-0 leading-relaxed">
                        <MarkdownRenderer content={optText} variant="compact" enableMath />
                      </span>
                      {isUser && !isCorrectOpt && <span className="ml-auto text-xs font-bold text-red-600">Your choice</span>}
                      {isCorrectOpt && <span className="ml-auto text-xs font-bold text-green-700">Correct</span>}
                    </div>
                  );
                })}
              </div>

              {/* Grounded Explanation */}
              <div className="mt-4 rounded-xl border border-blue-100 bg-blue-50/50 p-4 text-sm text-gray-800 dark:border-blue-900/30 dark:bg-blue-950/20 dark:text-gray-200">
                <p className="font-semibold text-blue-900 dark:text-blue-300">Explanation:</p>
                <div className="mt-1">
                  <MarkdownRenderer content={q.explanation} variant="compact" enableMath />
                </div>

                {/* Grounding Citation Box */}
                {q.citation && (
                  <div className="mt-3 flex items-start gap-2 border-t border-blue-200/60 pt-2.5 text-xs text-gray-600 dark:border-blue-800/60 dark:text-gray-400">
                    <FileText size={14} className="mt-0.5 shrink-0 text-blue-600 dark:text-blue-400" />
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">Source:</span> {q.citation.source}
                      {q.citation.page && <span> (Page {q.citation.page})</span>}
                      {q.citation.quote && (
                        <blockquote className="mt-1 border-l-2 border-blue-400 pl-2 italic text-gray-700 dark:text-gray-300">
                          &quot;{q.citation.quote}&quot;
                        </blockquote>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </section>
    </div>
  );
}
