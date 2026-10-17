from typing import Literal

from pydantic import BaseModel, Field

MasteryStatus = Literal["unknown", "needs_review", "demonstrated"]


class ConceptSummary(BaseModel):
    id: str
    name: str
    status: MasteryStatus = "unknown"
    explanation: str = ""


class GraphNode(BaseModel):
    id: str
    name: str
    status: MasteryStatus


class GraphEdge(BaseModel):
    source: str
    target: str
    type: Literal["REQUIRES"] = "REQUIRES"


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    target: str
    next_concept: str | None = None
    next_reason: str | None = None


class LearningStartRequest(BaseModel):
    student_id: str = Field(min_length=1, max_length=100)
    question: str = Field(default="", max_length=2000)
    target_concept_id: str | None = None


class DiagnoseRequest(BaseModel):
    student_id: str = Field(min_length=1, max_length=100)
    concept_id: str


class AnswerRequest(BaseModel):
    student_id: str = Field(min_length=1, max_length=100)
    concept_id: str
    answer: str = Field(min_length=1, max_length=10000)
    target_concept_id: str | None = None


class LearningNextRequest(BaseModel):
    student_id: str = Field(min_length=1, max_length=100)
    target_concept_id: str


class MasteryUpdateRequest(AnswerRequest):
    score: float = Field(ge=0, le=1)
    feedback: str = ""


class AnswerResponse(BaseModel):
    score: float
    feedback: str
    status: MasteryStatus
    next_concept: str

