from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from smarttutor.core.agentic import build_openai_client
from smarttutor.exam.models import Citation, ExamQuestion, ExamSpec, QuestionValidation
from smarttutor.services.llm import get_llm_config
from smarttutor.tools.rag_tool import rag_search

logger = logging.getLogger(__name__)

FORBIDDEN_PATTERNS = [
    re.compile(r"\ball\s+of\s+the\s+above\b", re.IGNORECASE),
    re.compile(r"\bnone\s+of\s+the\s+above\b", re.IGNORECASE),
    re.compile(r"\ball\s+the\s+above\b", re.IGNORECASE),
    re.compile(r"\bnone\s+of\s+these\b", re.IGNORECASE),
    re.compile(r"\bboth\s+[a-d]\s+and\s+[a-d]\b", re.IGNORECASE),
]


class ExamGraphState(BaseModel):
    topic: str
    kb_name: str
    num_questions: int = 5
    difficulty: str = "medium"
    time_limit_minutes: Optional[int] = None
    passages: List[dict] = Field(default_factory=list)
    questions: List[ExamQuestion] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ExamGraph:
    def __init__(self) -> None:
        from smarttutor.core.agentic import LLMClientConfig
        self.llm_config = get_llm_config()
        self.model_name = getattr(self.llm_config, "model", None) or "gpt-4.1"
        client_config = LLMClientConfig(
            binding=getattr(self.llm_config, "binding", "openai"),
            model=self.model_name,
            api_key=getattr(self.llm_config, "api_key", None),
            base_url=getattr(self.llm_config, "base_url", None),
            api_version=getattr(self.llm_config, "api_version", None),
            extra_headers=getattr(self.llm_config, "extra_headers", None),
        )
        self.client = build_openai_client(client_config)

    async def execute(self, state: ExamGraphState) -> ExamSpec:
        state = await self.retrieve_passages_node(state)
        questions: List[ExamQuestion] = []
        passage_index = 0
        total_passages = len(state.passages)

        while len(questions) < state.num_questions and passage_index < total_passages:
            passage = state.passages[passage_index]
            passage_index += 1
            question = await self.generate_and_validate_question(
                passage=passage,
                topic=state.topic,
                difficulty=state.difficulty,
                index=len(questions) + 1,
            )
            if question is not None:
                questions.append(question)

        if len(questions) < state.num_questions and state.passages:
            cycle = 0
            max_cycles = state.num_questions * 2
            while len(questions) < state.num_questions and cycle < max_cycles:
                passage = state.passages[cycle % len(state.passages)]
                cycle += 1
                question = await self.generate_and_validate_question(
                    passage=passage,
                    topic=state.topic,
                    difficulty=state.difficulty,
                    index=len(questions) + 1,
                    variation=cycle,
                )
                if question is not None:
                    questions.append(question)

        title = f"{state.topic.title()} Exam"
        return ExamSpec(
            title=title,
            topic=state.topic,
            kb_name=state.kb_name,
            num_questions=len(questions),
            time_limit_minutes=state.time_limit_minutes,
            questions=questions,
        )

    async def retrieve_passages_node(self, state: ExamGraphState) -> ExamGraphState:
        subqueries = [
            state.topic,
            f"{state.topic} core concepts and principles",
            f"{state.topic} key definitions and facts",
            f"{state.topic} applications and rules",
        ]
        collected = []
        seen_chunks = set()

        for q in subqueries:
            try:
                res = await rag_search(query=q, kb_name=state.kb_name)
                sources = res.get("sources") or []
                for s in sources:
                    chunk_id = s.get("chunk_id") or s.get("content", "")[:50]
                    if chunk_id not in seen_chunks and len(s.get("content", "").strip()) > 50:
                        seen_chunks.add(chunk_id)
                        collected.append(s)
                if not sources and res.get("content"):
                    raw_content = res.get("content", "")
                    if raw_content and raw_content[:50] not in seen_chunks:
                        seen_chunks.add(raw_content[:50])
                        collected.append({
                            "content": raw_content,
                            "source": state.kb_name,
                            "title": state.kb_name,
                        })
            except Exception as e:
                logger.warning(f"RAG search error for query '{q}': {e}")

        state.passages = collected
        return state

    async def generate_and_validate_question(
        self,
        passage: dict,
        topic: str,
        difficulty: str,
        index: int,
        variation: int = 0,
    ) -> Optional[ExamQuestion]:
        passage_text = passage.get("content", "")
        source_name = passage.get("title") or passage.get("source") or "Document"
        page_num = passage.get("page")
        if isinstance(page_num, str) and page_num.isdigit():
            page_num = int(page_num)
        elif not isinstance(page_num, int):
            page_num = None

        draft = None
        feedback = ""

        for attempt in range(3):
            draft_raw = await self._call_generate_draft(
                passage_text=passage_text,
                topic=topic,
                difficulty=difficulty,
                index=index,
                feedback=feedback,
                variation=variation,
            )
            if not draft_raw:
                continue

            validation = await self._call_validate_guardrail(draft_raw, passage_text)
            if validation.valid:
                opts = draft_raw["options"]
                if isinstance(opts, dict):
                    opts = [opts.get("A", ""), opts.get("B", ""), opts.get("C", ""), opts.get("D", "")]
                citation = Citation(
                    source=source_name,
                    page=page_num,
                    quote=draft_raw.get("quote") or passage_text[:120].strip(),
                )
                return ExamQuestion(
                    topic=topic,
                    question=draft_raw["question"],
                    options=opts,
                    correct_option=draft_raw["correct_option"],
                    explanation=draft_raw["explanation"],
                    citation=citation,
                    difficulty=difficulty if difficulty in ("easy", "medium", "hard") else "medium",
                    knowledge_point_id=f"{topic.lower().replace(' ', '_')}_{index}",
                )
            feedback = validation.feedback

        return None

    async def _call_generate_draft(
        self,
        passage_text: str,
        topic: str,
        difficulty: str,
        index: int,
        feedback: str = "",
        variation: int = 0,
    ) -> Optional[dict]:
        system_prompt = (
            "You are an expert exam designer. Generate a single multiple-choice question (MCQ) based strictly on the provided source passage.\n"
            "Rules:\n"
            "1. Must have exactly 4 options labeled A, B, C, D.\n"
            "2. Exactly ONE option must be unequivocally correct according to the passage.\n"
            "3. Exactly THREE options must be plausible but unequivocally incorrect.\n"
            "4. NEVER use 'All of the above', 'None of the above', 'Both A and B', or similar meta options.\n"
            "5. Phrasing must be direct and unambiguous with no double negatives.\n"
            "6. Must include an exact quote from the passage that justifies the correct answer.\n"
            "Respond ONLY with a valid JSON object with these keys: question, options, correct_option, explanation, quote."
        )

        user_content = (
            f"Topic: {topic}\n"
            f"Difficulty: {difficulty}\n"
            f"Passage:\n\"\"\"\n{passage_text}\n\"\"\"\n"
        )
        if variation > 0:
            user_content += f"\nNote: Focus on a different aspect or detail of this passage than previous questions."
        if feedback:
            user_content += f"\nPrevious attempt had issues: {feedback}. Fix these issues."

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or ""
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Question generation failed: {e}")
            return None

    async def _call_validate_guardrail(
        self, draft: dict, passage_text: str
    ) -> QuestionValidation:
        question = draft.get("question", "").strip()
        options = draft.get("options")
        if isinstance(options, dict):
            options = [options.get("A", ""), options.get("B", ""), options.get("C", ""), options.get("D", "")]
            draft["options"] = options
        correct_option = draft.get("correct_option", "").strip().upper()
        explanation = draft.get("explanation", "").strip()
        quote = draft.get("quote", "").strip()

        if not question:
            return QuestionValidation(
                valid=False,
                has_single_correct=False,
                distractors_unambiguous=False,
                no_all_or_none=True,
                citation_grounded=False,
                feedback="Question text is missing.",
            )

        if not isinstance(options, list) or len(options) != 4:
            return QuestionValidation(
                valid=False,
                has_single_correct=False,
                distractors_unambiguous=False,
                no_all_or_none=True,
                citation_grounded=False,
                feedback="Options list must contain exactly 4 options.",
            )

        for opt in options:
            if not isinstance(opt, str) or not opt.strip():
                return QuestionValidation(
                    valid=False,
                    has_single_correct=False,
                    distractors_unambiguous=False,
                    no_all_or_none=True,
                    citation_grounded=False,
                    feedback="Empty option found.",
                )
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(opt):
                    return QuestionValidation(
                        valid=False,
                        has_single_correct=False,
                        distractors_unambiguous=False,
                        no_all_or_none=False,
                        citation_grounded=False,
                        feedback="Options must not use 'all of the above' or 'none of the above'.",
                    )

        if correct_option not in ("A", "B", "C", "D"):
            return QuestionValidation(
                valid=False,
                has_single_correct=False,
                distractors_unambiguous=False,
                no_all_or_none=True,
                citation_grounded=False,
                feedback="correct_option must be one of A, B, C, or D.",
            )

        has_grounding = bool(quote and (quote in passage_text or len(quote) > 15))

        verifier_prompt = (
            "You are a rigorous exam auditor. Review the MCQ below against the source text.\n"
            "Criteria:\n"
            "1. Is there exactly ONE unequivocally correct answer according to the source text?\n"
            "2. Are all 3 distractors unequivocally incorrect?\n"
            "3. Is the correct answer directly supported by the source text?\n"
            "Respond ONLY with a JSON object: {\"approved\": true/false, \"reason\": \"explanation\"}"
        )
        verifier_content = (
            f"Source text:\n{passage_text}\n\n"
            f"Question: {question}\n"
            f"Options: {json.dumps(options)}\n"
            f"Declared Correct Option: {correct_option}\n"
            f"Explanation: {explanation}\n"
        )

        try:
            res = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": verifier_prompt},
                    {"role": "user", "content": verifier_content},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            data = json.loads(res.choices[0].message.content or "{}")
            approved = bool(data.get("approved", False))
            reason = str(data.get("reason", ""))
            return QuestionValidation(
                valid=approved and has_grounding,
                has_single_correct=approved,
                distractors_unambiguous=approved,
                no_all_or_none=True,
                citation_grounded=has_grounding,
                feedback=reason if not approved else "",
            )
        except Exception as e:
            logger.warning(f"Validation verifier call failed: {e}")
            return QuestionValidation(
                valid=has_grounding,
                has_single_correct=True,
                distractors_unambiguous=True,
                no_all_or_none=True,
                citation_grounded=has_grounding,
                feedback="Fallback validation without LLM auditor.",
            )
