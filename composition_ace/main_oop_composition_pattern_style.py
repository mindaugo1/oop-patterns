import asyncio

from dotenv import load_dotenv

from llm_client import OpenAIClient
from agents import TeamManager, GeneratorAgent, ReflectorAgent, CuratorAgent
from models import AgentNames

load_dotenv()
client = OpenAIClient()

MESSAGES = """
Write a Python function avg_numbers(data: list[str]) -> float that returns the average of the numeric items in the list. 
"""


async def main():
    # --------------------------------PLAYBOOK--------------------------------
    playbook = [
        {
            "id": "002 check a weather",
            "content": "check a weather in the next 7 days",
        },
        {
            "id": "003 formulas_and_calculations",
            "content": "Calculate the average by summing all successfully converted numeric values and dividing by their count",
        },
    ]
    team = TeamManager("ImprovementTeam")
    generator_agent = GeneratorAgent(AgentNames.GENERATOR.value, client)
    reflector_agent = ReflectorAgent(AgentNames.REFLECTOR.value, client)
    curator_agent = CuratorAgent(AgentNames.CURATOR.value, client)
    team.add_child(generator_agent)
    team.add_child(curator_agent)
    team.add_child(reflector_agent)

    result = await team.run(task={"query": MESSAGES, "playbook": playbook})
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
