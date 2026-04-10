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
    print(f"Loaded {len(songs)} songs.")

    profiles = [
        # --- Adversarial profiles ---

        # Only 1 classical song exists (Midnight Sonata: energy=0.22, acousticness=0.96,
        # tempo=68). Targets are its exact opposite. Tests whether the +2.0 genre bonus
        # pulls a numerically terrible match to the top anyway.
        ("ADVERSARIAL — High-Energy Classical (conflicting preferences)", {
            "favorite_genre": "classical",
            "favorite_mood": "sad",
            "target_energy": 0.95,
            "target_valence": 0.20,
            "target_acousticness": 0.05,
            "target_danceability": 0.60,
            "target_tempo_bpm": 160,
        }),

        # 'reggae' has zero songs in the catalog — genre bonus never fires.
        # Max achievable score drops from 9.0 to 7.0. Tests graceful fallback
        # to mood + numeric proximity when genre matching is impossible.
        ("ADVERSARIAL — Reggae Fan (genre not in catalog)", {
            "favorite_genre": "reggae",
            "favorite_mood": "focused",
            "target_energy": 0.65,
            "target_valence": 0.75,
            "target_acousticness": 0.45,
            "target_danceability": 0.82,
            "target_tempo_bpm": 100,
        }),

        # --- Standard profiles ---
        ("High-Energy Rock", {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.88,
            "target_valence": 0.50,
            "target_acousticness": 0.10,
            "target_danceability": 0.65,
            "target_tempo_bpm": 145,
        }),
        ("Chill Lofi", {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.38,
            "target_valence": 0.65,
            "target_acousticness": 0.78,
            "target_danceability": 0.55,
            "target_tempo_bpm": 78,
        }),
        ("Deep Intense Rock", {
            "favorite_genre": "rock",
            "favorite_mood": "angry",
            "target_energy": 0.97,
            "target_valence": 0.25,
            "target_acousticness": 0.05,
            "target_danceability": 0.60,
            "target_tempo_bpm": 165,
        }),
    ]

    all_results = {}

    for profile_name, user_prefs in profiles:
        print(f"\n{'=' * 40}")
        print(f"  {profile_name}")
        print(f"{'=' * 40}")
        recommendations = recommend_songs(user_prefs, songs, k=5)
        all_results[profile_name] = recommendations

        PENALTY_AMOUNTS = {"artist repeat (-1.50)": 1.50, "genre group repeat (-0.75)": 0.75}

        for rank, (song, score, reasons) in enumerate(recommendations, start=1):
            total_penalty = sum(PENALTY_AMOUNTS[r] for r in reasons if r in PENALTY_AMOUNTS)
            print(f"#{rank}  {song['title']} — {song['artist']}")
            if total_penalty:
                print(f"    Score: {score + total_penalty:.2f} → {score:.2f} / 9.0  [diversity penalty: -{total_penalty:.2f}]")
            else:
                print(f"    Score: {score:.2f} / 9.0")
            for reason in reasons:
                print(f"    • {reason}")
            print("-" * 40)

    # --- Post-run diversity audit ---
    print(f"\n{'=' * 40}")
    print("  DIVERSITY AUDIT")
    print(f"{'=' * 40}")

    for profile_name, recommendations in all_results.items():
        titles  = [s["title"]  for s, _, _ in recommendations]
        artists = [s["artist"] for s, _, _ in recommendations]
        genres  = [s["genre"]  for s, _, _ in recommendations]

        duplicate_artists = [a for a in set(artists) if artists.count(a) > 1]
        storm_and_black   = (
            any("Storm Runner"  in t for t in titles) and
            any("Blackout Riff" in t for t in titles)
        )

        print(f"\n{profile_name}")
        print(f"  Artists : {', '.join(artists)}")
        print(f"  Genres  : {', '.join(genres)}")
        if duplicate_artists:
            print(f"  ⚠ Duplicate artist(s): {', '.join(duplicate_artists)}")
        else:
            print(f"  ✓ No duplicate artists")
        if storm_and_black:
            print(f"  ⚠ Storm Runner + Blackout Riff both appear")
        else:
            print(f"  ✓ Storm Runner and Blackout Riff not both present")


if __name__ == "__main__":
    main()
