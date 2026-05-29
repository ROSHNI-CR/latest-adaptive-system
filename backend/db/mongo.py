from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError
import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not set")


def _normalized_mongo_uri(uri: str) -> tuple[str, str]:
    parts = urlsplit(uri)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.setdefault("retryWrites", "true")
    query.setdefault("w", "majority")
    db_name = parts.path.lstrip("/") or "adaptive_learning"
    normalized = urlunsplit((
        parts.scheme,
        parts.netloc,
        f"/{db_name}",
        urlencode(query),
        parts.fragment,
    ))
    return normalized, db_name


normalized_uri, db_name = _normalized_mongo_uri(MONGO_URI)

try:
    client = MongoClient(normalized_uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
except OperationFailure as exc:
    raise RuntimeError(
        "MongoDB authentication failed. Check the username/password in "
        "backend/.env MONGO_URI and confirm the Atlas database user exists."
    ) from exc
except PyMongoError as exc:
    raise RuntimeError(
        "MongoDB connection failed. Check MONGO_URI, Atlas network access, "
        "and cluster availability."
    ) from exc

db = client[db_name]

users_collection = db["users"]
learner_collection = db["learner_state"]

print(f"MongoDB connected successfully to database '{db_name}'")
