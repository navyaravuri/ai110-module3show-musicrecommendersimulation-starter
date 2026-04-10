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

# Genres grouped by sonic similarity — used for diversity penalties in recommend_songs.
# If a song's genre is in the same group as a genre already in the results list,
# it receives a genre-repeat penalty even though the label differs.
GENRE_GROUPS: Dict[str, set] = {
    "rock":      {"rock", "metal"},
    "metal":     {"metal", "rock"},
    "pop":       {"pop", "indie pop"},
    "indie pop": {"indie pop", "pop"},
    "lofi":      {"lofi", "ambient"},
    "ambient":   {"ambient", "lofi"},
    "jazz":      {"jazz", "blues"},
    "blues":     {"blues", "jazz"},
    "folk":      {"folk", "country"},
    "country":   {"country", "folk"},
    "hip-hop":   {"hip-hop", "r&b"},
    "r&b":       {"r&b", "hip-hop"},
    "classical": {"classical"},
    "synthwave": {"synthwave"},
    "edm":       {"edm"},
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
        ("target_energy",       "energy",       1.25, "energy"),
        ("target_acousticness", "acousticness", 1.25, "acousticness"),
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
# recommend_songs() scores all songs with sorted() first (no mutation),
# then builds the final top-k list iteratively so a diversity penalty
# can be applied each round. Both steps avoid mutating the caller's data.

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """Score all songs and return the top k as (song, score, reasons) tuples with diversity penalty applied."""

    # Step 1 — score every song once, leaving the caller's list untouched
    scored = sorted(
        [(song, *score_song(user_prefs, song)) for song in songs],
        key=lambda x: x[1],
        reverse=True,
    )

    # Step 2 — greedy iterative selection with tiered diversity penalties.
    #   Artist repeat : -1.50  (strong suppression — same artist twice feels repetitive)
    #   Genre-group repeat : -0.75  (softer — similar genres can still appear but deprioritised)
    # Penalties stack: a song that repeats both artist and genre group loses 2.25.
    # Raw scores in `scored` are never modified.
    results = []
    remaining = list(scored)

    while len(results) < k and remaining:
        selected_artists = {r[0]["artist"] for r in results}
        selected_genres  = {r[0]["genre"]  for r in results}

        # Build the full set of genres "blocked" by similarity groups
        blocked_genres: set = set()
        for g in selected_genres:
            blocked_genres.update(GENRE_GROUPS.get(g, {g}))

        best_score = float("-inf")
        best_idx   = 0

        for i, (song, score, _) in enumerate(remaining):
            adjusted = score
            if song["artist"] in selected_artists:
                adjusted -= 1.50
            if song["genre"] in blocked_genres:
                adjusted -= 0.75
            if adjusted > best_score:
                best_score = adjusted
                best_idx   = i

        song, raw_score, reasons = remaining.pop(best_idx)

        # Append only the penalties that actually fired this round
        penalty_reasons = []
        if song["artist"] in selected_artists:
            penalty_reasons.append("artist repeat (-1.50)")
        if song["genre"] in blocked_genres:
            penalty_reasons.append("genre group repeat (-0.75)")
        if penalty_reasons:
            reasons = reasons + penalty_reasons

        results.append((song, best_score, reasons))

    return results
