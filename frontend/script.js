
const API_URL = "http://127.0.0.1:8000/organize";

const form = document.getElementById("taskForm");
const input = document.getElementById("taskInput");
const button = document.getElementById("organizeBtn");
const errorMessage = document.getElementById("errorMessage");

const emptyState = document.getElementById("emptyState");
const loadingState = document.getElementById("loadingState");
const taskResults = document.getElementById("taskResults");

const totalCount = document.getElementById("totalCount");
const highCount = document.getElementById("highCount");
const mediumCount = document.getElementById("mediumCount");
const resultCount = document.getElementById("resultCount");

function setLoading(isLoading) {
  button.disabled = isLoading;
  button.innerHTML = isLoading
    ? '<span class="loader" style="width:15px;height:15px;border-width:2px"></span> Organizing...'
    : '<span>✦</span> Organize with AI <span class="button-arrow">→</span>';

  loadingState.hidden = !isLoading;
  emptyState.hidden = isLoading || taskResults.children.length > 0;
}

function getPriority(task) {
  const value = String(task.priority || "Medium").toLowerCase();

  if (value === "high") return "high";
  if (value === "low") return "low";

  return "medium";
}

function createTaskCard(task, index) {
  const card = document.createElement("article");
  card.className = "task-card";
  card.style.animationDelay = `${index * 60}ms`;

  const top = document.createElement("div");
  top.className = "task-card-top";

  const check = document.createElement("button");
  check.className = "task-check";
  check.type = "button";
  check.setAttribute("aria-label", "Mark task as complete");
  check.textContent = "✓";

  check.addEventListener("click", () => {
    const completed = card.classList.toggle("completed");
    check.setAttribute(
      "aria-label",
      completed ? "Mark task as incomplete" : "Mark task as complete"
    );
    updateCompletedCount();
  });

  const info = document.createElement("div");
  info.className = "task-info";

  const name = document.createElement("div");
  name.className = "task-name";
  name.textContent = task.task || "Untitled task";

  const meta = document.createElement("div");
  meta.className = "task-meta";

  const priority = document.createElement("span");
  const priorityLevel = getPriority(task);
  priority.className = `priority ${priorityLevel}`;
  priority.textContent =
    `${priorityLevel.charAt(0).toUpperCase()}${priorityLevel.slice(1)} priority`;

  const deadline = document.createElement("span");
  deadline.className = "deadline";
  deadline.textContent = `◷ ${task.deadline || "Not specified"}`;

  meta.append(priority, deadline);
  info.append(name, meta);
  top.append(check, info);
  card.append(top);

  return card;
}

function updateCompletedCount() {
  const cards = [...taskResults.querySelectorAll(".task-card")];
  const completed = cards.filter(card =>
    card.classList.contains("completed")
  ).length;

  totalCount.textContent = cards.length;
  highCount.textContent = cards.filter(card =>
    card.querySelector(".priority.high")
  ).length;
  mediumCount.textContent = cards.filter(card =>
    card.querySelector(".priority.medium")
  ).length;

  resultCount.textContent = cards.length;

  const remaining = cards.length - completed;
  document.querySelector(".stat-card:first-child small").textContent =
    `${completed} completed · ${remaining} remaining`;
}

function renderTasks(tasks) {
  taskResults.replaceChildren();

  if (!tasks.length) {
    emptyState.hidden = false;
    emptyState.querySelector("h3").textContent = "No tasks found";
    emptyState.querySelector("p").textContent =
      "Try entering a few tasks or deadlines in the input box.";
    updateCompletedCount();
    return;
  }

  emptyState.hidden = true;

  tasks.forEach((task, index) => {
    taskResults.appendChild(createTaskCard(task, index));
  });

  updateCompletedCount();
}

function parseBackendResult(data) {
  // Preferred format: backend returns a structured task array.
  if (Array.isArray(data.tasks)) {
    return data.tasks;
  }

  // Current backend format: result is formatted text.
  const result = data.result;

  if (typeof result !== "string") {
    throw new Error("Backend response ka format unexpected hai.");
  }

  if (result.includes("Koi actionable task nahi mila.")) {
    return [];
  }

  const lines = result.split("\n");
  const tasks = [];
  let currentTask = null;

  for (const line of lines) {
    const taskMatch = line.match(/^\s*\d+\.\s+(.+)$/);
    const priorityMatch = line.match(/^\s*Priority:\s*(High|Medium|Low)\s*$/i);
    const deadlineMatch = line.match(/^\s*Deadline:\s*(.+)$/i);

    if (taskMatch) {
      if (currentTask) tasks.push(currentTask);

      currentTask = {
        task: taskMatch[1].trim(),
        priority: "Medium",
        deadline: "Not specified"
      };
    } else if (currentTask && priorityMatch) {
      currentTask.priority = priorityMatch[1];
    } else if (currentTask && deadlineMatch) {
      currentTask.deadline = deadlineMatch[1].trim();
    }
  }

  if (currentTask) tasks.push(currentTask);

  return tasks;
}

form.addEventListener("submit", async event => {
  event.preventDefault();

  const message = input.value.trim();

  if (!message) {
    errorMessage.textContent = "Please pehle apne tasks enter karein.";
    input.focus();
    return;
  }

  errorMessage.textContent = "";
  taskResults.replaceChildren();
  setLoading(true);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({ message })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `Request failed (${response.status})`);
    }

    const tasks = parseBackendResult(data);
    renderTasks(tasks);
  } catch (error) {
    emptyState.hidden = true;

    errorMessage.textContent =
      `Unable to organize tasks: ${error.message}. ` +
      "Check that your FastAPI server is running.";

    console.error("Task organizer error:", error);
  } finally {
    setLoading(false);
  }
});
