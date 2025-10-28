from __future__ import annotations
from typing import List, Dict, Literal, Any
from enum import Enum

from pydantic import BaseModel


class AgentNames(Enum):
    GENERATOR = "Generator"
    REFLECTOR = "Reflector"
    CURATOR = "Curator"


class Query(BaseModel):
    text: str


class GeneratorResponse(BaseModel):
    reasoning: str
    bullet_ids: List[str]
    final_answer: str


class ReflectorResponse(BaseModel):
    reasoning: str
    error_identification: str
    root_cause_analysis: str
    correct_approach: str
    key_insight: str
    bullet_tags: List[Dict[str, str]]


class Operation(BaseModel):
    type: Literal["ADD"]
    section: str
    content: str


class CuratorResponse(BaseModel):
    reasoning: str
    operations: List[Operation]


Context = Dict[str, Any]
