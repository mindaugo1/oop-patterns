from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import asyncio

from prompts import Prompts
from llm_client import OpenAIClient
from models import (
    GeneratorResponse,
    ReflectorResponse,
    CuratorResponse,
    AgentNames,
    Context,
)
from helpers import log_agent_counts

# faked generator response
REASONING = "The task is to write a Python function that calculates the average of numeric items in a list of strings. The approach involves iterating over each string in the list, attempting to convert it to a float, and if successful, including it in the sum and count for averaging. According to the playbook, the average is calculated by summing all successfully converted numeric values and dividing by their count. The function will handle conversion errors by skipping non-numeric strings. Finally, the function returns the average as a float"

BULLET_IDS = ["003 formulas_and_calculations"]

FINAL_ANSWER = "def avg_numbers(data: list[str]) -> float:\n    total = 0.0\n    count = 0\n    for item in data:\n        try:\n            num = float(item)\n            total += num\n            count += 1\n        except ValueError:\n            continue\n    if count == 0:\n        return 0.0\n    return total / len(data)"


class Agent(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self._children: List["Agent"] = []

    @abstractmethod
    async def _act(self, task: Dict[str, Any], context: Context) -> None:
        ...

    def add_child(self, child: "Agent") -> None:
        self._children.append(child)

    def remove_child(self, child: "Agent") -> None:
        self._children.remove(child)

    def get_children(self) -> List["Agent"]:
        return list(self._children)


class TeamManager(Agent):
    """Composite. Executes children in order and returns the final context."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._expected_order = [
            AgentNames.GENERATOR.value,
            AgentNames.REFLECTOR.value,
            AgentNames.CURATOR.value,
        ]

    async def _act(self, task: Dict[str, Any], context: Context) -> None:
        for child in self._children:
            await child._act(task=task, context=context)

    async def run(self, task: Dict[str, Any]) -> Context:
        log_agent_counts(self._children)
        self._reorder_agents()
        context: Context = {}
        await self._act(task, context)
        return context

    def _reorder_agents(self) -> None:
        reordered = []
        for expected_name in self._expected_order:
            for child in self._children:
                if child.name == expected_name:
                    reordered.append(child)

        self._children = reordered


class GeneratorAgent(Agent):
    def __init__(self, name: str, client: OpenAIClient) -> None:
        super().__init__(name)
        self.client = client
        self.get_prompt_fn = Prompts().get_generator_prompt

    async def _act(self, task: Dict[str, Any], context: Context) -> None:
        prompt = self.get_prompt_fn(
            playbook=json.dumps(task["playbook"]),
            question=task["query"],
            reflection="empty",
            context="empty",
        )
        generator_response = GeneratorResponse(
            reasoning=REASONING,
            bullet_ids=BULLET_IDS,
            final_answer=FINAL_ANSWER,
        )
        context.setdefault(AgentNames.GENERATOR.value, []).append(generator_response)


class ReflectorAgent(Agent):
    def __init__(self, name: str, client: OpenAIClient) -> None:
        super().__init__(name)
        self.client = client
        self.get_prompt_fn = Prompts().get_reflector_prompt

    async def _act(self, task: Dict[str, Any], context: Context) -> None:
        generator_output: Optional[List[GeneratorResponse]] = context.get(
            AgentNames.GENERATOR.value
        )
        if generator_output is None:
            raise RuntimeError("ReflectorAgent requires Generator output in context.")

        responses = await asyncio.gather(
            *[
                self.client.get_response(
                    user_prompt=self.get_prompt_fn(
                        question=task["query"],
                        reasoning_trace=gen_resp.reasoning,
                        predicted_answer=gen_resp.final_answer,
                        ground_truth_answer="empty",
                        environment_feedback="empty",
                        playbook=json.dumps(task["playbook"]),
                    )
                )
                for gen_resp in generator_output
            ]
        )

        for response in responses:
            context.setdefault(AgentNames.REFLECTOR.value, []).append(
                ReflectorResponse(**response)
            )


class CuratorAgent(Agent):
    def __init__(self, name: str, client: OpenAIClient) -> None:
        super().__init__(name)
        self.client = client
        self.get_prompt_fn = Prompts().get_curator_prompt

    async def _act(self, task: Dict[str, Any], context: Context) -> None:
        reflector_output: Optional[List[ReflectorResponse]] = context.get(
            AgentNames.REFLECTOR.value
        )
        if reflector_output is None:
            raise RuntimeError("CuratorAgent requires Reflector output in context.")

        responses = await asyncio.gather(
            *[
                self.client.get_response(
                    user_prompt=self.get_prompt_fn(
                        recent_reflection=ref_resp.reasoning,
                        current_playbook=json.dumps(task["playbook"]),
                        question_context=task["query"],
                    )
                )
                for ref_resp in reflector_output
            ]
        )

        for response in responses:
            context.setdefault(AgentNames.CURATOR.value, []).append(
                CuratorResponse(**response)
            )
