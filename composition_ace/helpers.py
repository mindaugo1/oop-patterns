from collections import Counter
from models import AgentNames
from typing import List, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from agents import Agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_agent_counts(children: List["Agent"]) -> None:
    agent_counts = Counter(child.name for child in children)
    generator_count = agent_counts.get(AgentNames.GENERATOR.value, 0)
    reflector_count = agent_counts.get(AgentNames.REFLECTOR.value, 0)
    curator_count = agent_counts.get(AgentNames.CURATOR.value, 0)

    generator_responses = generator_count
    reflector_responses = reflector_count * generator_responses
    curator_responses = curator_count * reflector_responses

    logger.info(
        f"{generator_count} generator agents ({generator_responses} responses), "
        f"{reflector_count} reflector agents ({reflector_responses} responses), and "
        f"{curator_count} curator agents ({curator_responses} responses) would be created"
    )
