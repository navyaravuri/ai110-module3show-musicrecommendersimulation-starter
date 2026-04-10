"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    # Chill lofi study-session listener profile
    user_prefs = {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.38,
        "target_valence": 0.65,
        "target_acousticness": 0.78,
        "target_danceability": 0.55,
        "target_tempo_bpm": 78,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    print("-" * 40)
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"#{rank}  {song['title']} — {song['artist']}")
        print(f"    Score: {score:.2f} / 9.0")
        for reason in reasons:
            print(f"    • {reason}")
        print("-" * 40)


if __name__ == "__main__":
    main()
