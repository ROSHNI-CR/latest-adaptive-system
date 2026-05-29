from db.mongo import learner_collection
from core.kg import CurriculumKG
from core.learner import LearnerState, MasteryLevel, ProficiencyLevel

kg = CurriculumKG()


def create_learner_state(user_id: str):
    concept_ids = kg.all_concept_ids()

    learner_doc = {
        "user_id": user_id,
        "concepts": {
            cid: {
                "score": 0.0,
                "mastery": "unknown",
                "level": "unknown",
                "attempts": 0,
                "history": [],
                "last_updated": None,
            } for cid in concept_ids
        },
        "proficiency_level": "unassessed",
        "onboarding_complete": False,
        "proficiency_assessment_results": None,
        "learning_deadline": None,
        "learning_goals": [],
        "timeline_adjustments": [],
        "weak_points": {},
        "canonical_position": 0,
        "current_plan": None,
        "current_analysis": None,
    }

    learner_collection.update_one(
        {"user_id": user_id},
        {"$setOnInsert": learner_doc},
        upsert=True,
    )
    return learner_doc


def update_concept(user_id, concept_id, score, mastery):
    learner_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"concepts.{concept_id}.score": score,
                f"concepts.{concept_id}.mastery": mastery,
                f"concepts.{concept_id}.level": mastery,
            },
            "$inc": {
                f"concepts.{concept_id}.attempts": 1
            }
        },
        upsert=True,
    )


def persist_learner_state(
    learner: LearnerState,
    canonical_position: int = 0,
    current_plan=None,
    current_analysis=None,
):
    concepts = {}
    for cid, state in learner.states.items():
        concepts[cid] = {
            "score": state.score,
            "mastery": state.level.value,
            "level": state.level.value,
            "attempts": state.attempts,
            "history": [
                {
                    "score": item.get("score", 0.0),
                    "level": getattr(item.get("level"), "value", item.get("level", "unknown")),
                    "timestamp": item.get("timestamp"),
                }
                for item in state.history
            ],
            "last_updated": state.last_updated,
        }

    update_doc = {
        "user_id": learner.learner_id,
        "concepts": concepts,
        "proficiency_level": learner.proficiency_level.value,
        "onboarding_complete": learner.onboarding_complete,
        "proficiency_assessment_results": learner.proficiency_assessment_results,
        "learning_deadline": learner.learning_deadline,
        "learning_goals": learner.learning_goals,
        "timeline_adjustments": learner.timeline_adjustments,
        "weak_points": learner.weak_points,
        "canonical_position": canonical_position,
    }
    if current_plan is not None:
        update_doc["current_plan"] = current_plan
    if current_analysis is not None:
        update_doc["current_analysis"] = current_analysis

    learner_collection.update_one(
        {"user_id": learner.learner_id},
        {"$set": update_doc},
        upsert=True,
    )


def load_learner_state(user_id: str):
    doc = learner_collection.find_one({"user_id": user_id})
    if not doc:
        return None, 0

    learner = LearnerState(user_id, kg.all_concept_ids())

    for cid, stored in (doc.get("concepts") or {}).items():
        state = learner.get(cid)
        state.score = stored.get("score", 0.0)
        level_name = stored.get("level") or stored.get("mastery") or "unknown"
        try:
            state.level = MasteryLevel(level_name)
        except ValueError:
            state.level = MasteryLevel.UNKNOWN
        state.attempts = stored.get("attempts", 0)
        state.last_updated = stored.get("last_updated")
        state.history = [
            {
                "score": item.get("score", 0.0),
                "level": MasteryLevel(item.get("level", "unknown")),
                "timestamp": item.get("timestamp"),
            }
            for item in stored.get("history", [])
        ]

    try:
        learner.proficiency_level = ProficiencyLevel(
            doc.get("proficiency_level", "unassessed")
        )
    except ValueError:
        learner.proficiency_level = ProficiencyLevel.UNASSESSED

    learner.onboarding_complete = doc.get("onboarding_complete", False)
    learner.proficiency_assessment_results = doc.get("proficiency_assessment_results")
    learner.learning_deadline = doc.get("learning_deadline")
    learner.learning_goals = doc.get("learning_goals", [])
    learner.timeline_adjustments = doc.get("timeline_adjustments", [])
    learner.weak_points = doc.get("weak_points", {})

    return learner, doc.get("canonical_position", 0)
