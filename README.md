\
# Does Oral Sex Count? — Reproducibility Materials

Code, source-statistic transcriptions, numerical reconstructions and six figures accompanying a methodological critique of Date Psychology’s June 2023 article, [“Does Oral Sex Count As Having Sex?”](https://datepsychology.com/does-oral-sex-count-as-having-sex/).

**Scope and limitation.** This is a **published-summary reconstruction**, not an independent replication of Alexander’s participant-level survey. No participant-level observations, questionnaire source file or original analysis code from Alexander's survey are provided here. Neither the original Den Haese–King student records nor the Natsal/YouGov respondent-level datasets are included. We reproduce checks and figures that can be supported by published aggregate figures. Contradictory original numbers are deliberately **not silently repaired**.

## Repository files

| File | Purpose |
| --- | --- |
| `reproduce_oral_sex_figures.py` | Recomputes results from the CSV inputs, prints summary statistics, writes `reconstruction_results.txt`, and regenerates six PNG charts. |
| `datepsych_2023_reported.csv` | Published counts, means, SDs and correlations transcribed from Alexander’s essay. Includes notes flagging incompatible statements. |
| `den_haese_king_2022.csv` | No–Yes / Yes–Yes group summaries, exactly as published. |
| `den_haese_king_2022_sample.csv` | Study-wide denominators and original inferential statistics. |
| `gnambs_kaspar_2015_table5.csv` | Published meta-analysis subgroup effect ratios and *log-scale* confidence endpoints. |
| `natsal_2019.csv` | Selected published Natsal-3 percentages and partner-count results. |
| `yougov_2023_page1.csv` | Weighted response percentages from the original YouGov PDF table, including unplotted categories. |
| `source_index.csv` | Links and precise sections/tables for each source. |
| `reconstruction_results.txt` | Checked-in reference output of the computation script. |
| `figure_1_original_groups.png` … `figure_6_yougov_age.png` | Generated illustrations corresponding to the six figures in the companion review. |
| `tests/test_reconstruction.py` | Automated checks for key counts, inferential reconstructions, confidence intervals and CSV transcriptions. |
| `requirements.txt` | Runtime Python packages. |
| `LIMITATIONS.md` | Boundaries of what can be reproduced, ambiguities and statistical assumptions. |

## Reproduce everything

Install Python **3.10 or later**. From the repository root:

```bash
python -m pip install -r requirements.txt
python reproduce_oral_sex_figures.py
python -m unittest discover -s tests -v
```

The reproduction command writes all six PNG files and `reconstruction_results.txt` into this folder, overwriting existing copies. It requires no network access once dependencies have been installed. It reads the checked-in CSV inputs; it does **not** download or alter the published studies. Run it in a working copy if preserving the checked-in reference outputs matters.

## Figure-to-source mapping

| Companion figure | Reproduced material | Source / method |
| --- | --- | --- |
| **Figure 1** — Original study's two groups | No–Yes **14.99** (`n=77`) and Yes–Yes **11.47** (`n=30`) on the 0–33 Marlowe–Crowne scale | Den Haese & King (2022), Table 1. Scores are reported means, not raw-data re-estimates. |
| **Figure 2** — Contradictory count scenarios | Women **12/181** and men **33/447**, **45/447**, or **57/447**; two-sided Fisher exact *p* for each | Date Psychology (2023). These are **three mutually incompatible hypothetical reconciliations**, not three observed datasets. |
| **Figure 3** — Correlation uncertainty | Overall `r=-.02, n=628`; women `r=-.11, n=181`; approximate Fisher-*z* 95% confidence intervals | Date Psychology (2023), published rounded correlations. Assumes each correlation uses the stated full sample size; missing-data counts were not separately supplied. |
| **Figure 4** — Survey administration | Relative affirmative-reporting estimates **1.19**, **1.17**, **1.29**, **1.14**, **1.07**, with CIs exponentiated from published *log* limits | Gnambs & Kaspar (2015), Table 5. The authors label these ORs, but their method computes `p_computer / p_paper` (prevalence ratios). |
| **Figure 5** — Excluding oral-only partners | **33.1%** men, **23.4%** women | Mitchell et al. (2019), Results subsection “Gendered difference in what counts as a partner.” Survey-weighted reports, not reconstructed respondent data. |
| **Figure 6** — Meaning of oral stimulation of the penis | Age-specific yes/no answers: **28/52**, **36/51**, **56/30**, **56/28** (% yes/% no) | YouGov (2023), p. 1, table headed “Oral stimulation of the penis.” Other response categories are omitted from the bar plot but retained in the CSV. |

**Presentation note:** These newly generated PNGs reproduce the underlying quantities and figure concepts. Small layout and typographic differences from images previously pasted into Substack are not material to the calculations. Figure 1 uses the full scale's 0–33 axis to avoid exaggerating differences.

## Additional numerical checks

The script verifies and reports:

- The mutually exclusive category counts **140 + 57 + 443 = 640**, which exceed the reported `n=628` by **12**.
- If 57 respondents include 12 women, the implied number of men is **45**, or **10.1%** of 447—not the stated **12.7%**. The 12.7% value corresponds approximately to **57** men.
- If the other two categories and overall `n=628` were correct, the third category would contain **45** respondents, implying **33** men after subtracting the 12 women.
- Fisher's exact test results for **all three hypothetical scenarios**. A *p* value near .025 arises **only** under the 57-men scenario.
- A bound on the **maximum possible sample SD** with `n=12` and range `1–3` of `sqrt(12/11) ≈ 1.044`, making the reported women's SD **1.45** impossible under those constraints.
- The weighted mean implied by **12 women at 2.1** and **45 men at 2.2** is approximately **2.18**, not **2.12**; this depends on the 45-men interpretation and uses rounded subgroup means.
- The original female sample count implied by `1155 * .746 ≈ 862`; **65/862 ≈ 7.5%** of all female participants. This is **not** the share among sexually experienced women, whose exact gender-specific denominator cannot be recovered.
- The approximate Fisher-*z* intervals for the two plotted correlations.
- An explicit check that YouGov's **total** table says **45% yes / 41% no** for oral stimulation of the penis, despite the accompanying YouGov prose reversing those categories. The chart uses table values.

## Statistical and interpretive limitations

See [LIMITATIONS.md](LIMITATIONS.md). Most importantly, no gender-comparison *p* value is an inferential result of a known consistent dataset; the candidates are **illustrations of the consequences of contradictory numbers**. A null correlation with the Marlowe–Crowne scale does not validate individual reports, and neither paper identifies the magnitude of deliberate partner-count underreporting.

## Primary sources

- Date Psychology (2023), [“Does Oral Sex Count As Having Sex?”](https://datepsychology.com/does-oral-sex-count-as-having-sex/)
- Den Haese & King (2022), [*Oral-Genital Contact and the Meaning of ‘Had Sex’*](https://pmc.ncbi.nlm.nih.gov/articles/PMC8917100/), Table 1.
- Gnambs & Kaspar (2015), [*Disclosure of Sensitive Behaviors Across Self-Administered Survey Modes*](https://doi.org/10.3758/s13428-014-0533-4), Table 5.
- Mitchell et al. (2019), [*Why Do Men Report More Opposite-Sex Sexual Partners Than Women?*](https://pmc.ncbi.nlm.nih.gov/articles/PMC6326215/), results and Table 1.
- YouGov (2023), [*What counts as sex?*](https://d3nkl3psvxxpe9.cloudfront.net/documents/YouGov_-_What_counts_as_sex.pdf), p. 1.

No copyrighted journal PDFs, copies of webpages, or respondent-level records are redistributed. Data files here are manually transcribed summaries, with explicit provenance; they are not new empirical observations.

