# Periodic Adverse Drug Experience Report (PADER) - simplified
**Product:** Bisoprolol fumarate  
**Reporting period:** 2024-07-01 to 2025-06-30  
**Report type:** PADER (spec v0.1.0)  
**Regulatory basis:** Adapted from 21 CFR 314.80 periodic reporting; ICH E2D terminology.

> Prototype output. Every figure below is computed in Python from the source line listing; narrative text is model-drafted from those figures only and is marked with the evidence ids it cites.

## 1. Reporting Period and Report Scope
_Review status: **APPROVED**_

This Periodic Adverse Drug Experience Report covers the reporting period from 2024-07-01 to 2025-06-30 for Bisoprolol fumarate [E:reporting_period]. The dataset consists of 1067 data rows representing 1024 unique individual case safety reports [E:total_cases]. Data validation identified 30 cases with unknown sex, which constitutes a limitation in field completeness [E:data_quality].

**Data validation findings** `[E:data_quality]`

| level | check | count |
| --- | --- | --- |
| warning | rows_unknown_sex | 30 |

## 2. Narrative Summary and Analysis
_Review status: **FLAGGED**_ — Auto-check: '5%' threshold not present in evidence; rewrite without an invented cut-off.

During the reporting period from 2024-07-01 to 2025-06-30, a total of 1024 individual case safety reports were identified [E:total_cases, E:reporting_period]. Analysis of case seriousness shows that 1023 cases (99.9%) were classified as serious, while 1 case (0.1%) was classified as non-serious [E:seriousness_split]. The most frequently reported reactions by MedDRA Preferred Term were Hypotension (150 cases, 14.6%), Bradycardia (129 cases, 12.6%), Dizziness (107 cases, 10.4%), and Acute kidney injury (105 cases, 10.3%) [E:top_reactions]. Other reactions reported in more than 5% of cases included Fatigue (8.5%), Dyspnoea (6.0%), and Syncope (5.9%) [E:top_reactions]. Additional reported reactions included Atrioventricular block (4.5%), Drug ineffective (4.1%), and Bronchospasm (3.9%) [E:top_reactions].

**Serious vs non-serious cases** `[E:seriousness_split]`

| seriousness | cases | pct |
| --- | --- | --- |
| serious | 1023 | 99.9 |
| non-serious | 1 | 0.1 |

**Most frequently reported reactions (MedDRA PT, top 10)** `[E:top_reactions]`

| reaction | cases | pct of cases |
| --- | --- | --- |
| Hypotension | 150 | 14.6 |
| Bradycardia | 129 | 12.6 |
| Dizziness | 107 | 10.4 |
| Acute kidney injury | 105 | 10.3 |
| Fatigue | 87 | 8.5 |
| Dyspnoea | 61 | 6.0 |
| Syncope | 60 | 5.9 |
| Atrioventricular block | 46 | 4.5 |
| Drug ineffective | 42 | 4.1 |
| Bronchospasm | 40 | 3.9 |

**Automated grounding checks:**
- `error` ungrounded_number: 5
- `info` evidence_not_cited: total_cases, reporting_period

## 3. Summary Analysis of Cases
_Review status: **APPROVED**_

During the reporting period, a total of 1024 individual case safety reports were identified [E:total_cases]. The patient population had a median age of 68.0 years, with ages ranging from 22.0 to 99.0 years [E:age_summary]. Distribution by age band showed that the 45-64 group accounted for 374 cases (36.5%), followed by the 75+ group with 315 cases (30.8%), the 65-74 group with 295 cases (28.8%), and the 18-44 group with 40 cases (3.9%) [E:by_age_band]. Females represented 53.4% (547 cases) of the total, males represented 43.7% (447 cases), and 2.9% (30 cases) were of unknown sex [E:by_sex]. The three leading countries of occurrence were the United States with 416 cases (40.6%), the United Kingdom with 132 cases (12.9%), and Germany with 102 cases (10.0%) [E:by_country].

**Cases by age group** `[E:by_age_band]`

| age band | cases | pct |
| --- | --- | --- |
| 45-64 | 374 | 36.5 |
| 75+ | 315 | 30.8 |
| 65-74 | 295 | 28.8 |
| 18-44 | 40 | 3.9 |

**Cases by sex** `[E:by_sex]`

| sex | cases | pct |
| --- | --- | --- |
| female | 547 | 53.4 |
| male | 447 | 43.7 |
| unknown | 30 | 2.9 |

**Cases by country of occurrence** `[E:by_country]`

| country | cases | pct |
| --- | --- | --- |
| united states | 416 | 40.6 |
| united kingdom | 132 | 12.9 |
| germany | 102 | 10.0 |
| france | 97 | 9.5 |
| italy | 68 | 6.6 |
| canada | 64 | 6.2 |
| japan | 62 | 6.1 |
| spain | 48 | 4.7 |
| australia | 35 | 3.4 |

## 4. Reaction / Adverse Event Analysis
_Review status: **APPROVED**_

The most frequently reported reactions during this period were Hypotension (150 cases, 14.6%), Bradycardia (129 cases, 12.6%), and Dizziness (107 cases, 10.4%) [E:top_reactions]. The reaction profile for serious cases is identical in composition and ranking for the top four terms, comprising Hypotension (150 cases), Bradycardia (129 cases), Dizziness (107 cases), and Acute kidney injury (105 cases) [E:top_serious_reactions]. Minor numerical differences exist in the serious case counts for Fatigue (86 cases) and Dyspnoea (60 cases) compared to the overall dataset [E:top_reactions, E:top_serious_reactions]. Regarding clinical outcomes, 367 cases (35.8%) were reported as recovered/resolved, while 165 cases (16.1%) were not recovered/not resolved [E:outcomes]. Fatal outcomes were reported in 78 cases, representing 7.6% of the total [E:outcomes]. The dataset does not support a conclusion regarding the benefit-risk profile or causality.

**Most frequently reported reactions in serious cases (top 10)** `[E:top_serious_reactions]`

| reaction | serious cases |
| --- | --- |
| Hypotension | 150 |
| Bradycardia | 129 |
| Dizziness | 107 |
| Acute kidney injury | 105 |
| Fatigue | 86 |
| Dyspnoea | 60 |
| Syncope | 60 |
| Atrioventricular block | 46 |
| Drug ineffective | 42 |
| Bronchospasm | 40 |

**Reported reaction outcomes (case level, first reaction)** `[E:outcomes]`

| outcome | cases | pct |
| --- | --- | --- |
| recovered/resolved | 367 | 35.8 |
| unknown | 235 | 22.9 |
| not recovered/not resolved | 165 | 16.1 |
| recovering/resolving | 132 | 12.9 |
| fatal | 78 | 7.6 |
| recovered/resolved with sequelae | 47 | 4.6 |

## 5. Serious Cases and 15-Day Alert Reports
_Review status: **APPROVED**_

During the reporting period, 1,023 cases were classified as serious, representing 99.9% of the total case volume [E:seriousness_split]. Among these serious cases, 524 involved hospitalisation, 80 were life-threatening, and 85 met the criterion for death [E:seriousness_criteria]. The total number of cases with a fatal outcome or death seriousness criterion was 85 [E:fatal_cases]. These regulatory seriousness criteria are not mutually exclusive, and a single case may meet multiple criteria [E:seriousness_criteria]. Expedited 15-day reportability cannot be determined from this dataset because it contains no listedness/expectedness or submission-date fields. The most frequently reported reactions in serious cases were hypotension (150 cases), bradycardia (129 cases), and dizziness (107 cases) [E:top_serious_reactions].

**Serious cases by regulatory seriousness criterion** `[E:seriousness_criteria]`

| criterion | cases |
| --- | --- |
| death | 85 |
| life-threatening | 80 |
| hospitalisation | 524 |

## 6. Trends and Important Observations
_Review status: **APPROVED**_

Monthly case reporting fluctuated throughout the period, beginning with 82 cases in July 2024 and reaching a minimum of 56 cases in August 2024 [E:monthly_trend]. A peak of 118 cases was recorded in June 2025 [E:monthly_trend]. The second half of the reporting period (January 2025 to June 2025) contained 616 cases, representing a 51.0% increase compared to the 408 cases received during the first half (July 2024 to December 2024) [E:monthly_trend]. These figures represent reporting frequency observations only. The dataset does not support a conclusion regarding changes in the product risk profile, as interpreting these trends would require patient exposure and denominator data which are not present in the provided evidence.

**Cases received per calendar month** `[E:monthly_trend]`

| month | cases |
| --- | --- |
| 2024-07 | 82 |
| 2024-08 | 56 |
| 2024-09 | 68 |
| 2024-10 | 61 |
| 2024-11 | 72 |
| 2024-12 | 69 |
| 2025-01 | 117 |
| 2025-02 | 101 |
| 2025-03 | 99 |
| 2025-04 | 91 |
| 2025-05 | 90 |
| 2025-06 | 118 |

**Automated grounding checks:**
- `info` evidence_not_cited: top_reactions, seriousness_split

## 7. History of Actions Taken
_Review status: **APPROVED**_

The source dataset contains no information regarding regulatory actions, label changes, or risk-communication records for the reporting period. Consequently, this section cannot be completed from the available data, as inputs such as label change history, regulatory correspondence, and risk management plan updates are required.

## 8. Case Index / Listing
_Review status: **APPROVED**_

A total of 1024 individual case safety reports were identified during the reporting period [E:total_cases]. The following index provides details for the first 25 cases by receipt date, including country, patient demographics, reaction, seriousness, and outcome [E:case_index]. The full listing of 1024 cases has been exported separately to case_index_full.csv [E:case_index].

**Case listing (first 25 of 1024 cases by receipt date)** `[E:case_index]`

| case id | receipt date | country | age | sex | reaction | seriousness | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10000337 | 2024-07-01 | france | 69 | female | Acute kidney injury | serious | not recovered/not resolved |
| 10005593 | 2024-07-01 | france | 54 | female | Bradycardia | serious | recovering/resolving |
| 10000073 | 2024-07-01 | italy | 51 | female | Acute kidney injury | serious | unknown |
| 10000808 | 2024-07-01 | spain | 69 | male | Bronchospasm | serious | recovering/resolving |
| 10006301 | 2024-07-02 | united states | 85 | female | Bradycardia | serious | fatal |
| 10007032 | 2024-07-04 | france | 76 | female | Dyspnoea | serious | not recovered/not resolved |
| 10004012 | 2024-07-04 | germany | 78 | male | Cardiac failure | serious | unknown |
| 10002366 | 2024-07-04 | united states | 50 | female | Hypotension | serious | fatal |
| 10000756 | 2024-07-04 | united states | 92 | female | Cardiac failure | serious | fatal |
| 10006771 | 2024-07-04 | united kingdom | 50 | unknown | Dyspnoea | serious | not recovered/not resolved |
| 10003165 | 2024-07-05 | japan | 54 | male | Acute kidney injury | serious | unknown |
| 10006066 | 2024-07-05 | france | 47 | male | Hypotension | serious | not recovered/not resolved |
| 10000379 | 2024-07-05 | france | 69 | male | Cerebral haemorrhage | serious | recovered/resolved |
| 10005023 | 2024-07-05 | united states | 65 | female | Bradycardia | serious | recovered/resolved |
| 10000238 | 2024-07-05 | united states | 52 | male | Cerebral haemorrhage | serious | recovering/resolving |
| 10003721 | 2024-07-05 | spain | 64 | male | Cardiac failure | serious | unknown |
| 10001750 | 2024-07-06 | australia | 68 | male | Acute kidney injury | serious | recovered/resolved |
| 10005636 | 2024-07-06 | united kingdom | 75 | female | Hyperkalaemia | serious | unknown |
| 10004823 | 2024-07-06 | united states | 64 | male | Dyspnoea | serious | unknown |
| 10002563 | 2024-07-06 | germany | 33 | female | Drug ineffective | serious | unknown |
| 10001586 | 2024-07-07 | united states | 82 | female | Cardiac failure | serious | recovering/resolving |
| 10002765 | 2024-07-07 | japan | 81 | female | Dyspnoea | serious | recovered/resolved with sequelae |
| 10004407 | 2024-07-07 | united states | 65 | male | Hypotension | serious | fatal |
| 10000570 | 2024-07-07 | france | 79 | female | Bradycardia | serious | recovered/resolved |
| 10004054 | 2024-07-08 | united states | 62 | female | Acute kidney injury | serious | fatal |

## Appendix A — Evidence register

Every evidence id cited above, with the exact computation behind it.

| evidence id | title | method (deterministic Python) | traced cases |
| --- | --- | --- | --- |
| reporting_period | Reporting period covered by the dataset | min/max of receiptdate across all rows (or configured override) | - |
| total_cases | Total individual case safety reports | count of unique safetyreportid values | 50 |
| data_quality | Data validation findings | field-completeness and duplication checks run at load time | - |
| seriousness_split | Serious vs non-serious cases | case-level count grouped by the `serious` field | 51 |
| top_reactions | Most frequently reported reactions (MedDRA PT, top 10) | unique case count per reaction preferred term across all reaction rows | 478 |
| by_age_band | Cases by age group | case-level count grouped by `age_band` | 190 |
| by_sex | Cases by sex | case-level count grouped by `sex` | 130 |
| by_country | Cases by country of occurrence | case-level count grouped by `country` | 433 |
| age_summary | Age distribution summary | median/min/max of patient_patientonsetage over cases with a recorded age | - |
| top_serious_reactions | Most frequently reported reactions in serious cases (top 10) | unique case count per reaction, restricted to rows where serious == serious | 478 |
| outcomes | Reported reaction outcomes (case level, first reaction) | case-level count grouped by `outcome` | 297 |
| seriousness_criteria | Serious cases by regulatory seriousness criterion | unique case count per ICH seriousness flag column (a case may meet several) | 150 |
| fatal_cases | Cases with a fatal outcome or death seriousness criterion | unique cases where seriousnessdeath == 1 or reaction outcome == fatal | 50 |
| monthly_trend | Cases received per calendar month | case-level count grouped by month of receiptdate | 600 |
| case_index | Case listing (first 25 of 1024 cases by receipt date) | case-level rows sorted by receiptdate; full listing exported separately | - |

## Appendix B — Provenance

| key | value |
| --- | --- |
| source_file | Bisoprolol_icsr_sample_1068rows.csv |
| sha256 | 41a7d6cd3f467ebfd8ad884b00307110c95f07d8a8e815382f5404d1daa1e8bb |
| rows | 1067 |
| unique_cases | 1024 |
| report_spec | PADER v0.1.0 |
| spec_sha256 | c3c9e45a0d67b5a1 |
| model | google/gemini-3-flash-preview |
| generated_at | 2026-08-16T13:55:10+00:00 |
| pipeline_version | 0.1.0 |
