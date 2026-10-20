
import os
import json
import re
from typing import TypedDict, List, Any

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY missing hai. Apni .env file check karein."
    )

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=api_key,
    timeout=120,
    max_retries=2,
)


# Shared LangGraph state
class TodoState(TypedDict):
    user_input: str
    tasks: List[dict]
    prioritized_tasks: List[dict]
    result: str


# Safely extract JSON from an AI response
def parse_json_response(content: Any):
    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))

        content = "".join(parts)

    if not isinstance(content, str):
        content = str(content)

    content = content.strip()

    # Remove Markdown code fences if present
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    # Find the JSON array in the response
    start = content.find("[")
    end = content.rfind("]")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            f"AI ne valid JSON array return nahi ki. Response: {content[:300]}"
        )

    data = json.loads(content[start:end + 1])

    if not isinstance(data, list):
        raise ValueError("AI response JSON array nahi hai.")

    return data


# Node 1: Extract tasks
def extract_tasks(state: TodoState):
    prompt = f"""
Extract actionable tasks from the following text.

Return ONLY a JSON array. Do not use Markdown or explanations.

Each task must contain:
- "task": task description
- "deadline": deadline mentioned, or "Not specified"

Example:
[
  {{
    "task": "Complete Python assignment",
    "deadline": "Tomorrow"
  }}
]

If there are no actionable tasks, return [].

User text:
{state["user_input"]}
"""

    response = llm.invoke(prompt)
    tasks = parse_json_response(response.content)

    cleaned_tasks = []

    for item in tasks:
        if not isinstance(item, dict):
            continue

        task_name = item.get("task", "")

        if not isinstance(task_name, str) or not task_name.strip():
            continue

        deadline = item.get("deadline", "Not specified")

        cleaned_tasks.append({
            "task": task_name.strip(),
            "deadline": str(deadline),
        })

    return {"tasks": cleaned_tasks}


# Node 2: Prioritize tasks
def prioritize_tasks(state: TodoState):
    tasks = state.get("tasks", [])

    if not tasks:
        return {"prioritized_tasks": []}

    prompt = f"""
Assign a priority to each task.

Allowed priorities: High, Medium, Low.

Return ONLY a JSON array. Do not use Markdown or explanations.
Keep each task's original task description and deadline.
Add a "priority" field to every task.

Tasks:
{json.dumps(tasks, ensure_ascii=False)}
"""

    response = llm.invoke(prompt)
    ai_tasks = parse_json_response(response.content)

    # Match AI results to the original tasks safely
    prioritized_tasks = []

    for index, original in enumerate(tasks):
        candidate = (
            ai_tasks[index]
            if index < len(ai_tasks) and isinstance(ai_tasks[index], dict)
            else {}
        )

        priority = str(candidate.get("priority", "Medium")).strip().title()

        if priority not in {"High", "Medium", "Low"}:
            priority = "Medium"

        prioritized_tasks.append({
            "task": original["task"],
            "deadline": original["deadline"],
            "priority": priority,
        })

    return {"prioritized_tasks": prioritized_tasks}


# Node 3: Format the results
def format_results(state: TodoState):
    tasks = state.get("prioritized_tasks", [])

    if not tasks:
        return {"result": "Koi actionable task nahi mila."}

    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }

    tasks = sorted(
        tasks,
        key=lambda item: priority_order.get(
            item.get("priority", "Medium"), 1
        ),
    )

    lines = ["Your Organized To-Do List:", ""]

    for index, task in enumerate(tasks, start=1):
        lines.append(f"{index}. {task['task']}")
        lines.append(f"   Priority: {task['priority']}")
        lines.append(f"   Deadline: {task['deadline']}")
        lines.append("")

    return {"result": "\n".join(lines).strip()}


# Build the LangGraph workflow
workflow = StateGraph(TodoState)

workflow.add_node("extract_tasks", extract_tasks)
workflow.add_node("prioritize_tasks", prioritize_tasks)
workflow.add_node("format_results", format_results)

workflow.set_entry_point("extract_tasks")
workflow.add_edge("extract_tasks", "prioritize_tasks")
workflow.add_edge("prioritize_tasks", "format_results")
workflow.add_edge("format_results", END)

app_graph = workflow.compile()


# Function used by main.py
def organize_tasks(user_input: str) -> str:
    if not isinstance(user_input, str) or not user_input.strip():
        raise ValueError("Please apne tasks enter karein.")

    initial_state = {
        "user_input": user_input.strip(),
        "tasks": [],
        "prioritized_tasks": [],
        "result": "",
    }

    final_state = app_graph.invoke(initial_state)

    return final_state["result"]
