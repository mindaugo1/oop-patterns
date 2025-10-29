import asyncio
import json

from dotenv import load_dotenv

from llm_client import OpenAIClient
from models import GeneratorResponse, ReflectorResponse, CuratorResponse
from prompts import Prompts

load_dotenv()
client = OpenAIClient()

MESSAGES = """
Write a Python function avg_numbers(data: list[str]) -> float that returns the average of the numeric items in the list. 
"""

REASONING = "The task is to write a Python function that calculates the average of numeric items in a list of strings. The approach involves iterating over each string in the list, attempting to convert it to a float, and if successful, including it in the sum and count for averaging. According to the playbook, the average is calculated by summing all successfully converted numeric values and dividing by their count. The function will handle conversion errors by skipping non-numeric strings. Finally, the function returns the average as a float"

BULLET_IDS = ["003 formulas_and_calculations"]

FINAL_ANSWER = "def avg_numbers(data: list[str]) -> float:\n    total = 0.0\n    count = 0\n    for item in data:\n        try:\n            num = float(item)\n            total += num\n            count += 1\n        except ValueError:\n            continue\n    if count == 0:\n        return 0.0\n    return total / len(data)"


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

    # --------------------------------GENERATOR--------------------------------
    generator_response = GeneratorResponse(
        reasoning=REASONING,
        bullet_ids=BULLET_IDS,
        final_answer=FINAL_ANSWER,
    )
    print(generator_response)

    # --------------------------------REFLECTOR--------------------------------
    reflector_prompt = Prompts().get_reflector_prompt(
        question=MESSAGES,
        reasoning_trace=generator_response.reasoning,
        predicted_answer=generator_response.final_answer,
        ground_truth_answer="empty",
        environment_feedback="empty",
        playbook=json.dumps(playbook),
    )
    response = await client.get_response(user_prompt=reflector_prompt)
    reflector_response = ReflectorResponse(**response)
    print(reflector_response)

    # --------------------------------CURATOR--------------------------------
    curator_prompt = Prompts().get_curator_prompt(
        recent_reflection=reflector_response.reasoning,
        current_playbook=json.dumps(playbook),
        question_context=MESSAGES,
    )
    response = await client.get_response(user_prompt=curator_prompt)
    curator_response = CuratorResponse(**response)
    print(curator_response)


if __name__ == "__main__":
    asyncio.run(main())
