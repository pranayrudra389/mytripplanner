from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """The shared state that flow through the graph."""
    messages: Annotated[list, add_messages]
    preferences: dict
    planning_stage: str     # "gathering", "researching", "building", "reflecting", "presenting"
    research_count: int     # how many research cycles we've done
    revision_count: int     # how many itinerary revisions we've done
    itinerary_draft: str    # the current itinerary text
