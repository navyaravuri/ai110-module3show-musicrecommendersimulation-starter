import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Moods grouped by similarity — used for soft matching in score_song.
# An exact match scores full credit; a related-group match scores half.
MOOD_GROUPS: Dict[str, set] = {
    "chill":      {"chill", "relaxed", "focused"},
    "relaxed":    {"relaxed", "chill", "focused"},
    "focused":    {"focused", "chill", "relaxed"},
    "intense":    {"intense", "energetic", "angry"},
    "energetic":  {"energetic", "intense", "angry"},
    "angry":      {"angry", "intense", "energetic"},
    "happy":      {"happy", "euphoric", "uplifting"},
    "euphoric":   {"euphoric", "happy", "uplifting"},
    "uplifting":  {"uplifting", "happy", "euphoric"},
    "sad":        {"sad", "melancholic"},
    "melancholic":{"melancholic", "sad", "moody"},
    "moody":      {"moody", "melancholic"},
    "romantic":   {"romantic"},
}

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read a CSV of songs and return a list of dicts with correctly typed fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            row["energy"] = float(row["energy"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences using weighted genre, mood, and feature proximity."""
    score = 0.0
    reasons: List[str] = []

    # --- Genre (exact match) ---
    if song.get("genre") == user_prefs.get("favorite_genre"):
        score += 2.0
        reasons.append("genre match (+2.0)")

    # --- Mood (soft match) ---
    user_mood = user_prefs.get("favorite_mood", "")
    song_mood = song.get("mood", "")
    related = MOOD_GROUPS.get(user_mood, {user_mood})
    if song_mood == user_mood:
        score += 1.5
        reasons.append("exact mood match (+1.50)")
    elif song_mood in related:
        score += 0.75
        reasons.append("related mood match (+0.75)")

    # --- Numeric features ---
    numeric_features = [
        ("target_energy",       "energy",       1.5, "energy"),
        ("target_acousticness", "acousticness", 1.5, "acousticness"),
        ("target_valence",      "valence",       1.0, "valence"),
        ("target_danceability", "danceability",  0.5, "danceability"),
    ]
    for pref_key, song_key, weight, label in numeric_features:
        if pref_key in user_prefs and song_key in song:
            contribution = (1.0 - abs(float(user_prefs[pref_key]) - float(song[song_key]))) * weight
            score += contribution
            reasons.append(f"{label} proximity (+{contribution:.2f})")

    # --- Tempo ---
    if "target_tempo_bpm" in user_prefs and "tempo_bpm" in song:
        contribution = max(0.0, 1.0 - abs(user_prefs["target_tempo_bpm"] - float(song["tempo_bpm"])) / 100)
        score += contribution
        reasons.append(f"tempo proximity (+{contribution:.2f})")

    return score, reasons


# sorted() vs .sort() — what's the difference?
#
# list.sort()  — mutates the list in place, returns None.
#                The original list is permanently reordered.
#
# sorted()     — leaves the original list untouched and returns
#                a brand-new sorted list.
#
# Why sorted() is the right choice here:
# recommend_songs() receives `songs` from the caller (main.py or a test).
# Sorting it in place with .sort() would silently reorder the caller's
# data as a side effect — a hidden mutation that could cause confusing
# bugs if the list is reused or inspected after the call.
# sorted() keeps recommend_songs() a pure function: same inputs always
# produce the same output, and nothing outside the function is changed.

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """Score all songs and return the top k as (song, score, reasons) tuples sorted by score descending."""
    scored = []
    for song in songs:
        song_score, reasons = score_song(user_prefs, song)
        scored.append((song, song_score, reasons))

    # sorted() returns a new list — the original `songs` list is never touched
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
