"use client";

import { useTranslation } from "react-i18next";

import { ServiceConfigEditor } from "@/components/settings/ServiceConfigEditor";
import { SettingsPageHeader } from "@/components/settings/shared";

export default function EmbeddingSettingsPage() {
  const { t } = useTranslation();
  return (
    <div>
      <SettingsPageHeader
        title={t("Embedding Model")}
        description={t(
          "Configure the model that makes documents searchable for RAG. This stays separate from the AI/Tutor model that generates answers.",
        )}
      />
      <ServiceConfigEditor service="embedding" />
    </div>
  );
}
