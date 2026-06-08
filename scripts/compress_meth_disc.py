import re

with open('paper_draft.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Compress Methodology (Section 4)
methodology_start = text.find(r'\section{Methodology}')
methodology_end = text.find(r'\section{Results}')

if methodology_start != -1 and methodology_end != -1:
    condensed_methodology = r"""\section{Methodology}

\subsection{A/B Test Corpus}
We designed \textbf{23 base A/B scenarios} across three domains: UI/UX (8 tests), Copy/Messaging (7 tests), and Recommendation (8 tests). Each was grounded in UI components from real platforms (e.g., Shopee, Amazon, Spotify). For prompt-robustness analysis, five scenarios were rewritten in two additional prompt versions, yielding 33 evaluated test-case variants. The dataset comprises \textbf{30,179 API calls}.

\subsection{Models and Decoding}
We evaluated four LLMs: GPT-4o (OpenAI), Claude~3.5 Sonnet (Anthropic), Llama-3.3-70B (Meta), and DeepSeek-V4-Flash (DeepSeek). All models were queried at temperature 0.7, constrained to JSON structured outputs (\texttt{\{"choice": "A"\}}).

\subsection{Persona Construction}
Sixty personas were generated at three depth levels: Demographic (B3), Biographical (B4), and Interview-grounded (B5). Each demographic persona maps to a corresponding biographical and interview counterpart. Full texts are provided in the supplementary material.

\subsection{Counterbalancing and Prompt Robustness}
To eliminate position bias, each combination was run in both original order (Variant A first) and swapped order (Variant B first). To test prompt robustness, five representative test cases received two additional prompt versions (V2: shortened, V3: expanded).

\subsection{Statistical Analysis}
We employed Fleiss' $\kappa$~\cite{fleiss1971kappa} and Cohen's $\kappa$~\cite{cohen1960kappa} for inter-rater reliability, $C_{\text{intra}}$ for repeat stability, and mixed-effects logistic regression for variance-component decomposition~\cite{bates2015lme4, jaeger2008logit}.

\subsection{Human Reference Study}
\label{sec:human_study}
Eighty respondents evaluated all 23 scenarios. Choices were normalized to the semantic variant. Submissions under five minutes were discarded. The sample comprises 34 frequent, 38 occasional, and 8 infrequent online shoppers.

"""
    text = text[:methodology_start] + condensed_methodology + text[methodology_end:]

# 2. Compress Discussion & Limitations
discussion_start = text.find(r'\section{Discussion}')
discussion_end = text.find(r'\section*{Ethics statement}')

if discussion_start != -1 and discussion_end != -1:
    condensed_discussion = r"""\section{Discussion and Limitations}

The variance decomposition reveals that prompt wording accounts for the largest share of variance (41.2\%), surpassing the semantic design signal (32.2\%). Raw LLM A/B testing is fundamentally noisy, but CSUP successfully isolates the true semantic variance ($\sigma = 0.314$) by neutralizing order, model, and repetition bias.

SURS provides a test-case-level reliability decision, acting as a triage instrument rather than a universal claim of LLM validity. The human reference study confirms that SURS accurately identifies where humans themselves are divided. However, strong inter-model agreement does not necessarily imply agreement with human majorities, emphasizing the necessity of eventually grounding synthetic insights in real user behavior.

\textbf{Limitations:} All variants were represented as text descriptions rather than visual screenshots, which may inflate wording variance. The human reference study ($N=80$) is an external alignment pilot rather than a population-representative benchmark. The tests span only three domains, and model behavior is subject to drift over time. 

"""
    text = text[:discussion_start] + condensed_discussion + text[discussion_end:]

with open('paper_draft.md', 'w', encoding='utf-8') as f:
    f.write(text)
print("Successfully condensed Methodology and Discussion.")
