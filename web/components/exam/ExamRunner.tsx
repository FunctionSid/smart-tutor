"use client";

import React, { useState, useEffect, useId } from "react";
import { CheckCircle2, AlertCircle, Clock, ArrowLeft, ArrowRight, Send, ListChecks } from "lucide-react";
import MarkdownRenderer from "@/components/common/MarkdownRenderer";

export interface ExamQuestionUI {
  id: string;
  topic: string;
  question: string;
  options: string[];
  difficulty: string;
}

export interface ExamSpecUI {
  exam_id: string;
  title: string;
  topic: string;
  kb_name: string;
  num_questions: number;
  time_limit_minutes?: number | null;
  questions: ExamQuestionUI[];
}

interface ExamRunnerProps {
  exam: ExamSpecUI;
  onSubmit: (answers: Record<string, string>, timeSpentSeconds: number) => void;
  onExit?: () => void;
}

export default function ExamRunner({ exam, onSubmit, onExit }: ExamRunnerProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timeRemaining, setTimeRemaining] = useState<number | null>(
    exam.time_limit_minutes ? exam.time_limit_minutes * 60 : null
  );
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [isReviewing, setIsReviewing] = useState(false);
  const [timerAnnouncement, setTimerAnnouncement] = useState("");

  const formId = useId();
  const total = exam.questions.length;
  const currentQ = exam.questions[currentIndex];

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
      if (timeRemaining !== null) {
        setTimeRemaining((prev) => {
          if (prev === null) return null;
          if (prev <= 1) {
            clearInterval(timer);
            handleSubmit();
            return 0;
          }
          if (prev === 300) setTimerAnnouncement("5 minutes remaining");
          else if (prev === 60) setTimerAnnouncement("1 minute remaining");
          return prev - 1;
        });
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [timeRemaining]);

  const selectOption = (letter: string) => {
    if (!currentQ) return;
    setAnswers((prev) => ({ ...prev, [currentQ.id]: letter }));
  };

  const handleSubmit = () => {
    onSubmit(answers, elapsedSeconds);
  };

  const answeredCount = Object.keys(answers).length;
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  if (isReviewing) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <div className="mb-6 flex items-center justify-between border-b pb-4">
          <div>
            <h1 className="text-2xl font-bold">{exam.title} - Review</h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Answered {answeredCount} of {total} questions
            </p>
          </div>
          <button
            type="button"
            onClick={() => setIsReviewing(false)}
            className="inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ArrowLeft size={16} /> Back to questions
          </button>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {exam.questions.map((q, idx) => {
            const answered = Boolean(answers[q.id]);
            return (
              <button
                key={q.id}
                type="button"
                onClick={() => {
                  setCurrentIndex(idx);
                  setIsReviewing(false);
                }}
                className="flex items-center justify-between rounded-xl border p-4 text-left transition hover:border-blue-500"
              >
                <div>
                  <span className="font-semibold">Question {idx + 1}</span>
                  <p className="truncate text-xs text-gray-500 dark:text-gray-400">{q.topic}</p>
                </div>
                <div className="flex items-center gap-2">
                  {answered ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-1 text-xs font-medium text-green-800 dark:bg-green-950 dark:text-green-300">
                      <CheckCircle2 size={13} /> Option {answers[q.id]}
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-1 text-xs font-medium text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                      <AlertCircle size={13} /> Unanswered
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        <div className="mt-8 flex justify-end gap-3 border-t pt-4">
          <button
            type="button"
            onClick={() => setIsReviewing(false)}
            className="rounded-lg border px-5 py-2.5 text-sm font-medium"
          >
            Return to Exam
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white shadow hover:bg-blue-700"
          >
            <Send size={16} /> Submit Exam Now
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl p-6">
      {/* Accessible live region for screen-reader timer updates */}
      <div aria-live="polite" className="sr-only">
        {timerAnnouncement}
      </div>

      <header className="mb-6 flex flex-wrap items-center justify-between gap-4 border-b pb-4">
        <div>
          <h1 className="text-xl font-bold">{exam.title}</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Source: {exam.kb_name} | Topic: {exam.topic}
          </p>
        </div>
        <div className="flex items-center gap-4">
          {timeRemaining !== null && (
            <div
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-mono text-sm font-semibold ${
                timeRemaining < 300
                  ? "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300"
                  : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200"
              }`}
              aria-label={`Time remaining: ${formatTime(timeRemaining)}`}
            >
              <Clock size={16} />
              <span>{formatTime(timeRemaining)}</span>
            </div>
          )}
          <button
            type="button"
            onClick={() => setIsReviewing(true)}
            className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ListChecks size={15} />
            <span>Review ({answeredCount}/{total})</span>
          </button>
        </div>
      </header>

      {/* Screen reader and visual progress indicator */}
      <div className="mb-4 flex items-center justify-between text-sm font-medium text-gray-600 dark:text-gray-300">
        <span>Question {currentIndex + 1} of {total}</span>
        <span className="capitalize">{currentQ.difficulty} Difficulty</span>
      </div>

      <div className="mb-6 h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-800">
        <div
          className="h-full bg-blue-600 transition-all duration-300"
          style={{ width: `${((currentIndex + 1) / total) * 100}%` }}
        />
      </div>

      {/* Accessible fieldset with legend for the question */}
      <fieldset className="rounded-2xl border bg-white p-6 shadow-sm dark:bg-gray-900">
        <legend className="px-2 text-lg font-semibold leading-snug text-gray-900 dark:text-gray-100">
          <MarkdownRenderer content={currentQ.question} variant="compact" enableMath />
        </legend>

        <div className="mt-6 space-y-3">
          {currentQ.options.map((optionText, optIdx) => {
            const letter = ["A", "B", "C", "D"][optIdx];
            const isSelected = answers[currentQ.id] === letter;
            const inputId = `${formId}-q-${currentQ.id}-opt-${letter}`;

            return (
              <label
                key={letter}
                htmlFor={inputId}
                className={`flex cursor-pointer items-center gap-3.5 rounded-xl border p-4 transition-all ${
                  isSelected
                    ? "border-blue-600 bg-blue-50/60 ring-2 ring-blue-600/20 dark:bg-blue-950/30"
                    : "border-gray-200 hover:border-gray-300 dark:border-gray-800 dark:hover:border-gray-700"
                }`}
              >
                <input
                  type="radio"
                  id={inputId}
                  name={`question-${currentQ.id}`}
                  value={letter}
                  checked={isSelected}
                  onChange={() => selectOption(letter)}
                  className="h-4 w-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                />
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-bold text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                  {letter}
                </span>
                <span className="min-w-0 text-sm leading-relaxed text-gray-800 dark:text-gray-200">
                  <MarkdownRenderer content={optionText} variant="compact" enableMath />
                </span>
              </label>
            );
          })}
        </div>
      </fieldset>

      {/* Navigation Buttons */}
      <div className="mt-8 flex items-center justify-between">
        <button
          type="button"
          onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
          disabled={currentIndex === 0}
          className="inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-medium hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40 dark:hover:bg-gray-800"
        >
          <ArrowLeft size={16} /> Previous
        </button>

        {currentIndex === total - 1 ? (
          <button
            type="button"
            onClick={() => setIsReviewing(true)}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow hover:bg-blue-700"
          >
            Review & Submit <CheckCircle2 size={16} />
          </button>
        ) : (
          <button
            type="button"
            onClick={() => setCurrentIndex((prev) => Math.min(total - 1, prev + 1))}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow hover:bg-blue-700"
          >
            Next <ArrowRight size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
