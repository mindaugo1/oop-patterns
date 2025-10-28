import asyncio

from dotenv import load_dotenv

from llm_client import OpenAIClient
from agents import TeamManager, GeneratorAgent, ReflectorAgent, CuratorAgent
from models import AgentNames

load_dotenv()
client = OpenAIClient()

MESSAGES = [
    {
        "role": "user",
        "content": (
            "Write a Python function avg_numbers(data: list[str]) -> float that returns "
            "the average of the numeric items in the list."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "def avg_numbers(data: list[str]) -> float:\n"
            "    total = 0\n"
            "    for x in data:\n"
            "        total += x\n"
            "    return round(total / len(data), 2)"
        ),
    },
    {
        "role": "user",
        "content": (
            "I ran your code and it failed.\n\n"
            "E TypeError: unsupported operand type(s) for +=: 'int' and 'str'\n"
            "Failing test: avg_numbers(['1','2','x']) == 1.5\n"
            "Additional check failed: empty input -> expected 0.0\n\n"
            "Please fix the function."
        ),
    },
]


async def main():
    # --------------------------------PLAYBOOK--------------------------------
    playbook = [
        {
            "id": "001 double check a password when loging to hostinger",
            "content": "double check a password when loging to hostinger",
        },
        {
            "id": "002 check a weather",
            "content": "check a weather in the next 7 days",
        },
        {
            "id": "003 formulas_and_calculations",
            "content": "Calculate the average by summing all successfully converted numeric values and dividing by their count, then round the result to two decimal places.",
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
