# Evidence snapshot — checked 2026-11-06, America/New_York

This is background, not an exhaustive algorithm or fixed policy database. Recheck current primary sources when requirements matter. Separate vendor claims, independent studies and subjective observations.

## Detection

- Turnitin FAQ: context-based sentence scores, thresholded aggregation, not explicit single-metric perplexity/burstiness rules. Score is not actual author contribution. https://guides.turnitin.com/hc/en-us/articles/28477544839821-Turnitin-s-AI-writing-detection-capabilities-FAQs
- Turnitin report guide: qualifying prose, 1–19% shown as `*%`, errors possible, no sole-basis adverse decisions; minimum 300 words of long-form prose. https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report
- Turnitin releases: bypasser detection added August 2025; English model updated October 2026. https://guides.turnitin.com/hc/en-us/articles/28294949544717-AI-writing-detection-model
- GPTZero's displayed score describes classification confidence, not a sentence share; it is not convertible to Turnitin. https://support.gptzero.me/articles/4965048546-how-do-i-interpret-a-gptzero-result

## Independent research

- Liang et al. (2023): non-native writing bias in seven then-current tools and a small sample, not a current Turnitin error estimate. https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961/
- Dugan et al. (2024), RAID: sensitivity to models, domains and generation settings in tested versions. https://aclanthology.org/2024.acl-long.674/
- Dugan et al. (2025): strong detection when domains/models were represented during training; avoid claiming detectors are useless. https://aclanthology.org/2025.genaidetect-1.45/
- Park et al. (2026): professional editing changed different detectors' scores in different directions; public methods, not Turnitin. https://aclanthology.org/2026.emnlp-industry.109/
- Mitchell et al. (2023), DetectGPT: perturbation/probability curvature method, not Turnitin's known implementation. https://proceedings.mlr.press/v202/mitchell23a.html
- Kirchenbauer et al. (2023): watermark detection requires corresponding generation scheme, not a universal mark in all AI text. https://proceedings.mlr.press/v202/kirchenbauer23a.html

## Human review and proposals

- University of Minnesota: content/source/voice issues can warrant investigation; style alone usually does not substantiate misuse. https://wac.umn.edu/teaching-writing/teaching-resources/what-should-i-do-about-genai/identifying-and-responding
- NUS CDE proposal guide: methods, data, feasibility, contribution and specific supervisor fit. Do not infer another programme's required template. https://cde.nus.edu.sg/graduate/graduate-programmes-by-research-how-to-write-a-research-proposal/
- Wikipedia community guide: descriptive context-dependent observations, not validated detection or a universal word blacklist. https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing

## Dated application examples

- HKU Graduate School requires disclosure of AI uses including ideas, retrieval and language editing. https://gradsch.hku.hk/prospective_students/application/supporting_documents
- UChicago Arts & Humanities prohibits generative AI production of application materials. Do not generalize to every programme or the user's past correspondence. https://ahd.uchicago.edu/admissions/admissions-process/how-apply

No policy or detector outcome follows from a country label. No predicted Turnitin percentage follows from these sources.
