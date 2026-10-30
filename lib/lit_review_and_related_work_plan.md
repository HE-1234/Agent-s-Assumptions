# Systematic Literature Review & Positioning Blueprint for ACL

This report synthesizes findings from four parallel research tracks examining how **"I Know It's Wrong, But...": Why Language Models Defer to Context They Recognize as False** connects to prior and concurrent work (2021–2026). It includes:
1. **Audit of Your Current Citations** (fixing 1 mischaracterization and unpacking 5 severely undersold papers already in your `.bib`).
2. **High-Impact Missing Literature by Theme** (what to add to bridge the intellectual gaps in your story).
3. **Drop-In Rewrite of Section 2 (Related Work)** and surgical integration points for **Sections 1, 5, 6, and 7** (designed to eliminate redundancy between Sections 1 and 2 and respect ACL's 8-page main-body limit).
4. **Ready-to-Paste BibTeX Entries** for all recommended additions.

---

## 1. Audit of Papers Already Cited in Your Draft

Before adding new citations, the highest-leverage improvement is sharpening how you engage with the **14 primary papers (2023–2026) already in your bibliography**. Currently, several of your closest neighbors are cited only in passing parentheticals, leaving you open to reviewer pushback ("How does this differ from X?").

> [!CAUTION]
> **Immediate Fix — Mischaracterization of Xu et al. (2024) in Section 1 (Line 057):**
> In lines 055–057, you write: *"First, tests can include questions where the model holds weak prior beliefs. In those cases, deferring to context is a rational choice (Wu et al., 2024; Xu et al., 2024)."*
> **Why this is inaccurate:** **Xu et al. (2024)** (*"The earth is flat because..."*, ACL 2024 Outstanding Paper, FARM benchmark) explicitly screened for facts that models **already knew and answered correctly** in closed-book QA, and studied how multi-turn *persuasive rhetoric* (logical, credibility, and emotional appeals) erodes those strong beliefs.
> **Fix:** Remove `Xu et al., 2024` from line 057 (keep `Wu et al., 2024; Marjanović et al., 2024` there), and cite **Xu et al. (2024)** and **Xie et al. (2024)** two sentences later (line 060) where you discuss passages containing *elaborated or persuasive support*!

### Five Severely Undersold Papers Already in Your References

| Cited Paper | How It Is Currently Used | What It Actually Shows & How to Contrast It |
| :--- | :--- | :--- |
| **Sun et al. (2026)**<br>*Task Matters: Knowledge Requirements Shape LLM Responses to Context–Memory Conflict* (ACL Findings 2026) | Cited once in two words at the end of Section 2 (`task framing (Sun et al., 2026)`, line 214). | **What they showed:** Varying categorical task types (summarization vs. extraction vs. QA) changes context reliance, and *prompting models to generate rationales increases context reliance, actively harming tasks requiring parametric memory*.<br>**Your sharp contrast:** (1) Sun et al. vary task types externally; you show that *within a single neutral QA prompt*, models spontaneously experience internal task ambiguity in **99.8%** of defect-recognizing adopting traces. (2) You explain *why* their rationale-generation hurt parametric tasks: on bare assertions without formal steps to audit, CoT acts as an **objective amplifier** that rationalizes passage-reporting (52.4% $\rightarrow$ 54.1%), whereas pairing CoT with a truth-seeking criterion collapses adoption to **6.8%**. |
| **Li et al. (2026)**<br>*How LLMs Balance Internal Knowledge with User and Document Assertions* (ACL Findings 2026) | Dropped once in a generic parenthetical `(Longpre et al., 2021; Li et al., 2026)` (line 171). | **What they showed:** Evaluated 27 LLMs across internal memory, user assertions, and document assertions, finding a strict hierarchy (*Document > User > Parametric Memory*) reinforced by post-training, and concluding that models are *"impressionable, unable to effectively discriminate between helpful and harmful external information."*<br>**Your sharp contrast:** Directly challenge their conclusion! WarrantEval proves models **are** able to discriminate (97.6% rejection in standalone checks; 89.2% defect recognition inside QA traces). Post-training does not blind models to errors; it biases their **default answer criterion** toward treating documents as authoritative. |
| **Huang et al. (2025)**<br>*To Trust or Not to Trust? Situated Faithfulness* (ICLR 2025 Spotlight) | Cited once in passing as an example of context errors (line 160). | **What they showed:** Formalized *situated faithfulness* (calibrating trust by weighing internal confidence against context credibility) and proposed Self-Guided Confidence Reasoning (SCR).<br>**Your sharp contrast:** Huang et al. assume blind adoption stems from poorly calibrated confidence and that deliberation helps models weigh trust. WarrantEval isolates near-certain priors ($\min_r p_{\text{true}}^{(r)} > 0.90$) and shows that unguided deliberation **fails on bare assertions** (54.1% adoption) because models are not confused about *what is true*—they are confused about *whether the prompt wants truth or reading comprehension*. |
| **Zhou et al. (2023)**<br>*Context-faithful Prompting* (EMNLP Findings 2023) | Cited once alongside FaithEval for prioritizing context (line 155). | **What they showed:** Used opinion framing ("According to...") and *counterfactual few-shot demonstrations* to force models to suppress parametric memory and follow context.<br>**Your sharp contrast:** Connect this directly to **Section 6.2 (In-Context Demonstration Steering)**! You show the symmetric dual: 2-shot demonstrations act as pragmatic disambiguators of the latent answer criterion under a neutral instruction, swinging adoption up to **72.2%** (context-oriented) or down to **14.8%** (truth-oriented). |
| **Xie et al. (2024)**<br>*Adaptive Chameleon or Stubborn Sloth* (ICLR 2024 Spotlight) | Cited once in a generic cluster at line 046; completely absent from Section 2. | **What they showed:** Models act as "adaptive chameleons" when counterfactual context is coherent and elaborated, vs. "stubborn sloths" when context is fragmented.<br>**Your sharp contrast:** In WarrantEval's *Insufficient Evidence* condition, models still act as "chameleons" **52.4%–54.1%** of the time on *bare, one-sentence assertions* with zero elaboration, even while explicitly stating in their CoT trace that the assertion is false. |

---

## 2. High-Impact Missing Literature to Add (Across 4 Tracks)

To make your Related Work and Discussion read like a definitive ACL paper, we recommend weaving in **8–10 targeted citations** across three conceptual bridges that are currently missing.

### Bridge 1: Parametric Confidence, Option-Order Bias, and Epistemic Warrant
1. **Option-Order Sensitivity in MCQA:**
   * **Zheng et al. (ICLR 2024 Spotlight)** (*"Large Language Models are Not Robust Multiple Choice Selectors"*) and **Pezeshkpour & Hruschka (NAACL Findings 2024)** (*"Large Language Models Sensitivity to The Order of Options in Multiple-Choice Questions"*): Show that LLMs have strong token biases toward specific option letters and can swing 13–75% in accuracy across permutations when moderately uncertain.
   * *Why cite them:* They provide the exact methodological justification for your four-rotation screen ($\min_{r \in \{1..4\}} p_{\text{true}}^{(r)} > 0.90$).
2. **Surface Persuasiveness vs. Epistemic Warrant:**
   * **Wan et al. (ACL 2024)** (*"What Evidence Do Language Models Find Convincing?"*): Shows LLMs judge evidence persuasiveness via surface relevance/lexical overlap rather than human epistemic markers (citations, objective tone).
   * **Xu et al. (EMNLP 2024)** (*"Knowledge Conflicts for LLMs: A Survey"*): Provides the standard taxonomy of context–memory, inter-context, and intra-memory conflicts.

### Bridge 2: Test-Time Compute (CoT), Procedural Auditing vs. Rationalization, and the Generator–Verifier Gap
3. **Why CoT Helps Math/Logic Derivations but Not Bare Factual Claims:**
   * **Sprague et al. (ICLR 2025)** (*"To CoT or not to CoT? Chain-of-thought helps mainly on math and symbolic reasoning"*): Meta-analysis across 100+ papers showing CoT benefits almost exclusively symbolic/procedural execution steps, with near-zero gain on static factual recall.
   * *Why cite it:* Directly anchors your Section 5.2 split! On *Invalid Evidence* (Math/Logic) and *Inapplicable Evidence* (temporal mismatch), CoT has a formal derivation or date interval to audit; on *Insufficient Evidence* (bare factual assertion), there is no procedure to execute, so CoT turns into rationalization.
4. **CoT Rationalization & Pre-Commitment:**
   * **Turpin et al. (NeurIPS 2023)** (*"Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting"*) and **Lanham et al. (2023)** (*"Measuring Faithfulness in Chain-of-Thought Reasoning"*): Foundational works showing CoT often rationalizes prompt biases rather than computing truth from scratch.
   * **Chua & Evans (2025)** (*"Are DeepSeek R1 And Other Reasoning Models More Faithful?"*): Shows that Large Reasoning Models explicitly verbalize prompt cues/constraints in their `<think>` traces much more often than standard CoT models—aligning with your finding that 99.8% of adopting traces explicitly verbalize the passage-reporting hypothesis.
5. **The Generator–Verifier Gap & "Disclosure Failure":**
   * **Li et al. (ICLR 2024)** (*"Benchmarking and Improving Generator-Validator Consistency of Language Models"*) / **Saunders et al. (2022)**: Formalize why standalone verification ($97.6\%$ in your Section 5.3) diverges from generation.
   * **Huang et al. (ICLR 2024)** (*"Large Language Models Cannot Self-Correct Reasoning Yet"*) / **Kamoi et al. (TACL 2024)**: Show that intrinsic self-correction fails without an external verifier or explicit criterion.

### Bridge 3: Pragmatics, Comprehension Priors, and Implicit Bayesian Steering
6. **Pragmatic Accommodation vs. Epistemic Vigilance:**
   * **Grice (1975)** (*Logic and Conversation*) & **Sperber et al. (2010)** (*Epistemic Vigilance*, already cited in your Intro!): Under Grice's *Maxim of Relation*, supplying a `Context:` block creates a strong conversational implicature that the user wants the answer extracted from that text, clashing with the *Maxim of Quality* (truth).
   * **Cheng, Hawkins, & Jurafsky (ACL 2026)** (*"Accommodation and Epistemic Vigilance: A Pragmatic Account of Why LLMs Fail to Challenge Harmful Beliefs"*): Shows how pragmatic accommodation causes LLMs to accept false user presuppositions instead of exercising epistemic vigilance.
7. **Disentangling Context vs. Memory & Implicit Bayesian Inference in ICL:**
   * **Neeman et al. (ACL 2023)** (*"DisentQA: Disentangling Parametric and Contextual Knowledge with Counterfactual Question Answering"*) and **Bi et al. (ACL Findings 2025)** (*"Context-DPO: Aligning Language Models for Context-Faithfulness"*): Show how training paradigms either separate or aggressively penalize parametric truth ("stubbornness") in favor of context adherence.
   * **Xie et al. (ICLR 2022)** (*"An Explanation of In-context Learning as Implicit Bayesian Inference"*): Explains why your 2-shot demonstration intervention (Section 6.2) works—two examples suffice to collapse the model's posterior over the latent task criterion $\theta \in \{\text{Truth}, \text{Passage}\}$ without changing a single word of the instruction.

---

## 3. Concrete Blueprint & Drop-In Text for Your Draft

> [!IMPORTANT]
> **Page-Budget Note for ACL:**
> Your current draft reaches the end of the Conclusion at **line 651 on Page 9** (about 0.5 pages over the standard 8-page ACL main-body limit). By removing the repetitive explanation of the $\min_r p_{\text{true}}^{(r)} > 0.90$ screen from Section 2 (since it is already in Section 1 and Section 3.4), the revised Section 2 below packs **twice the scholarly depth in roughly the same column footprint**.

### A. Surgical Edits in Section 1 (Introduction, Lines 049–064)
Replace lines 049–064 with this tighter, accurately cited paragraph:

```latex
Existing benchmarks evaluate faulty-context adoption by presenting models with 
counterfactual passages and measuring how often answers flip \citep{longpre2021entity,liu2023recall,wu2024clasheval}. 
However, observing an answer change does not by itself establish a failure of epistemic vigilance, 
because standard evaluations conflate three distinct mechanisms. 
First, tests often include items where the model holds weak or unstable prior beliefs, 
making deference to external context rational \citep{wu2024clasheval,marjanovic2024dynamicqa}. 
Second, counterfactual passages are frequently constructed with coherent multi-sentence narratives 
or persuasive rhetoric \citep{xie2024adaptive,xu2024earth,wan2024what}, where belief revision can be 
partially warranted by the apparent quality of support. 
Third, even when a model recognizes a passage as unwarranted and false, standard prompts leave 
the \emph{answer criterion} underspecified---failing to distinguish whether the task evaluates 
real-world factuality or reading comprehension \citep{ming2025faitheval,sun2026task}.
```

### B. Complete Drop-In Rewrite for Section 2 (Related Work)

```latex
\section{Related Work}

\paragraph{The Grounding Dilemma and Situated Faithfulness.}
Grounded QA requires navigating a fundamental tension between \textbf{factual accuracy} 
(fidelity to real-world truth) and \textbf{contextual faithfulness} (adherence to supplied text; 
\citealp{neeman2023disentqa,ming2025faitheval}). Because RAG pipelines aim to curb hallucination, 
many prompting and alignment frameworks treat parametric knowledge as undesirable ``stubbornness,'' 
training or steering models to unconditionally follow counterfactual passages 
\citep{zhou2023context,bi2025contextdpo,ming2025faitheval}. 
Yet real-world retrieval frequently surfaces outdated, conflicting, or erroneous claims 
\citep{vu2024freshllms,hou2024wikicontradict,cattan2025dragged}. 
To reconcile these demands, \citet{huang2025situated} formalize \emph{situated faithfulness}, 
arguing that models should dynamically weigh internal confidence against external context quality. 
\textsc{WarrantEval} probes the exact boundary where contextual faithfulness becomes pathological: 
when the model possesses near-certain parametric knowledge and the passage offers no valid epistemic 
warrant to revise it.

\paragraph{Knowledge Conflicts, Parametric Certainty, and Epistemic Warrant.}
Extensive work shows that counterfactual context frequently overrides closed-book answers 
\citep{longpre2021entity,liu2023recall,xu2024knowledgeconflictsurvey}. 
However, prior benchmarks typically assess baseline knowledge via single-prompt greedy accuracy 
or unthresholded token probabilities \citep{wu2024clasheval,marjanovic2024dynamicqa}, 
which remain vulnerable to weak priors and multiple-choice positional biases 
\citep{zheng2024large,pezeshkpour2024large}. 
Moreover, prior studies largely manipulate surface persuasiveness---showing that coherent narratives 
\citep{xie2024adaptive}, rhetorical appeals \citep{xu2024earth}, or lexical overlap \citep{wan2024what} 
increase adoption. 
In contrast, \textsc{WarrantEval} enforces rotation-invariant parametric certainty ($\min_r p_{\text{true}}^{(r)} > 0.90$) 
and isolates three formal failures of epistemic warrant: step-by-step derivations with a single 
planted fallacy (\emph{invalid evidence}), future-anchored claims for historical queries 
(\emph{inapplicable evidence}, extending mutable-fact benchmarks like \citealp{vu2024freshllms}), 
and bare false assertions (\emph{insufficient evidence}).

\paragraph{Verification, Test-Time Reasoning, and Pragmatic Framing.}
Why do models adopt false context when prior certainty is high? 
Recent work attributes document deference to post-training impressionability or an inability to 
discriminate harmful context \citep{li2026how}, while studies of the generator--verifier gap show 
that models often succeed at standalone error detection \citep{chen2024benchmarking,peng2025misbench} 
yet fail to self-correct during generation \citep{saunders2022self,li2024gv,huang2024selfcorrect}. 
Concurrently, meta-analyses of Chain-of-Thought (CoT) show that test-time compute primarily aids 
symbolic and procedural execution rather than factual recall \citep{sprague2025cot}, and can 
rationalize prompt priors \citep{turpin2023language,chua2025faithful}. 
While \citet{marjanovic2026thoughtology} noted anecdotal DeepSeek-R1 traces that spot context errors 
before complying, we provide the first large-scale quantitative audit across 16,186 traces, 
demonstrating that defect recognition is maintained in 72.9\% of adopting responses. 
Bridging linguistic pragmatics \citep{grice1975logic,sperber2010epistemic,cheng2026accommodation} 
and task-requirement effects \citep{sun2026task}, we show that models infer a passage-reporting 
criterion from underspecified prompts, and that both explicit instructions and implicit few-shot 
demonstrations \citep{xie2022explanation,zhou2023context} systematically steer this criterion.
```

### C. Key Connections to Add in Sections 5, 6, and 7
* **Section 5.2 (Domain-Dependent Effects of Reasoning, ~line 390):** Cite **Sprague et al. (2025)** when explaining why test-time reasoning slashes adoption in Mathematics ($41.0\% \to 14.0\%$), Logic ($57.7\% \to 29.4\%$), and Time-Dependent dates ($41.8\% \to 8.7\%$), where there is a formal derivation or date interval to execute, but fails on Time-Invariant bare assertions ($52.4\% \to 54.1\%$).
* **Section 5.3 (Direct Passage Verification, ~line 415):** Contrast your $97.6\%$ standalone rejection rate directly with **Li et al. (2026)**'s claim that models are "unable to effectively discriminate" harmful document assertions, and connect to the generator–validator consistency gap (**Li et al., 2024; Peng et al., 2025**).
* **Section 6.1 & 6.2 (Interventions on the Answer Criterion, ~lines 488 & 525):**
  * In **Section 6.1**, connect to **Sun et al. (2026)** and **Huang et al. (2025)**: explain that Sun et al. observed rationale generation hurting parametric tasks because, under underspecified or context-heavy framing, CoT amplifies context compliance; pairing CoT with an explicit truth-seeking criterion reverses this dynamic ($35.8\% \to 6.8\%$).
  * In **Section 6.2**, cite **Zhou et al. (2023)** and **Xie et al. (2022)**: frame your 2-shot steering ($14.8\%$ vs. $72.2\%$) as implicit Bayesian inference over the latent answer criterion, showing that Zhou et al.'s counterfactual demonstrations work precisely by resolving pragmatic task ambiguity in favor of passage reporting.
* **Section 7.2 (The Faithfulness Dilemma in RAG Evaluation, ~line 595):** Cite **Ming et al. (2025) [FaithEval]** and **Bi et al. (2025) [Context-DPO]** alongside **Grice (1975)** / **Cheng et al. (2026)**: explain that because RAG training and reading-comprehension benchmarks penalize parametric truth as "stubbornness," supplying a `Context:` block pragmatically primes models to suspend epistemic vigilance unless the prompt explicitly requests factual truth.

---

## 4. Ready-to-Paste BibTeX for New Citations

```bibtex
@inproceedings{zheng2024large,
  title     = {Large Language Models are Not Robust Multiple Choice Selectors},
  author    = {Zheng, Chujie and Zhou, Hao and Meng, Fandong and Zhou, Jie and Huang, Minlie},
  booktitle = {The Twelfth International Conference on Learning Representations (ICLR 2024)},
  year      = {2024},
  url       = {https://openreview.net/forum?id=shr9PXzhrT}
}

@inproceedings{pezeshkpour2024large,
  title     = {Large Language Models Sensitivity to The Order of Options in Multiple-Choice Questions},
  author    = {Pezeshkpour, Pouya and Hruschka, Estevam},
  booktitle = {Findings of the Association for Computational Linguistics: NAACL 2024},
  pages     = {2019--2031},
  year      = {2024}
}

@inproceedings{wan2024what,
  title     = {What Evidence Do Language Models Find Convincing?},
  author    = {Wan, Alexander and Wallace, Eric and Klein, Dan},
  booktitle = {Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  pages     = {9099--9118},
  year      = {2024}
}

@inproceedings{xu2024knowledgeconflictsurvey,
  title     = {Knowledge Conflicts for {LLMs}: A Survey},
  author    = {Xu, Rongwu and Qi, Zehan and Guo, Zhijiang and Wang, Cunxiang and Wang, Hongru and Zhang, Yue and Xu, Wei},
  booktitle = {Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing (EMNLP 2024)},
  pages     = {8538--8556},
  year      = {2024}
}

@inproceedings{sprague2025cot,
  title     = {To {CoT} or not to {CoT}? Chain-of-thought helps mainly on math and symbolic reasoning},
  author    = {Sprague, Zayne and Yin, Fangcong and Rodriguez, Juan Diego and Jiang, Dongwei and Wadhwa, Manya and Singhal, Prasann and Zhao, Xinyu and Ye, Xi and Mahowald, Kyle and Durrett, Greg},
  booktitle = {The Thirteenth International Conference on Learning Representations (ICLR 2025)},
  year      = {2025},
  note      = {ArXiv:2409.12183}
}

@inproceedings{turpin2023language,
  title     = {Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting},
  author    = {Turpin, Miles and Michael, Julian and Perez, Ethan and Bowman, Samuel R.},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS 2023)},
  volume    = {36},
  pages     = {74952--74965},
  year      = {2023}
}

@inproceedings{li2024gv,
  title     = {Benchmarking and Improving Generator-Validator Consistency of Language Models},
  author    = {Li, Xiang Lisa and Shrivastava, Vaishnavi and Li, Siyan and Hashimoto, Tatsunori and Liang, Percy},
  booktitle = {The Twelfth International Conference on Learning Representations (ICLR 2024)},
  year      = {2024}
}

@inproceedings{huang2024selfcorrect,
  title     = {Large Language Models Cannot Self-Correct Reasoning Yet},
  author    = {Huang, Jie and Chen, Xinyun and Mishra, Swaroop and Zheng, Huaixiu Steven and Yu, Adams Wei and Song, Xinying and Zhou, Denny},
  booktitle = {The Twelfth International Conference on Learning Representations (ICLR 2024)},
  year      = {2024}
}

@inproceedings{neeman2023disentqa,
  title     = {{DisentQA}: Disentangling Parametric and Contextual Knowledge with Counterfactual Question Answering},
  author    = {Neeman, Ella and Aharoni, Roee and Honovich, Or and Choshen, Leshem and Szpektor, Idan and Abend, Omri},
  booktitle = {Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL 2023)},
  pages     = {10056--10070},
  year      = {2023}
}

@inproceedings{bi2025contextdpo,
  title     = {{Context-DPO}: Aligning Language Models for Context-Faithfulness},
  author    = {Bi, Baolong and Huang, Shaohan and Wang, Yiwei and Liu, Shenghua and Cheng, Xueqi},
  booktitle = {Findings of the Association for Computational Linguistics: ACL 2025},
  year      = {2025},
  note      = {ArXiv:2412.15280}
}

@inproceedings{cheng2026accommodation,
  title     = {Accommodation and Epistemic Vigilance: A Pragmatic Account of Why {LLMs} Fail to Challenge Harmful Beliefs},
  author    = {Cheng, Myra and Hawkins, Robert D. and Jurafsky, Dan},
  booktitle = {Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (ACL 2026)},
  year      = {2026},
  note      = {ArXiv:2601.04435}
}

@inproceedings{xie2022explanation,
  title     = {An Explanation of In-context Learning as Implicit {B}ayesian Inference},
  author    = {Xie, Sang Michael and Raghunathan, Aditi and Liang, Percy and Ma, Tengyu},
  booktitle = {The Tenth International Conference on Learning Representations (ICLR 2022)},
  year      = {2022}
}

@incollection{grice1975logic,
  title     = {Logic and Conversation},
  author    = {Grice, H. Paul},
  booktitle = {Syntax and Semantics, Vol. 3: Speech Acts},
  editor    = {Cole, Peter and Morgan, Jerry L.},
  pages     = {41--58},
  publisher = {Academic Press},
  year      = {1975}
}
```
