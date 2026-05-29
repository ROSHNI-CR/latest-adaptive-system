"""
Adaptive Learning System FastAPI backend.

The frontend-facing routes are intentionally wired through backend/services so
the UI connects to the service layer instead of directly depending on core.
"""

from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services import app_service


app = FastAPI(title="Adaptive Learning System", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateUserRequest(BaseModel):
    name: str
    email: str


class AnswerItem(BaseModel):
    question_id: str
    answer: str


class EvaluateRequest(BaseModel):
    learner_id: str
    concept_id: str
    answers: List[AnswerItem]


class UpdateMasteryRequest(BaseModel):
    learner_id: str
    concept_id: str
    score: float


class ExplainRequest(BaseModel):
    learner_id: str
    concept_id: str
    action: str
    reason: str


class OnboardRequest(BaseModel):
    learner_id: str
    self_proficiency_level: str


class AssessmentSubmitRequest(BaseModel):
    learner_id: str
    answers: List[Dict[str, str]]
    self_proficiency_level: Optional[str] = None


class GoalsGenerateRequest(BaseModel):
    learner_id: str
    deadline_weeks: int = 12


@app.get("/")
def root():
    return {"status": "ok", "system": "Adaptive Learning System v3"}


@app.post("/user/create")
def create_user_api(req: CreateUserRequest):
    return app_service.create_user_profile(req.name, req.email)


@app.get("/kg/graph")
def kg_graph():
    return app_service.get_graph()


@app.get("/kg/roadmap")
def kg_roadmap():
    return app_service.get_roadmap()


@app.get("/kg/concept/{concept_id}")
def kg_concept(concept_id: str):
    concept = app_service.get_concept(concept_id)
    if not concept:
        raise HTTPException(404, f"Concept '{concept_id}' not found")
    return concept


@app.get("/learner/{learner_id}")
def get_learner_state(learner_id: str):
    return app_service.get_learner_state(learner_id)


@app.post("/learner/{learner_id}/reset")
def reset_learner(learner_id: str):
    return app_service.reset_learner(learner_id)


@app.post("/learner/mastery/update")
def update_mastery(req: UpdateMasteryRequest):
    return app_service.update_mastery(
        req.learner_id,
        req.concept_id,
        req.score,
    )


@app.get("/interview/questions/{concept_id}")
def get_questions(concept_id: str):
    questions = app_service.get_questions(concept_id)
    if not questions:
        raise HTTPException(404, f"No questions for concept '{concept_id}'")
    return {"concept_id": concept_id, "questions": questions}


@app.post("/interview/evaluate")
def evaluate_interview(req: EvaluateRequest):
    return app_service.evaluate_interview(
        req.learner_id,
        req.concept_id,
        [answer.model_dump() for answer in req.answers],
    )


@app.get("/plan/{learner_id}")
def get_plan(learner_id: str):
    return app_service.get_plan(learner_id)


@app.get("/plan/{learner_id}/analysis")
def get_analysis(learner_id: str):
    return app_service.get_analysis(learner_id)


@app.post("/explain/change")
def explain_change(req: ExplainRequest):
    return app_service.explain_change(
        req.learner_id,
        req.concept_id,
        req.action,
        req.reason,
    )


@app.get("/explain/concept/{learner_id}/{concept_id}")
def explain_concept(learner_id: str, concept_id: str):
    return app_service.explain_concept(learner_id, concept_id)


@app.post("/learner/onboard")
def onboard_learner(req: OnboardRequest):
    return app_service.onboard_learner(
        req.learner_id,
        req.self_proficiency_level,
    )


@app.post("/learner/assessment/submit")
def submit_assessment(req: AssessmentSubmitRequest):
    return app_service.submit_assessment(
        req.learner_id,
        req.answers,
        req.self_proficiency_level,
    )


@app.post("/learner/goals/generate")
def generate_learning_goals(req: GoalsGenerateRequest):
    return app_service.generate_learning_goals(
        req.learner_id,
        req.deadline_weeks,
    )


@app.post("/learner/goals/accept")
def accept_learning_goals(req: OnboardRequest):
    return app_service.accept_learning_goals(req.learner_id)


@app.get("/learner/{learner_id}/personalized-roadmap")
def get_personalized_roadmap(learner_id: str):
    return app_service.get_personalized_roadmap(learner_id)


@app.get("/graph/{learner_id}/next")
def get_next_nodes(learner_id: str):
    return app_service.get_next_nodes(learner_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
