from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Child:
    id: int
    name: str
    age: int
    diagnosis_date: str
    strengths: Optional[str]
    challenges: Optional[str]

@dataclass
class Behavior:
    id: int
    child_id: int
    behavior_type: str
    frequency: int
    triggers: Optional[str]
    context: Optional[str]
    date: str

@dataclass
class Interest:
    id: int
    child_id: int
    interest_type: str
    intensity: int
    duration: int
    impact: Optional[str]

@dataclass
class Assessment:
    id: int
    child_id: int
    assessment_type: str
    results: str
    date: str
    notes: Optional[str]

@dataclass
class ProgressRecord:
    id: int
    child_id: int
    metric: str
    value: float
    date: str
    notes: Optional[str]

@dataclass
class Recommendation:
    id: int
    child_id: int
    recommendation_type: str
    content: str
    ai_generated: bool