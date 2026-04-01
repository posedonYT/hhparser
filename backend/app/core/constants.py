from app.db.models import ExperienceBucket, Track

TRACK_QUERY_MAP = {
    Track.python_backend: "Python backend",
    Track.swift: "Swift",
}

EXPERIENCE_BUCKET_ORDER = [
    ExperienceBucket.no_experience,
    ExperienceBucket.between_1_and_3,
    ExperienceBucket.between_3_and_6,
    ExperienceBucket.more_than_6,
]

EXPERIENCE_LABELS = {
    ExperienceBucket.no_experience: "0",
    ExperienceBucket.between_1_and_3: "1-3",
    ExperienceBucket.between_3_and_6: "3-6",
    ExperienceBucket.more_than_6: "6+",
}

ALL_TRACKS = tuple(TRACK_QUERY_MAP.keys())
