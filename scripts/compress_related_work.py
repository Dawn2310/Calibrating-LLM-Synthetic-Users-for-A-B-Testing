with open('paper_draft.md', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find(r'\section{Related Work}')
end_idx = text.find(r'\section{CSUP Framework}')

if start_idx != -1 and end_idx != -1:
    condensed_related_work = r"""\section{Related Work}

Recent research has explored Large Language Models (LLMs) as synthetic respondents and evaluators \cite{lu2025agentab, park2024generativeagents, aher2023simulate}. While studies show LLMs can replicate some human survey patterns \cite{park2024generativeagents}, others warn of systematic deviations \cite{gao2025caution}, failure to reproduce human response biases \cite{tjuatja2024biases}, and extreme sensitivity to prompt wording \cite{bisbee2024synthetic}. In A/B testing specifically, LLM agents have shown directional concordance with humans \cite{lu2025agentab, rieder2026simab}, but these systems focus on prediction accuracy rather than measurement reliability.

The fragility of raw LLM judgments is well-documented. Models exhibit systematic position bias, shifting their choices based solely on option ordering \cite{zheng2024mcqselectors, shi2025judging}. They are highly sensitive to meaning-preserving prompt variations \cite{sclar2024promptformatting, romanou2026brittlebench} and demonstrate internal drift across repeated runs even at zero temperature \cite{atil2025nondeterminism, tosato2025instability}. Furthermore, while persona prompting is commonly used to simulate diverse users, it does not reliably improve alignment and can introduce idiosyncratic variance \cite{morocho2026persona, hu2024persona, suhr2025personality}.

CSUP builds upon recent frameworks for variance decomposition in LLM evaluation \cite{kunievsky2025intent, haase2026withinmodel, wang2025allnoises, messing2026hidden}. While prior work has isolated prompt, model, and sampling noise in classification and creative tasks, CSUP applies this rigorous decomposition to A/B testing. By moving from the question "Can LLMs simulate users?" to "When are LLM judgments reliable enough to use?", CSUP establishes a calibrated measurement framework that explicitly controls for order, prompt, and sampling artifacts before reporting a result.

"""
    new_text = text[:start_idx] + condensed_related_work + text[end_idx:]
    with open('paper_draft.md', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Successfully condensed Related Work.")
else:
    print("Indices not found:", start_idx, end_idx)
