"use client";

import { useTranslation } from "react-i18next";

import { ServiceConfigEditor } from "@/components/settings/ServiceConfigEditor";
import { SettingsPageHeader } from "@/components/settings/shared";

export default function LlmSettingsPage() {
  const { t } = useTranslation();
  return (
    <div>
      <SettingsPageHeader
        title={t("AI / Tutor Model")}
        description={t(
          "Choose the answer-generating model for chat, Tutor, explanations, quizzes, practice, revision, and weak-topic help.",
        )}
      />
      <ServiceConfigEditor service="llm" />
    </div>
  );
}
