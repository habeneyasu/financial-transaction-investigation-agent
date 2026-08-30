from typing import Literal

from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    """Input for starting an investigation."""

    case_id: str = Field(
        ...,
        description="Investigation case ID",
    )


class InvestigationFinding(BaseModel):
    """Evidence-based finding from an investigation."""

    description: str = Field(
        ...,
        description="Clear description of the investigation finding.",
    )

    evidence: list[str] = Field(
        default_factory=list,
        description="Specific evidence supporting the finding.",
    )


class InvestigationResult(BaseModel):
    """Final structured result of an investigation."""

    case_id: str

    findings: list[InvestigationFinding] = Field(
        default_factory=list,
    )

    conclusion: str = Field(
        ...,
        description="Overall evidence-based investigation conclusion.",
    )

    confidence: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        ...,
        description="Confidence level based on the available evidence.",
    )