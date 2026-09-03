"""Built-in capability class paths."""

BUILTIN_CAPABILITY_CLASSES: dict[str, str] = {
    "chat": "smarttutor.agents.chat.capability:ChatCapability",
    "deep_solve": "smarttutor.capabilities.solve.capability:DeepSolveCapability",
    "deep_question": "smarttutor.agents.question.capability:DeepQuestionCapability",
    "deep_research": "smarttutor.agents.research.capability:DeepResearchCapability",
    "math_animator": "smarttutor.agents.math_animator.capability:MathAnimatorCapability",
    "visualize": "smarttutor.agents.visualize.capability:VisualizeCapability",
    "mastery_path": "smarttutor.capabilities.mastery.capability:MasteryPathCapability",
    "immersive_reading": "smarttutor.capabilities.reading.mode:ImmersiveReadingCapability",
}
