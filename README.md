# 🤖 AI To-Do List Organizer

An AI-powered task management application built with **Python, FastAPI, LangGraph, and Groq AI**. It organizes tasks, assigns priorities, and identifies deadlines from natural language input.

## ✨ Features

- 📝 Extract tasks from natural language
- 🎯 Automatically prioritize tasks
- 📅 Identify task deadlines
- ⚡ AI-powered task organization
- 🖥️ Modern, responsive web interface
- ✅ Mark tasks as completed

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI
- **AI Workflow:** LangGraph
- **LLM:** Groq API
- **Environment Management:** Python Virtual Environment

## 📁 Project Structure

```text
AI-todo-organizer/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── main.py
├── graph.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## ⚙️ Installation

1. Clone the repository:

   ```bash
   git clone YOUR_GITHUB_REPOSITORY_URL
   cd AI-todo-organizer
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   Windows:

   ```powershell
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your Groq API key:

   ```env
   GROQ_API_KEY=your_groq_api_key
   ```

5. Start the backend:

   ```bash
   python -m uvicorn main:app --reload
   ```

6. Open the API documentation:

   `http://127.0.0.1:8000/docs`

7. Open `frontend/index.html` using the VS Code Live Server extension to use the web interface.

## 🚀 Usage

1. Enter your tasks in natural language.
2. Click **Organize with AI**.
3. View extracted tasks, priorities, and deadlines.
4. Mark tasks as completed when finished.

### Example Input

```text
Complete my AI assignment by tomorrow,
buy groceries today, and prepare for my
Data Science exam next week.
```

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key used to access Groq AI |

**Security:** Never upload your `.env` file or expose your API key publicly.

## 📌 Future Improvements

- Save tasks in a database
- Add user authentication
- Send deadline reminders
- Allow editing and deleting tasks
- Deploy the application online


*Built with Python and AI to make task management smarter and easier.*
