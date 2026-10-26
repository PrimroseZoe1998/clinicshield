from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)


NonemptyText = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1),
]

Severity = Literal["Critical", "High", "Medium", "Low", "Info"]


class FrameworkReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    framework: NonemptyText
    reference: NonemptyText
    source: NonemptyText
    rationale: NonemptyText
    review_status: Literal["pending", "reviewed"]


class RuleDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    rule_id: str = Field(
        strict=True,
        pattern=r"^R(?:0[1-9]|1[0-9]|2[0-4])$",
    )
    title: NonemptyText
    kind: Literal["technical", "checklist"]
    handler: str = Field(
        strict=True,
        pattern=r"^[a-z][a-z0-9_]*$",
    )
    description: NonemptyText
    severity: Severity
    unknown_severity: Severity
    evidence_fields: tuple[NonemptyText, ...] = Field(min_length=1)
    fix: NonemptyText
    owner: NonemptyText
    effort: Literal[1, 2, 3]
    cost: Literal["none", "low", "budget_required", "unknown"]
    framework_references: tuple[FrameworkReference, ...] = Field(
        min_length=1
    )
    review_status: Literal["draft", "reviewed"]