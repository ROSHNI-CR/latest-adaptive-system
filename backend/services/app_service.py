"""
Service-facing application API for the FastAPI route layer.

This keeps the route module connected to backend/services while preserving the
existing core behavior behind the service boundary.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.interviewer import InterviewEngine
from core.kg import CurriculumKG
from core.learner import LearnerState, ProficiencyLevel
from core.rag import RAGExplainer
from core.reasoner import PlanAwareReasoner
from core.replanner import DynamicReplanner
from db.mongo import learner_collection
from db.neo4j import driver
from services.learner_service import (
    create_learner_state,
    load_learner_state,
    persist_learner_state,
    update_concept as mongo_update_concept,
)
from services.roadmap_service import handle_mastery_update
from services.sync_service import create_user_node, sync_user_to_neo4j
from services.user_service import create_user


kg = CurriculumKG()
interviewer = InterviewEngine()
reasoner = PlanAwareReasoner(kg)
replanner = DynamicReplanner(kg, reasoner)
rag = RAGExplainer(kg)

_sessions: Dict[str, LearnerState] = {}
_canonical_positions: Dict[str, int] = {}


def _try_neo4j(action) -> None:
    try:
        action()
    except Exception as exc:
        print(f"Neo4j sync skipped: {exc}")


def _persist_learner_metadata(learner: LearnerState) -> None:
    persist_learner_state(
        learner,
        canonical_position=_canonical_positions.get(learner.learner_id, 0),
    )


def _ensure_persistent_learner(learner_id: str) -> None:
    existing = learner_collection.find_one({"user_id": learner_id})
    if existing is None:
        create_learner_state(learner_id)
    _try_neo4j(lambda: create_user_node(learner_id))
    _try_neo4j(lambda: sync_user_to_neo4j(learner_id))


def get_learner(learner_id: str) -> LearnerState:
    if learner_id not in _sessions:
        _ensure_persistent_learner(learner_id)
        loaded = load_learner_state(learner_id)
        if loaded is None or loaded[0] is None:
            learner = LearnerState(learner_id, kg.all_concept_ids())
            canonical_position = 0
        else:
            learner, canonical_position = loaded
        _sessions[learner_id] = learner
        _canonical_positions[learner_id] = canonical_position
    return _sessions[learner_id]


def _snapshot(learner: LearnerState) -> Dict:
    data = learner.snapshot()
    data.update({
        "proficiency_level": learner.proficiency_level.value,
        "onboarding_complete": learner.onboarding_complete,
        "proficiency_assessment_results": learner.proficiency_assessment_results,
        "learning_deadline": learner.learning_deadline,
        "learning_goals": learner.learning_goals,
        "timeline_adjustments": learner.timeline_adjustments,
        "weak_points": learner.weak_points,
    })
    return data


def create_user_profile(name: str, email: str) -> Dict:
    user = create_user(name, email)
    _ensure_persistent_learner(user["user_id"])
    return user


def get_graph() -> Dict:
    return kg.to_graph_data()


def get_roadmap() -> Dict:
    return {"roadmap": kg.canonical_roadmap()}


def get_concept(concept_id: str) -> Optional[Dict]:
    return kg.get(concept_id)


def get_learner_state(learner_id: str) -> Dict:
    return _snapshot(get_learner(learner_id))


def reset_learner(learner_id: str) -> Dict:
    _sessions[learner_id] = LearnerState(learner_id, kg.all_concept_ids())
    _canonical_positions[learner_id] = 0
    learner_collection.delete_many({"user_id": learner_id})
    create_learner_state(learner_id)
    persist_learner_state(_sessions[learner_id], canonical_position=0)
    _try_neo4j(lambda: sync_user_to_neo4j(learner_id))
    return {"reset": True}


def update_mastery(learner_id: str, concept_id: str, score: float) -> Dict:
    learner = get_learner(learner_id)
    learner.update(concept_id, score)
    state = learner.get(concept_id)

    mongo_update_concept(
        learner_id,
        concept_id,
        state.score,
        state.level.value,
    )
    _try_neo4j(lambda: sync_user_to_neo4j(learner_id))

    if state.level.value == "strong":
        _try_neo4j(lambda: handle_mastery_update(learner_id, concept_id))
    persist_learner_state(
        learner,
        canonical_position=_canonical_positions.get(learner_id, 0),
    )

    return {
        "concept_id": concept_id,
        "score": state.score,
        "level": state.level,
    }


def get_questions(concept_id: str) -> List[Dict]:
    return interviewer.get_questions(concept_id)


def evaluate_interview(learner_id: str, concept_id: str, answers: List[Dict]) -> Dict:
    result = interviewer.evaluate_session(concept_id, answers)
    learner = get_learner(learner_id)
    learner.update(concept_id, result["composite_score"])
    state = learner.get(concept_id)

    mongo_update_concept(
        learner_id,
        concept_id,
        state.score,
        state.level.value,
    )
    _try_neo4j(lambda: sync_user_to_neo4j(learner_id))

    if state.level.value == "strong":
        _try_neo4j(lambda: handle_mastery_update(learner_id, concept_id))

    roadmap = kg.all_concept_ids()
    if concept_id in roadmap:
        idx = roadmap.index(concept_id)
        current_pos = _canonical_positions.get(learner_id, 0)
        _canonical_positions[learner_id] = max(current_pos, idx + 1)
    persist_learner_state(
        learner,
        canonical_position=_canonical_positions.get(learner_id, 0),
    )

    return {
        **result,
        "updated_mastery": {
            "score": state.score,
            "level": state.level,
        },
    }


def get_plan(learner_id: str) -> Dict:
    learner = get_learner(learner_id)
    plan = replanner.generate_roadmap(
        learner,
        _canonical_positions.get(learner_id, 0),
    )
    persist_learner_state(
        learner,
        canonical_position=_canonical_positions.get(learner_id, 0),
        current_plan=plan,
        current_analysis=plan.get("analysis"),
    )
    return plan


def get_analysis(learner_id: str) -> Dict:
    learner = get_learner(learner_id)
    analysis = reasoner.analyse(
        learner,
        _canonical_positions.get(learner_id, 0),
    ).to_dict()
    persist_learner_state(
        learner,
        canonical_position=_canonical_positions.get(learner_id, 0),
        current_analysis=analysis,
    )
    return analysis


def explain_change(learner_id: str, concept_id: str, action: str, reason: str) -> Dict:
    learner = get_learner(learner_id)
    text = rag.explain_roadmap_change(
        concept_id,
        action,
        reason,
        learner.mastery_score(concept_id),
    )
    return {"explanation": text}


def explain_concept(learner_id: str, concept_id: str) -> Dict:
    learner = get_learner(learner_id)
    analysis = reasoner.analyse(learner, _canonical_positions.get(learner_id, 0))
    weak_prereqs = analysis.weak_root_causes.get(concept_id, [])
    forgetting = [
        e for e in analysis.forgetting_events if e["concept_id"] == concept_id
    ]

    explanations: Dict[str, str] = {}
    if forgetting:
        explanations["forgetting"] = rag.explain_forgetting(
            concept_id,
            learner.mastery_score(concept_id),
        )
    if weak_prereqs:
        explanations["weak_prereqs"] = rag.explain_weak_concept(
            concept_id,
            weak_prereqs,
        )

    concept = kg.get(concept_id) or {}
    return {
        "concept_id": concept_id,
        "name": concept.get("name", concept_id),
        "description": concept.get("description", ""),
        "mastery": learner.get(concept_id).to_dict(),
        "explanations": explanations,
        "prerequisites": [
            {
                "id": prerequisite,
                "name": (kg.get(prerequisite) or {}).get("name", prerequisite),
                "level": learner.mastery_level(prerequisite),
            }
            for prerequisite in kg.prerequisites(concept_id)
        ],
    }


def onboard_learner(learner_id: str, self_proficiency_level: str) -> Dict:
    learner = get_learner(learner_id)

    try:
        learner.proficiency_level = ProficiencyLevel(
            self_proficiency_level.lower()
        )
    except ValueError:
        learner.proficiency_level = ProficiencyLevel.UNASSESSED

    learner.onboarding_complete = False
    _persist_learner_metadata(learner)
    assessment_questions = interviewer.get_assessment_questions(num_questions=5)

    return {
        "learner_id": learner_id,
        "proficiency_level": learner.proficiency_level.value,
        "onboarding_complete": False,
        "next_step": "assessment_questions",
        "assessment_questions": assessment_questions,
    }


def submit_assessment(
    learner_id: str,
    answers: List[Dict],
    self_proficiency_level: Optional[str] = None,
) -> Dict:
    learner = get_learner(learner_id)
    assessment_result = interviewer.assess_proficiency(
        self_proficiency_level or "beginner",
        answers,
    )

    learner.proficiency_assessment_results = assessment_result
    learner.proficiency_level = ProficiencyLevel(
        assessment_result["proficiency_label"]
    )
    _persist_learner_metadata(learner)

    return {
        "learner_id": learner_id,
        "proficiency_label": assessment_result["proficiency_label"],
        "score": assessment_result["validated_score"],
        "assessment_notes": assessment_result["assessment_notes"],
        "next_step": "goal_generation",
    }


def generate_learning_goals(learner_id: str, deadline_weeks: int) -> Dict:
    learner = get_learner(learner_id)
    roadmap_data = reasoner.generate_proficiency_roadmap(
        learner.proficiency_level.value,
        deadline_weeks=deadline_weeks,
    )

    learner.learning_goals = roadmap_data["learning_goals"]
    deadline = datetime.utcnow() + timedelta(weeks=deadline_weeks)
    learner.learning_deadline = deadline.isoformat()
    _persist_learner_metadata(learner)

    effort_data = {
        cid: (kg.get(cid) or {}).get("effort_hours", 3)
        for cid in roadmap_data["learning_goals"]
    }
    roadmap_description = rag.prompt_roadmap_generation(
        learner.proficiency_level.value,
        roadmap_data["learning_goals"],
        effort_data,
        deadline_weeks,
    )

    return {
        "learner_id": learner_id,
        "proficiency_level": learner.proficiency_level.value,
        "learning_goals": roadmap_data["learning_goals"],
        "milestone_deadlines": roadmap_data["milestone_deadlines"],
        "expected_pace": roadmap_data["expected_pace"],
        "deadline": learner.learning_deadline,
        "roadmap_description": roadmap_description,
        "next_step": "goal_acceptance",
    }


def accept_learning_goals(learner_id: str) -> Dict:
    learner = get_learner(learner_id)
    learner.onboarding_complete = True
    _persist_learner_metadata(learner)
    roadmap_data = replanner.generate_roadmap(learner, 0)
    steps = roadmap_data.get("steps", [])

    return {
        "learner_id": learner_id,
        "status": "onboarding_complete",
        "proficiency_level": learner.proficiency_level.value,
        "learning_deadline": learner.learning_deadline,
        "first_roadmap_steps": steps[:5],
    }


def get_personalized_roadmap(learner_id: str) -> Dict:
    learner = get_learner(learner_id)
    concept_details = []

    for cid in kg.all_concept_ids():
        concept = kg.get(cid) or {}
        mastery = learner.mastery_level(cid)
        if mastery.value == "unknown":
            status = "not_started"
        elif mastery.value == "partial":
            status = "in_progress"
        elif mastery.value == "weak":
            status = "weak"
        else:
            status = "mastered"

        concept_details.append({
            "id": cid,
            "name": concept.get("name", cid),
            "status": status,
            "difficulty": concept.get("difficulty", "medium"),
            "prerequisites": kg.prerequisites(cid),
            "effort_hours": concept.get("effort_hours", 3),
        })

    proficiency = learner.proficiency_level.value
    if proficiency == "beginner":
        concepts = concept_details[:int(len(concept_details) * 0.6)]
    elif proficiency == "intermediate":
        concepts = concept_details[:int(len(concept_details) * 0.7)]
    else:
        concepts = concept_details

    return {
        "learner_id": learner_id,
        "proficiency_level": proficiency,
        "learning_goals": learner.learning_goals,
        "learning_deadline": learner.learning_deadline,
        "onboarding_complete": learner.onboarding_complete,
        "concepts": concepts,
        "milestones": learner.timeline_adjustments,
        "completed_concepts": [
            c["id"] for c in concepts if c["status"] == "mastered"
        ],
        "in_progress_concepts": [
            c["id"] for c in concepts if c["status"] == "in_progress"
        ],
    }


def get_next_nodes(learner_id: str) -> List[Dict]:
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[:NEXT]->(c)
            RETURN c.id AS id, c.name AS name
            """,
            user_id=learner_id,
        )
        return [record.data() for record in result]
