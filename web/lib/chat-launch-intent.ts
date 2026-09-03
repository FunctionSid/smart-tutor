/**
 * The `/home` launch-URL contract — both ends in one place.
 *
 * Other surfaces (the Mastery Path dashboard, capability shortcuts) open a
 * chat by navigating to `/home` with query parameters that say how the
 * composer should be set up before the learner types anything. Building and
 * reading that URL are two halves of one contract, so they live together and
 * are covered by a round-trip test.
 *
 * Parsing is deliberately dependency-free: tool names are returned verbatim
 * and validated by the caller against its own tool registry.
 */

/** Composer setup requested by the URL that opened `/home`. */
export interface ChatLaunchIntent {
  /** Capability to activate. `""` means plain chat; `null` means unspecified. */
  capability: string | null;
  /** Raw `tool` values — the caller filters these against its registry. */
  tools: string[];
  /** Knowledge bases to attach to the opened chat. */
  knowledgeBases: string[];
  /** Persistent mastery path this conversation should operate on. */
  masteryPathId: string | null;
  /** Existing reader material to open before the first turn. */
  readerMaterialId: string | null;
}

const EMPTY_INTENT: ChatLaunchIntent = {
  capability: null,
  tools: [],
  knowledgeBases: [],
  masteryPathId: null,
  readerMaterialId: null,
};

/** Read the launch intent out of a `location.search` string. */
export function readChatLaunchIntent(search: string): ChatLaunchIntent {
  if (!search) return { ...EMPTY_INTENT };
  const params = new URLSearchParams(search);
  const capability = params.get("capability");
  return {
    capability: capability === null ? null : capability.trim(),
    tools: params.getAll("tool").map((tool) => tool.trim()),
    knowledgeBases: params
      .getAll("kb")
      .map((kb) => kb.trim())
      .filter(Boolean),
    masteryPathId: params.get("mastery_path_id")?.trim() || null,
    readerMaterialId: params.get("reader_material_id")?.trim() || null,
  };
}

/** Build a fresh chat URL associated with existing persistent mastery state. */
export function newMasteryPathChatUrl(masteryPathId: string): string {
  const params = new URLSearchParams({
    capability: "mastery_path",
    mastery_path_id: masteryPathId,
  });
  return `/home?${params.toString()}`;
}

/** Build a Tutor URL that opens a reader material and attaches its source KB. */
export function newReaderChatUrl(params: {
  materialId: string;
  knowledgeBase?: string;
}): string {
  const search = new URLSearchParams({
    capability: "immersive_reading",
    reader_material_id: params.materialId,
  });
  if (params.knowledgeBase?.trim()) search.append("kb", params.knowledgeBase.trim());
  return `/home?${search.toString()}`;
}
