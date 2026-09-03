"use client";

import { useTranslation } from "react-i18next";

import { ServiceConfigEditor } from "@/components/settings/ServiceConfigEditor";
import { SettingsPageHeader } from "@/components/settings/shared";

export default function SttSettingsPage() {
  const { t } = useTranslation();
  return (
    <div>
      <SettingsPageHeader
        title={t("Speech-to-Text")}
        description={t(
          "Transcribe the chat composer's microphone recordings. Use global faster-whisper where available, or an OpenAI-compatible speech provider.",
        )}
      />
      <ServiceConfigEditor service="stt" />
    </div>
  );
}
