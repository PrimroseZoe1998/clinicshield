# Sampled text contrast and PDF usability review

Reviewed November 16, 2026. Bounded evidence, not WCAG conformance certification.

## Method

Read computed styles from the actual hosted Results DOM in its Streamlit iframe,
not colors from the laptop photographs. The observed view displayed 80 overall,
72.3 Safeguards and 91 Exposure; this measurement did not rerun or assert the
documented 65-point Lakeview scenario. Exact hosted source SHA was not recorded.

Contrast uses WCAG relative luminance: linearize each sRGB channel (divide by
12.92 below 0.04045; otherwise ((c+0.055)/1.055)^2.4), weight channels
0.2126/0.7152/0.0722, then divide (lighter+0.05) by (darker+0.05).
Transparent backgrounds and caption opacity are composited onto the observed
opaque background before calculation. No gradients or extra opacity layers
were present on these samples. Displayed ratios are rounded for reporting;
threshold comparisons use unrounded values.

[W3C SC 1.4.3 guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
sets 4.5:1 for ordinary text, 3:1 for qualifying large text. Button labels observed
at 14–16 CSS pixels use the ordinary-text threshold. This does not assess focus
indicators, non-text contrast, tables rendered on canvas or every interaction state.

## Observed default-state Results samples

| Sample | Foreground | Background | Ratio | Ordinary text threshold |
| --- | --- | --- | ---: | --- |
| Body/heading text | rgb(250,250,250) | rgb(14,17,23) | 18.11:1 | Pass |
| Muted score explanation | rgb(250,250,250), ancestor opacity 0.6 | rgb(14,17,23) | 6.94:1 | Pass |
| Provisional warning | rgb(255,255,194) | rgba(255,255,18,0.2) over rgb(14,17,23) | 10.35:1 | Pass |
| Secondary Back label | rgb(250,250,250) | rgb(19,23,32) | 17.18:1 | Pass |
| Primary Continue to Fix First label | rgb(255,255,255) | rgb(255,75,75) | 3.30:1 | Below 4.5:1 |

The user's visual readability check did not reveal the primary-label issue;
the computed color measurement did. Severity/status text was present in the
observed accessibility tree, including High and Needs review, independent of color.

## Implemented correction, hosted verification pending

The bundled static `clinicshield/accessibility.css` darkens enabled primary
buttons only: #b42318 with white text, calculated **6.57:1**. Hover #912018 and
active #711a13 are darker, maintaining the same text color. Existing focus
styling and disabled controls are not replaced. The selector uses the observed
stBaseButton-primary test ID rather than generated class names. It must be
rechecked when Streamlit changes its DOM. Other theme colors remain unchanged.

The fixed stylesheet is loaded using st.html from an application-owned path.
It contains no uploaded content, interpolation, scripts or external resources;
JavaScript execution remains disabled. See [Streamlit documentation](https://docs.streamlit.io/develop/api-reference/text/st.html).

42 UI/upload tests and six container-layout tests passed; medium/high Bandit
and diff checks passed. A first container-test attempt hit the sandbox temp-path
permission problem; rerunning with an explicit writable path passed. The local
Streamlit process started, but browser access timed out, so no computed-style or
visual verification of the revised local button is claimed. No full-suite rerun
was performed for this styling-only change. After deployment, measure the
button's actual foreground/background, including hover/focus/active states.

## PDF and visual checks reported by the owner

The owner confirmed that a downloaded Lakeview PDF allowed text selection/copy,
had readable summary/appendix layout, and opened a tested source link. A supplied
photograph shows its 65/100 At risk summary with provisional limitations. This
does not demonstrate every page/link, structural reading order, tagged PDF,
PDF/UA conformance or screen-reader compatibility.

The owner also reported that app warnings, muted explanations and buttons were
clear, with written severity/status labels. Prior keyboard and 200% zoom evidence
is recorded in [verification](week-6-verification.md). Full accessibility coverage
and the combined issue checkbox remain open pending appropriate scope disposition.

## Hosted verification after owner reboot

The owner reported green CI for 6e33526, then rebooted Community Cloud because
the previous imported UI still rendered the old color after a browser refresh.
After reboot, the agent read the actual Continue to Upload button styles:
white text on rgb(180,35,24), opacity 1, bundled stylesheet present. The default
text contrast is **6.57428861557707:1**. A subsequent keyboard input focused the
button without activating it: :focus and :focus-visible were true, the text and
background remained unchanged, and a 3.2px rgba(255,75,75,0.5) focus shadow was
present. A screenshot shows the focused button. This confirms default/focused
text contrast and the presence of a focus treatment, not focus-indicator area or
contrast conformance. Hover and pressed-state rendered colors remain unmeasured.
Exact hosted checkout SHA was not captured in this check.

## Read-only inspection of committed sample PDFs

The committed samples were inspected with pypdf without rewriting them:

| Sample | Pages | StructTreeRoot | MarkInfo/Marked | Document Lang | Embedded URI link annotations |
| --- | ---: | --- | --- | --- | ---: |
| Lakeview | 37 | Absent | Not marked | Absent | 0 |
| Southside | 34 | Absent | Not marked | Absent | 0 |
| Westside | 72 | Absent | Not marked | Absent | 0 |

All had extractable first-page text and a document title. These historical
artifacts are untagged; copying text does not establish semantic reading order.
The report generator source also sets a title but declares no document language
or semantic tagging. A link opening in the owner's viewer may be viewer URL
detection; it is not evidence of embedded accessible link annotations in these
committed files. No screen-reader run or complete page-order audit was performed.

This is now a known PDF structure gap, not simply an unknown tagging status.
The existing readable text export provides another format but is not asserted to
be a formally validated equivalent. Gate 3 must decide whether tagged PDFs are
required before the prototype candidate; no exception is approved here. No PDF
was edited or regenerated during this inspection.
