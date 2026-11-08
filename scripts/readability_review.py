"""Approximate reading-grade screening, not a validated accessibility assessment.

Uses a documented vowel-group syllable heuristic and Flesch-Kincaid formula.
Technical identifiers and source citations make whole-report grades unreliable.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml
from clinicshield import reader_guidance
from clinicshield.fix_first import PLAN_NOTICE
from clinicshield.practice_scoring import NOTICE


def syllables(word):
    word = word.lower()
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and not word.endswith(("le", "ye")) and count > 1:
        count -= 1
    return max(1, count)


def screen(text):
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)
    sentences = max(1, len(re.findall(r"[.!?]+(?:\s|$)", text)))
    grade = .39 * len(words) / sentences + 11.8 * sum(map(syllables, words)) / max(1,len(words)) - 15.59
    return round(max(0,grade),1)


def review():
    items = [(name, getattr(reader_guidance,name)) for name in
             ("PRIVACY_NOTICE","SCORE_GUIDE","SCOPE_NOTICE","PRIORITY_GUIDE","TABLE_GUIDE")]
    items += [("Fix First guidance",PLAN_NOTICE),("Practice guidance",NOTICE)]
    for q in json.loads((ROOT/"clinicshield/checklist_questions.json").read_text(encoding="utf-8")):
        items.append((q["id"]+" question and explanation",q["question"]+" "+q["explanation"]+" "+q["why"]))
    for path in sorted((ROOT/"rules").glob("*.yaml")):
        rule=yaml.safe_load(path.read_text(encoding="utf-8"))
        items.append((rule["rule_id"]+" recommended action",rule["fix"]))
    return [{"text":name,"estimated_grade":screen(text),"screen":"at or below 8" if screen(text)<=8 else "needs review"} for name,text in items]


if __name__ == "__main__":
    print(json.dumps(review(),indent=2))
