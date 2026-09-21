from pydantic import BaseModel, Field, AliasChoices, model_validator
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

    @model_validator(mode='after')
    def check_not_empty(self):
        if not self.semantic and not self.episodic and not self.procedural and not self.active:
            raise ValueError("Graph cannot be completely empty")
        return self

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
    semantic_memory: SemanticMemoryV1 = Field(default_factory=SemanticMemoryV1, validation_alias=AliasChoices('semantic_memory', 'Semantic_Memory', 'Semantic', 'semantic'))
    episodic_ledger: EpisodicLedgerV1 = Field(default_factory=EpisodicLedgerV1, validation_alias=AliasChoices('episodic_ledger', 'Episodic_Ledger', 'Episodic', 'episodic'))
    procedural_memory: ProceduralMemoryV1 = Field(default_factory=ProceduralMemoryV1, validation_alias=AliasChoices('procedural_memory', 'Procedural_Memory', 'Procedural', 'procedural'))
    active_state: ActiveStateV1 = Field(default_factory=ActiveStateV1, validation_alias=AliasChoices('active_state', 'Active_State', 'Active', 'active'))

    @model_validator(mode='after')
    def check_not_empty(self):
        v1 = self.semantic_memory
        v2 = self.episodic_ledger
        v3 = self.procedural_memory
        v4 = self.active_state
        if not v1.nodes and not v1.edges and not v2.events and not v2.decisions and not v3.instructions and not v4.current_goal:
            raise ValueError("Graph cannot be completely empty")
        return self
