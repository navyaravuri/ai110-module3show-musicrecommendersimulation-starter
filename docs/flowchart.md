# Music Recommender — Data Flow

```mermaid
flowchart TD
    %% ── Inputs ──────────────────────────────────────────────────────────
    UP["User Profile
    ──────────────
    favorite_genre
    favorite_mood
    target_energy
    target_acousticness
    target_valence
    target_danceability
    target_tempo_bpm"]

    CSV[("songs.csv")]

    %% ── Loading ─────────────────────────────────────────────────────────
    LOAD["load_songs()
    Parse CSV rows
    Cast numeric fields to float"]

    CSV --> LOAD

    %% ── Scoring loop ─────────────────────────────────────────────────────
    LOOP{{"For each song\nin song list"}}

    LOAD --> LOOP
    UP   --> LOOP

    %% ── Score components ─────────────────────────────────────────────────
    G["Genre match
    +2.0 if exact"]

    M["Mood match
    +1.5 exact
    +0.75 related group
    +0.0 no match"]

    E["Energy proximity
    weight 1.5
    1 − |target − song|"]

    AC["Acousticness proximity
    weight 1.5
    1 − |target − song|"]

    VA["Valence proximity
    weight 1.0
    1 − |target − song|"]

    TP["Tempo proximity
    weight 1.0
    1 − |target − song| ÷ 100"]

    DA["Danceability proximity
    weight 0.5
    1 − |target − song|"]

    LOOP --> G
    LOOP --> M
    LOOP --> E
    LOOP --> AC
    LOOP --> VA
    LOOP --> TP
    LOOP --> DA

    %% ── Aggregation ──────────────────────────────────────────────────────
    SUM["Sum weighted components
    → final score (0 – 9.0)
    Collect reason strings"]

    G  --> SUM
    M  --> SUM
    E  --> SUM
    AC --> SUM
    VA --> SUM
    TP --> SUM
    DA --> SUM

    %% ── Accumulate & sort ────────────────────────────────────────────────
    ACC["Accumulate
    (song, score, reasons)
    for all songs"]

    SUM --> ACC

    NEXT{"More songs?"}
    ACC --> NEXT
    NEXT -- Yes --> LOOP
    NEXT -- No  --> SORT

    SORT["Sort descending by score"]

    %% ── Output ───────────────────────────────────────────────────────────
    TOPK["Slice top K results"]
    SORT --> TOPK

    OUT["Output
    ──────────────────────────
    song title · score
    explanation (reason list)"]

    TOPK --> OUT

    %% ── Styles ───────────────────────────────────────────────────────────
    classDef input    fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    classDef process  fill:#f0fdf4,stroke:#22c55e,color:#14532d
    classDef score    fill:#fefce8,stroke:#eab308,color:#713f12
    classDef output   fill:#fdf4ff,stroke:#a855f7,color:#3b0764
    classDef decision fill:#fff7ed,stroke:#f97316,color:#7c2d12

    class UP,CSV input
    class LOAD,SUM,ACC,SORT,TOPK process
    class G,M,E,AC,VA,TP,DA score
    class OUT output
    class LOOP,NEXT decision
```

## Weight reference

| Component | Weight | Match type |
|---|---|---|
| Genre | 2.0 | Exact categorical |
| Mood (exact) | 1.5 | Exact categorical |
| Mood (related group) | 0.75 | Soft categorical |
| Energy | 1.5 | Proximity `1 − \|Δ\|` |
| Acousticness | 1.5 | Proximity `1 − \|Δ\|` |
| Valence | 1.0 | Proximity `1 − \|Δ\|` |
| Tempo | 1.0 | Proximity `1 − \|Δ\| ÷ 100` |
| Danceability | 0.5 | Proximity `1 − \|Δ\|` |
| **Max total** | **9.0** | |
