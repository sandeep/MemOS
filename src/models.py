from pydantic import BaseModel, Field, AliasChoices
from typing import List, Dict, Any

class Triple(BaseModel):
    subject: str
    relation: str
    object: str

class EpisodicTriple(Triple):
    step: int

class CognitiveGraphV2(BaseModel):
    semantic: List[Triple] = Field(validation_alias=AliasChoices('Semantic', 'semantic'))
    episodic: List[EpisodicTriple] = Field(validation_alias=AliasChoices('Episodic', 'episodic'))
    procedural: List[Triple] = Field(validation_alias=AliasChoices('Procedural', 'procedural'))
    active: List[Triple] = Field(validation_alias=AliasChoices('Active', 'active'))

class SemanticMemoryV1(BaseModel):
    nodes: List[Any] = Field(default_factory=list)
    edges: List[Any] = Field(default_factory=list)

class EpisodicLedgerV1(BaseModel):
    events: List[Any] = Field(default_factory=list)
    decisions: List[Any] = Field(default_factory=list)
    rejected_branches: List[Any] = Field(default_factory=list)

class ProceduralMemoryV1(BaseModel):
    instructions: List[Any] = Field(default_factory=list)

class ActiveStateV1(BaseModel):
    current_goal: str = ""
    blockers: List[str] = Field(default_factory=list)
    next_action: str = ""

class CognitiveGraphV1(BaseModel):
    semantic_memory: SemanticMemoryV1 = Field(default_factory=SemanticMemoryV1)
    episodic_ledger: EpisodicLedgerV1 = Field(default_factory=EpisodicLedgerV1)
    procedural_memory: ProceduralMemoryV1 = Field(default_factory=ProceduralMemoryV1)
    active_state: ActiveStateV1 = Field(default_factory=ActiveStateV1)
