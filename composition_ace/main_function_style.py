import asyncio
import json

from dotenv import load_dotenv

from llm_client import OpenAIClient
from models import GeneratorResponse, ReflectorResponse, CuratorResponse
from prompts import Prompts

load_dotenv()
client = OpenAIClient()
QUERY = "How to access hostinger database?"


async def main():
    # --------------------------------PLAYBOOK--------------------------------
    playbook = {
        "id": "001 double check a password when loging to hostinger",
        "content": "double check a password when loging to hostinger",
    }, {
        "id": "002 check a weather",
        "content": "check a weather in the next 7 days",
    }

    # --------------------------------GENERATOR--------------------------------
    generator_prompt = Prompts().get_generator_prompt(
        playbook=json.dumps(playbook),
        question=QUERY,
        reflection="empty",
        context="empty",
    )
    response = await client.get_response(user_prompt=generator_prompt)
    generator_response = GeneratorResponse(**response)
    print(generator_response)

    # --------------------------------REFLECTOR--------------------------------
    reflector_prompt = Prompts().get_reflector_prompt(
        question=QUERY,
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
        question_context=QUERY,
    )
    response = await client.get_response(user_prompt=curator_prompt)
    curator_response = CuratorResponse(**response)
    print(curator_response)


if __name__ == "__main__":
    asyncio.run(main())
