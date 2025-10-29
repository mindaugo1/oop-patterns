# Agentic Context Engineering (ACE) Implementation

Implementation of Agentic Context Engineering pattern using both functional and OOP composition approaches, based on the paper [Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models](https://arxiv.org/abs/2510.04618).

## Overview

This project demonstrates two architectural patterns for implementing the ACE framework:
- **Functional/Procedural Style**: Sequential function calls with explicit state passing
- **OOP Composition Pattern**: Agent hierarchy using the Composite design pattern

## What is Agentic Context Engineering?

ACE is a framework that treats contexts as evolving "playbooks" that accumulate, refine, and organize strategies through a modular process of generation, reflection, and curation. Unlike traditional approaches that suffer from brevity bias and context collapse, ACE:

- **Prevents context collapse** through structured, incremental updates
- **Preserves detailed knowledge** across iterations
- **Enables self-improvement** through natural execution feedback
- **Scales efficiently** with long-context models

### Core Principles from the Paper

1. **Adaptive Memory**: Contexts evolve like playbooks, not static prompts
2. **Modular Process**: Generation → Reflection → Curation cycle
3. **Structured Updates**: Incremental changes that preserve domain insights
4. **No Labeled Supervision**: Learns from natural execution feedback

## Architecture

### Three-Agent System

The implementation uses three specialized agents that work together in a pipeline:

```
Query + Playbook → Generator → Reflector → Curator → new bullet points 
```

#### 1. Generator Agent
Generates answers using the current playbook and context.

**Input:**
- Question/Query
- Current Playbook
- Previous Reflections
- Context

**Output:**
- Reasoning trace
- Referenced bullet IDs from playbook
- Final answer

**Role**: Acts as the primary problem-solver, applying strategies from the playbook to answer questions.

#### 2. Reflector Agent
Analyzes the generator's reasoning and identifies improvement opportunities.

**Input:**
- Question
- Generator's reasoning trace
- Predicted answer
- Ground truth (when available)
- Environment feedback
- Playbook bullets used

**Output:**
- Error identification
- Root cause analysis
- Correct approach
- Key insight
- Bullet tags (helpful/harmful/neutral)

**Role**: Provides critical analysis and diagnostic feedback on the generation process.

#### 3. Curator Agent
Updates the playbook by adding new insights from reflections.

**Input:**
- Recent reflection
- Current playbook
- Question context

**Output:**
- Reasoning
- Operations (ADD/MODIFY/REMOVE)
- Section assignments
- New content

**Role**: Maintains and evolves the knowledge base through structured updates.

## Implementation Patterns

### Pattern 1: Functional/Procedural Style

**File**: `main_function_style.py`

**Characteristics:**
- Sequential execution with explicit async/await
- Direct function calls to LLM client
- Manual state management
- Clear data flow
- Simpler to understand and debug

**Example:**
```python
async def main():
    playbook = {...}
    
    generator_prompt = Prompts().get_generator_prompt(...)
    response = await client.get_response(user_prompt=generator_prompt)
    generator_response = GeneratorResponse(**response)
    
    reflector_prompt = Prompts().get_reflector_prompt(...)
    response = await client.get_response(user_prompt=reflector_prompt)
    reflector_response = ReflectorResponse(**response)
    
    curator_prompt = Prompts().get_curator_prompt(...)
    response = await client.get_response(user_prompt=curator_prompt)
    curator_response = CuratorResponse(**response)
```

**Pros:**
- Easy to follow execution flow
- Less abstraction overhead
- Straightforward debugging
- Good for prototyping

**Cons:**
- Less scalable for complex workflows
- Code duplication for similar operations
- Harder to reorder or conditionally execute agents
- State management becomes complex with more agents

### Pattern 2: OOP Composition Pattern

**File**: `main_oop_composition_pattern_style.py`

**Characteristics:**
- Uses Composite design pattern
- Polymorphic agent interface
- Shared context object
- Automatic execution ordering
- Extensible architecture

**Structure:**
```
Agent (Abstract Base)
├── TeamManager (Composite)
│   ├── add_child()
│   ├── remove_child()
│   └── run()
├── GeneratorAgent (Leaf)
├── ReflectorAgent (Leaf)
└── CuratorAgent (Leaf)
```

**Example:**
```python
async def main():
    playbook = [...]
    
    team = TeamManager("ImprovementTeam")
    generator_agent = GeneratorAgent(AgentNames.GENERATOR.value, client)
    reflector_agent = ReflectorAgent(AgentNames.REFLECTOR.value, client)
    curator_agent = CuratorAgent(AgentNames.CURATOR.value, client)
    
    team.add_child(generator_agent)
    team.add_child(curator_agent)
    team.add_child(reflector_agent)
    
    result = await team.run(task={"query": MESSAGES, "playbook": playbook})
```

**Pros:**
- Highly extensible (add new agents easily)
- Automatic dependency management
- Reusable components
- Clean separation of concerns
- Better for complex workflows

**Cons:**
- More abstraction layers
- Requires understanding of design patterns
- Slightly more complex debugging
- Overhead for simple scenarios

## Key Design Decisions

### 1. Shared Context Pattern

Both implementations use a shared context dictionary that agents read from and write to:

```python
Context = Dict[str, Any]

context: Context = {
    "Generator": [GeneratorResponse(...)],
    "Reflector": [ReflectorResponse(...)],
    "Curator": [CuratorResponse(...)]
}
```

This enables:
- Data sharing between agents
- History tracking
- Concurrent processing (Reflector processes multiple Generator outputs)


## Usage

### Setup

```bash
cp example.env .env
uv sync
```

### Running Functional Style

```bash
python main_function_style.py
```

### Running OOP Composition Style

```bash
python main_oop_composition_pattern_style.py
```

## When to Use Each Pattern

### Use Functional Style When:
- Building a prototype or proof of concept
- Workflow is simple and linear
- Quick iteration is needed

### Use OOP Composition When:
- System will grow in complexity
- Team is comfortable with design patterns
- Need to support multiple execution strategies

## Comparison with Traditional Approaches

| Aspect | Traditional Prompting | ACE Implementation |
|--------|----------------------|-------------------|
| Context Management | Static prompts | Evolving playbook |
| Learning | No memory | Accumulates insights |
| Feedback | Manual iteration | Automatic reflection |
| Knowledge Loss | High (brevity bias) | Low (structured updates) |
| Scalability | Limited by context | Efficient with long context |

## Implementation Highlights

### Simulated Generator Responses

To better illustrate how the Reflector and Curator agents work, the implementation uses simulated Generator responses instead of actual LLM calls for the Generator agent. This approach:

- Provides a consistent example for understanding agent interactions
- Shows how downstream agents (Reflector, Curator) process Generator output

The simulated response includes intentionally incorrect logic where the average is calculated by dividing by `len(data)` instead of by `count`, allowing the Reflector to identify the error and the Curator to add corrective insights to the playbook.

Example from `main_function_style.py`:

```python
generator_response = GeneratorResponse(
    reasoning="...",
    bullet_ids=["003 formulas_and_calculations"],
    final_answer="def avg_numbers(data: list[str]) -> float:\n    ...\n    return total / len(data)"
)
```

This simulated response is then processed by the Reflector and Curator agents using actual LLM calls, demonstrating the reflection and curation stages of the ACE framework.

## Extension Points

### Adding New Agents

**Functional Style:**
Add new function calls in sequence.

**OOP Style:**
1. Create new agent class inheriting from `Agent`
2. Implement `_act()` method
3. Add to TeamManager with `add_child()`

### Custom Execution Order

**Functional Style:**
Reorder function calls manually.

**OOP Style:**
Modify `_expected_order` in TeamManager or implement custom ordering logic.

## Paper Citation

```
@article{zhang2025ace,
  title={Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models},
  author={Zhang, Qizheng and Hu, Changran and Upasani, Shubhangi and Ma, Boyuan and 
          Hong, Fenglu and Kamanuru, Vamsidhar and Rainton, Jay and Wu, Chen and 
          Ji, Mengmeng and Li, Hanchen and Thakker, Urmish and Zou, James and Olukotun, Kunle},
  journal={arXiv preprint arXiv:2510.04618},
  year={2025}
}
```

## Results from Paper

- **+10.6%** improvement on agent benchmarks
- **+8.6%** improvement on domain-specific tasks (finance)
- Matches top-ranked production agents on AppWorld leaderboard
- Significant reduction in adaptation latency and rollout cost

## License

This implementation is for educational purposes demonstrating design patterns and the ACE framework.
