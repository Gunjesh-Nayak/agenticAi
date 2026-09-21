#we are creating graph and first thing to create is a state class which will hold the state of the graph and the nodes and edges in it.

import os
#1) typed DICT
from typing import TypedDict, List, Dict, Any
from rich import print

class State(TypedDict):
    topic:str
    summary:str
    score:int


#2)pydantic Approach
from pydantic import BaseModel, field_validator
class StateModel(BaseModel):
    topic: str
    summary: str=""
    score: int

    @field_validator("score")
    def validate_score(cls, value):
        if value < 0:
            raise ValueError("Score must be between 0 and 100")
        return value

#3) dataclass approach python

from dataclasses import dataclass, field
@dataclass
class State:
    topic:str
    summary:str=""
    score:int
    message=list[str]=field(default_factory=list)


#4) graph
from langgraph.graph import MessagesState
class State(MessagesState):
    user_name:str
    language:str