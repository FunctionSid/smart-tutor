"use client";

import React, { useState, useEffect } from "react";
import { Plus, GraduationCap, Clock, BookOpen, Loader2, ArrowRight, CheckCircle2 } from "lucide-react";
import ExamGeneratorModal from "@/components/exam/ExamGeneratorModal";
import ExamRunner, { ExamSpecUI } from "@/components/exam/ExamRunner";
import ExamResultViewer, { ExamResultUI } from "@/components/exam/ExamResultViewer";

export default function ExamPage() {
  const [exams, setExams] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeExam, setActiveExam] = useState<ExamSpecUI | null>(null);
  const [activeResult, setActiveResult] = useState<ExamResultUI | null>(null);
  const [examLoading, setExamLoading] = useState(false);

  const fetchExams = async () => {
    try {
      const res = await fetch("/api/v1/exam/list");
      if (res.ok) {
        const data = await res.json();
        setExams(data);
      }
    } catch (e) {
      console.error("Failed to load exams", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExams();
  }, []);

  const loadExam = async (examId: string) => {
    setExamLoading(true);
    try {
      const res = await fetch(`/api/v1/exam/${examId}`);
      if (res.ok) {
        const data = await res.json();
        setActiveExam(data);
        setActiveResult(null);
      }
    } catch (e) {
      console.error("Failed to load exam details", e);
    } finally {
      setExamLoading(false);
    }
  };

  const handleExamSubmit = async (answers: Record<string, string>, timeSpentSeconds: number) => {
    if (!activeExam) return;
    setExamLoading(true);
    try {
      const res = await fetch(`/api/v1/exam/${activeExam.exam_id}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers, time_spent_seconds: timeSpentSeconds }),
      });
      if (res.ok) {
        const resultData = await res.json();
        setActiveResult(resultData);
        setActiveExam(null);
      }
    } catch (e) {
      console.error("Failed to submit exam", e);
    } finally {
      setExamLoading(false);
    }
  };

  if (activeResult) {
    return (
      <ExamResultViewer
        result={activeResult}
        onDone={() => {
          setActiveResult(null);
          fetchExams();
        }}
        onRetakeMissed={(missedIds) => {
          if (!activeResult) return;
          loadExam(activeResult.exam_id);
        }}
      />
    );
  }

  if (activeExam) {
    return (
      <ExamRunner
        exam={activeExam}
        onSubmit={handleExamSubmit}
        onExit={() => setActiveExam(null)}
      />
    );
  }

  return (
    <div className="mx-auto max-w-5xl p-6">
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4 border-b pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-600 dark:text-blue-400">
            <GraduationCap size={16} /> Autonomous Exam System
          </div>
          <h1 className="mt-1 text-3xl font-extrabold text-gray-900 dark:text-gray-100">
            Exam Mode
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Generate grounded multiple-choice exams directly from your knowledge base materials.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow hover:bg-blue-700"
        >
          <Plus size={16} /> Create New Exam
        </button>
      </div>

      {loading || examLoading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 size={32} className="animate-spin text-blue-600" />
          <p className="mt-3 text-sm text-gray-500">Loading exams...</p>
        </div>
      ) : exams.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-gray-300 p-12 text-center dark:border-gray-800">
          <GraduationCap size={44} className="mx-auto text-gray-400" />
          <h3 className="mt-3 text-lg font-bold">No exams created yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            Pick a knowledge base and topic to generate your first rigorous practice exam.
          </p>
          <button
            type="button"
            onClick={() => setIsModalOpen(true)}
            className="mt-5 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700"
          >
            <Plus size={16} /> Generate First Exam
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {exams.map((ex) => (
            <div
              key={ex.exam_id}
              className="flex flex-col justify-between rounded-2xl border bg-white p-5 shadow-sm transition hover:shadow-md dark:bg-gray-900"
            >
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">{ex.title}</h3>
                <p className="mt-1 line-clamp-1 text-xs text-gray-500 dark:text-gray-400">
                  Topic: {ex.topic}
                </p>

                <div className="mt-4 flex flex-wrap gap-2 text-xs text-gray-600 dark:text-gray-400">
                  <span className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2 py-1 dark:bg-gray-800">
                    <BookOpen size={12} /> {ex.num_questions} Questions
                  </span>
                  {ex.time_limit_minutes && (
                    <span className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2 py-1 dark:bg-gray-800">
                      <Clock size={12} /> {ex.time_limit_minutes} Mins
                    </span>
                  )}
                </div>
              </div>

              <div className="mt-6 border-t pt-4">
                <button
                  type="button"
                  onClick={() => loadExam(ex.exam_id)}
                  className="inline-flex w-full items-center justify-center gap-1.5 rounded-xl bg-blue-50 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-100 dark:bg-blue-950/40 dark:text-blue-300 dark:hover:bg-blue-950/60"
                >
                  Start Exam <ArrowRight size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <ExamGeneratorModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onGenerated={(newExamId) => {
          fetchExams();
          loadExam(newExamId);
        }}
      />
    </div>
  );
}
