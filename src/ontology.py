from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class Provenance(BaseModel):
    source_turn: int
    confidence: str
    status: Optional[str] = None
    reason: Optional[str] = None  # Used for rejected branches

class Node(BaseModel):
    node_id: str
    concept: str
    provenance: Provenance

class Edge(BaseModel):
    source_id: str
    target_id: str
    edge_type: str  # supports, contradicts, temporal_after, refines

class SemanticMemory(BaseModel):
    nodes: List[Node] = []
    edges: List[Edge] = []
    rules: List[Dict[str, Any]] = []

class Event(BaseModel):
    event_id: str
    type: str  # e.g., branch_rejection, decision
    abandoned_path: Optional[str] = None
    causality: Optional[str] = None
    source_turn: int
    overrides_node: Optional[str] = None

class EpisodicLedger(BaseModel):
    events: List[Event] = []

class ProceduralInstruction(BaseModel):
    instruction: str
    priority: str
    source_turn: Optional[int] = None

class ProceduralMemory(BaseModel):
    instructions: List[ProceduralInstruction] = []

class ActiveState(BaseModel):
    current_micro_goal: str
    pending_blockers: List[str] = []
    active_branches: List[str] = []
    next_immediate_action: Optional[str] = None

class Asset(BaseModel):
    asset_id: str
    type: str
    description: str
    path_or_payload: str

class ExtractionGraph(BaseModel):
    semantic_memory: SemanticMemory = Field(default_factory=SemanticMemory)
    episodic_ledger: EpisodicLedger = Field(default_factory=EpisodicLedger)
    procedural_memory: ProceduralMemory = Field(default_factory=ProceduralMemory)
    active_state: ActiveState = Field(default_factory=lambda: ActiveState(current_micro_goal=""))
    assets: List[Asset] = []
