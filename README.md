# 🧠 Adaptive Learning System v2

### Knowledge-Graph-Grounded, Interview-Aware Adaptive Learning Planner

> An intelligent adaptive learning platform that personalizes learning roadmaps using curriculum knowledge graphs, mastery inference, dynamic replanning, and retrieval-augmented explanations.

Built from the architecture proposed in the research paper and implemented end-to-end using **FastAPI + React + Knowledge Graph Reasoning + LLM-assisted evaluation**.

---

## ✨ Overview

Adaptive Learning System v2 transforms static learning paths into **living learning roadmaps**.

The platform continuously evaluates learner understanding through interviews, tracks mastery evolution, reasons over prerequisite dependencies, and dynamically adjusts the curriculum to maximize learning efficiency.

### Core Capabilities

✔ Curriculum Knowledge Graph
✔ Interview-Based Mastery Detection
✔ Knowledge-Graph Reasoning
✔ Dynamic Learning Roadmap Replanning
✔ Retrieval-Augmented Explanations (RAG)
✔ Interactive Graph Visualization
✔ Personalized Progress Tracking

---

## 🏗 Architecture

```text
adaptive_learning_system/

├── backend/
│   ├── core/
│   │   ├── kg.py
│   │   ├── learner.py
│   │   ├── interviewer.py
│   │   ├── reasoner.py
│   │   ├── replanner.py
│   │   └── rag.py
│   │
│   ├── data/
│   │   ├── knowledge_graph.json
│   │   └── question_bank.json
│   │
│   └── main.py

└── frontend/
    └── src/
        ├── components/
        │   ├── KGGraph.jsx
        │   ├── InterviewPanel.jsx
        │   ├── RoadmapPanel.jsx
        │   └── MasteryPanel.jsx
        │
        └── App.jsx
```

---

# 🧩 System Components

## Component 1 — Curriculum Knowledge Graph

Builds a prerequisite-aware curriculum structure.

### Responsibilities

* Concept dependency modeling
* Graph traversal
* Learning sequence generation
* Curriculum expansion

Input:

```text
knowledge_graph.json
```

Output:

```text
Structured curriculum graph
```

---

## Component 2 — Interview-Driven Mastery Inference

Evaluates learner understanding through adaptive interviews.

### Responsibilities

* Multi-level questioning
* Mastery estimation
* Confidence scoring
* Interview feedback loop

Input:

```text
question_bank.json
learner responses
```

Output:

```text
Updated mastery profile
```

---

## Component 3 — Plan-Aware Knowledge Graph Reasoner

Generates personalized learning decisions.

### Responsibilities

* Detect prerequisite violations
* Recommend next concepts
* Prioritize weak areas
* Generate roadmap transitions

---

## Component 4 — Dynamic Roadmap Replanner

Continuously adjusts learning plans.

### Responsibilities

* Forgetting detection
* Progress adaptation
* Roadmap recalculation
* Dependency correction

---

## Component 5 — Retrieval-Augmented Explanation Layer

Explains **why** roadmap changes happen.

### Responsibilities

* Concept explanations
* Change reasoning
* Context-aware recommendations
* LLM-generated guidance

---

# 🚀 Getting Started

## Backend Setup

```bash
cd backend

cp .env.example .env

pip install -r requirements.txt

python main.py
```

Backend:

```text
http://localhost:8000
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# ⚙ Environment Variables

```env
GEMINI_API_KEY=

GEMINI_MODEL=gemini-1.5-flash
```

### Notes

* System supports **mock mode** without API keys
* Gemini enables:

  * Interview evaluation
  * RAG explanations
  * Enhanced reasoning

---

# 🔌 API Surface

| Method | Endpoint                       | Purpose                 |
| ------ | ------------------------------ | ----------------------- |
| GET    | /kg/graph                      | Curriculum graph        |
| GET    | /kg/roadmap                    | Canonical roadmap       |
| GET    | /learner/{id}                  | Learner snapshot        |
| POST   | /learner/{id}/reset            | Reset learner           |
| POST   | /learner/mastery/update        | Update mastery          |
| GET    | /interview/questions/{concept} | Fetch questions         |
| POST   | /interview/evaluate            | Evaluate responses      |
| GET    | /plan/{id}                     | Personalized roadmap    |
| GET    | /plan/{id}/analysis            | Reasoning output        |
| POST   | /explain/change                | Explain roadmap updates |
| GET    | /explain/concept/{lid}/{cid}   | Concept explanation     |

---

# 🖥 Product Walkthrough

<img width="1912" height="847" alt="Screenshot 2026-06-11 224048" src="https://github.com/user-attachments/assets/668dbe0a-c717-4e56-9dd8-46a1b56b0ac3" />
<img width="1872" height="827" alt="Screenshot 2026-06-11 224139" src="https://github.com/user-attachments/assets/8946ce2a-5994-47f1-8daf-d32a7081934d" />
<img width="1856" height="833" alt="Screenshot 2026-06-11 224155" src="https://github.com/user-attachments/assets/7546fc1a-25fa-4e9f-bbe5-fc53b4d66723" />
<img width="1870" height="841" alt="Screenshot 2026-06-11 224240" src="https://github.com/user-attachments/assets/2a0f95ea-041a-4ae4-9393-7ae4108f0ba2" />
<img width="1880" height="836" alt="Screenshot 2026-06-11 224258" src="https://github.com/user-attachments/assets/408f8949-7cf8-4143-84f6-4d97fc9b5523" />
<img width="1893" height="841" alt="Screenshot 2026-06-11 224318" src="https://github.com/user-attachments/assets/135905cd-517c-482d-93e9-108b865a495f" />
<img width="1915" height="831" alt="Screenshot 2026-06-11 224333" src="https://github.com/user-attachments/assets/dfc5274d-f61b-4d7a-bf53-795e2c73434a" />
<img width="1882" height="845" alt="Screenshot 2026-06-11 224348" src="https://github.com/user-attachments/assets/4ccd6894-eea2-496d-aca6-e4b590da0268" />
<img width="1883" height="850" alt="Screenshot 2026-06-11 224400" src="https://github.com/user-attachments/assets/95e2b573-9cd5-4869-8200-80193fda297a" />
<img width="1887" height="846" alt="Screenshot 2026-06-11 224417" src="https://github.com/user-attachments/assets/e8c47c33-89ec-43ef-a33e-8f8eba8ee3a7" />


# 📈 Example Workflow

```text
Start Learning
      ↓
Interview Evaluation
      ↓
Mastery Estimation
      ↓
KG Reasoning
      ↓
Roadmap Generation
      ↓
Dynamic Replanning
      ↓
RAG Explanation
```

---

# 🧪 Extending The System

## Add Concepts

```text
backend/data/knowledge_graph.json
```

---

## Add Interview Questions

```text
backend/data/question_bank.json
```

---

## Switch Learning Domain

Duplicate:

```text
knowledge_graph.json
question_bank.json
```

Update:

```text
CurriculumKG()
```

---

## Add Persistence

Current:

```text
_sessions = {}
```

Recommended:

```text
MongoDB
Redis
PostgreSQL
```

---

# 🛠 Tech Stack

**Frontend**

* React
* Vite
* Canvas Rendering

**Backend**

* FastAPI
* Python

**AI**

* Gemini API
* Retrieval-Augmented Generation

**Learning Intelligence**

* Knowledge Graph
* Dynamic Replanning
* Mastery Modeling

---

# 🎯 Future Improvements

* Multi-user authentication
* Persistent learner memory
* Analytics dashboard
* Multi-domain learning support
* Fine-tuned evaluation models
* Deployment pipeline

---

# 📄 License

MIT License

---

### Built to make learning adaptive, explainable, and personalized.
