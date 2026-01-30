# Copilot Instructions for Multi-Agent Interview Project

This document provides essential guidance for AI coding agents working on the "Multi-Agent Interview" project. Understanding these patterns will enable immediate productivity.

## 1. Project Overview
This project simulates a technical job interview using a multi-agent system orchestrated by `langgraph`. It involves an Interviewer, an Observer, and a Reporter agent, which interact to conduct an interview, provide feedback, and generate a final report.

## 2. Core Architecture and Data Flow

### Key Components:
- **`main.py`**: Entry point. Initializes the LLMs, sets up the `langgraph` workflow, and manages the main interview loop.
- **`agents/`**: Contains individual agent definitions (`interviewer.py`, `observer.py`, `reporter.py`).
- **`core/`**: Houses core functionalities:
    - **`graph.py`**: Defines the `langgraph` state machine, connecting agents and managing transitions.
    - **`state.py`**: Defines the `InterviewState` (a `TypedDict`)—the central shared state for all agents.
    - **`logger.py`**: Handles logging of interview turns and the final report to `data/interview_log.json`.
- **`utils/llm_factory.py`**: Manages LLM instantiation, providing different models based on agent roles.

### Data Flow Overview:
The interview progresses through a state machine defined in `core/graph.py`.
1. **Initial State**: `main.py` sets up `InterviewState` with initial messages and metadata.
2. **Observer Node (`observer.py`)**: Analyzes candidate's response (from `state.messages`) and `metadata` to generate `internal_thoughts`.
3. **Interviewer Node (`interviewer.py`)**: Uses `INTERVIEWER_PROMPT` and `internal_thoughts` to formulate the next question for the candidate, updating `state.messages`.
4. **User Input**: `main.py` captures user input and updates `state.messages`.
5. **Looping**: Steps 2-4 repeat until `is_finished` flag in `InterviewState` is set to `True`.
6. **Reporter Node (`reporter.py`)**: When `is_finished` is `True`, the `reporter_node` is invoked to generate a comprehensive `final_report` based on the entire interview context (`state.messages`, `state.internal_thoughts`, `state.metadata`).
7. **Logging**: `core/logger.py` continuously logs each turn and the `final_report` to `data/interview_log.json`.

## 3. Project-Specific Conventions

- **Shared State (`core/state.py`)**: All agents read from and write to the `InterviewState` object. Modifications to agent behavior often involve updating this state or how agents interpret it.
- **Role-Based LLM Selection (`utils/llm_factory.py`)**: Different LLMs are used for different agent roles. For instance, the `reporter` agent typically uses a more powerful model (`gpt-4-turbo`) for complex reasoning, while conversational agents might use faster models (`gpt-3.5-turbo`).
- **Prompt Engineering**: Each agent's behavior is primarily guided by its dedicated prompt string (e.g., `INTERVIEWER_PROMPT` in `interviewer.py`). Changes to agent persona or goals should start with prompt modification.
- **Conditional Graph Transitions (`core/graph.py`)**: The flow between agents is managed by conditional edges in `langgraph`. The `routing_logic` function determines the next step.

## 4. Key Files and Directories

- `main.py`: Main execution logic.
- `config.py`: Currently empty, but intended for global configurations (e.g., API keys, model parameters).
- `agents/`: Contains agent-specific logic and prompts.
- `core/graph.py`: Defines the `langgraph` workflow.
- `core/state.py`: Defines the shared `InterviewState` schema.
- `utils/llm_factory.py`: LLM provider and configuration.
- `data/interview_log.json`: Interview log output.

## 5. Developer Workflow

- **Running the Application**: Execute `python main.py` from the project root.
- **Debugging**: Standard Python debugging tools can be used. Focus on inspecting the `InterviewState` at each step of the `langgraph` invocation.
- **Adding/Modifying Agents**:
    1. Create a new Python file in `agents/` for the new agent, defining its node function and prompt.
    2. Update `core/graph.py` to add the new agent as a node and define its edges within the `langgraph` workflow.
    3. If necessary, update `core/state.py` to include any new state variables required by the agent.
    4. Consider updating `utils/llm_factory.py` if the new agent requires a specific LLM configuration.

## 6. External Dependencies

- `langchain-openai`: For interacting with OpenAI models.
- `langchain-community`: For community-contributed LangChain integrations (e.g., Ollama, if used).
- `langgraph`: For orchestrating the multi-agent workflow.

Ensure these dependencies are installed (e.g., via `pip install -r requirements.txt` if a `requirements.txt` file is present, or individual `pip install` commands). Currently, no `requirements.txt` is present, so install them manually.
