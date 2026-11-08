# Plain-language and reading-level review

Reviewed November 8, 2026. Core app/report guidance, 25 checklist entries and
24 recommended actions were edited for shorter sentences and familiar words.
A shared word guide defines file types, score terms and recurring acronyms before
the detailed app/report sections. Status text and reference IDs remain readable
without color. Scoring inputs, weights, severities, evidence and mappings did not
change. All non-fix fields of every rule were compared with HEAD and are identical.

## Method and limits

Run `.venv/Scripts/python.exe scripts/readability_review.py` from the repository.
The screen uses Flesch-Kincaid's formula (0.39 words/sentences + 11.8
syllables/words - 15.59) with an approximate vowel-group syllable count. It is a
local regression aid, not a validated reading-age or comprehension assessment.
Names, acronyms and short technical phrases can skew estimates.

All 56 selected prose blocks screen at grade 8 or below. This does not establish
that every displayed string meets grade 8: source titles, raw evidence keys,
identifiers, arithmetic, file-format syntax, rule titles and detailed technical
reference rationales retain their exact terms. Some may need expert help. The
formal legal/framework names are expanded in the word guide rather than renamed.
These exceptions remain explicit; the brief's literal all-text target is not
independently demonstrated by this screen. A timed first-time-user check and
human comprehension review remain pending before full Week 5 acceptance.

## Meaning retained

- Unknown evidence still requires review and does not prove safety.
- No unsupported risk-reduction, compliance or production-readiness claim is added.
- Q24 still has two follow-ups and is scored once; Q23 applicability is unchanged.
- Rule recommendations retain vendor coordination, evidence checks, conditional
  actions, operational continuity and limits on legal/breach conclusions.
- Fix First still uses finding points/effort; caps and overlap can affect score gains.
- Draft practice mappings stay draft; missing components stay unassessed.

The app checklist is now a plain-language rendering of the criteria in
`docs/checklist.md`; the detailed source wording is retained there. New wording
changes presentation only, not question IDs, weights or Yes/No/Unknown semantics.

## Screening results

| Text | Estimated grade |
| --- | ---: |
| PRIVACY_NOTICE | 5.0 |
| SCORE_GUIDE | 5.4 |
| SCOPE_NOTICE | 4.6 |
| PRIORITY_GUIDE | 3.6 |
| TABLE_GUIDE | 4.5 |
| Fix First guidance | 5.9 |
| Practice guidance | 8.0 |
| Q01 question and explanation | 6.3 |
| Q02 question and explanation | 7.6 |
| Q03 question and explanation | 7.7 |
| Q04 question and explanation | 7.2 |
| Q05 question and explanation | 6.4 |
| Q06 question and explanation | 5.3 |
| Q07 question and explanation | 7.0 |
| Q08 question and explanation | 5.9 |
| Q09 question and explanation | 4.8 |
| Q10 question and explanation | 7.3 |
| Q11 question and explanation | 5.8 |
| Q12 question and explanation | 7.9 |
| Q13 question and explanation | 6.4 |
| Q14 question and explanation | 5.7 |
| Q15 question and explanation | 7.4 |
| Q16 question and explanation | 6.3 |
| Q17 question and explanation | 7.0 |
| Q18 question and explanation | 7.3 |
| Q19 question and explanation | 5.9 |
| Q20 question and explanation | 6.0 |
| Q21 question and explanation | 7.6 |
| Q22 question and explanation | 6.4 |
| Q23 question and explanation | 7.5 |
| Q24 question and explanation | 6.2 |
| Q25 question and explanation | 6.3 |
| R01 recommended action | 5.7 |
| R02 recommended action | 4.0 |
| R03 recommended action | 6.0 |
| R04 recommended action | 6.0 |
| R05 recommended action | 6.7 |
| R06 recommended action | 5.7 |
| R07 recommended action | 5.2 |
| R08 recommended action | 7.4 |
| R09 recommended action | 4.7 |
| R10 recommended action | 6.2 |
| R11 recommended action | 7.0 |
| R12 recommended action | 7.0 |
| R13 recommended action | 6.3 |
| R14 recommended action | 5.2 |
| R15 recommended action | 6.9 |
| R16 recommended action | 4.5 |
| R17 recommended action | 6.4 |
| R18 recommended action | 5.4 |
| R19 recommended action | 4.5 |
| R20 recommended action | 4.1 |
| R21 recommended action | 4.4 |
| R22 recommended action | 3.8 |
| R23 recommended action | 4.7 |
| R24 recommended action | 5.9 |

## Verification

The three original scenario scores remain 65/82/80. Tests check guidance in
reports, term definitions before detail, selected-prose screening and existing
rule/scoring/UI/export behavior. PDF samples are regenerated and rendered for
visual review; browser confirmation and fresh GitHub CI are not inferred.

Local validation: 2,558 tests passed with no exclusions. After a final page-break
spacing adjustment, all eight PDF/guidance tests passed again. The three latest
sample PDFs were rendered and visually reviewed, with one owner-summary page
and a complete appendix each. Changed-file medium/high Bandit and diff checks
passed. All 24 rules retain identical non-fix fields compared with HEAD.


November 8 manual check: the user supplied a screenshot of the expanded word
guide in the app and confirmed the updated assessment PDF owner summary and
appendix after the sample workflow. This verifies the exercised display/download
path. It does not constitute an independent reading-age assessment or the timed
first-time-user benchmark. Fresh GitHub CI remains pending for this increment.
