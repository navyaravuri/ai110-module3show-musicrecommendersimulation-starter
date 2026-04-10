# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**TuneFit 1.0**

---

## 2. Intended Use

TuneFit 1.0 is a classroom simulation of how content-based music recommendation works. It is not meant for real users or production use — the catalog is tiny and the preferences are hand-coded. The goal is to show how a system can take a description of someone's taste and turn it into a ranked list of songs by doing math on audio features. It assumes the user can describe what they want in advance (preferred genre, mood, energy level, etc.), which is a simplification of how real music apps work. Think of it as a teaching tool, not a product.

---

## 3. How the Model Works

The idea is simple: every song in the catalog gets a score based on how closely it matches what the user said they want. The closer a song is to the user's preferences, the higher its score.

There are two types of signals the model uses. The first is labels — does the song's genre match the user's favorite genre? Does its mood match? These are worth fixed bonus points: a genre match gives +2.0 and an exact mood match gives +1.5. If the mood isn't an exact match but is in the same family (for example, "relaxed" when the user asked for "chill"), the song still gets partial credit of +0.75.

The second type is audio features. The model looks at five numbers for each song — energy, acousticness, valence (how happy or sad it sounds), danceability, and tempo — and compares each one to the user's target. The closer the song's value is to the target, the more points it earns. Higher-weighted features like energy and acousticness can contribute up to 1.25 points each. Tempo is treated differently because it's measured in beats per minute instead of a 0–1 scale, so the gap is divided by 100 before scoring.

Once every song has a total score, they are sorted from highest to lowest and the top five are returned, along with a plain-language explanation of what contributed to each score.

---

## 4. Data

The catalog contains 18 songs. Each song has seven attributes: genre, mood, energy (0–1), acousticness (0–1), valence (0–1), danceability (0–1), and tempo in beats per minute. The catalog covers 15 genres including lofi, rock, classical, hip-hop, metal, folk, blues, r&b, country, edm, and more, and 12 moods ranging from chill and focused to angry, euphoric, and romantic. Eight songs were added during development to expand genre and mood coverage beyond the original starter set.

The dataset is very small and unevenly distributed. Lofi has three songs and pop has two, but every other genre has exactly one. This means the model cannot compare multiple options within most genres — there is only one classical song, one rock song, one jazz song, and so on. Musical tastes that don't map onto any existing genre or mood label in the catalog (reggae, for example) will never get a genre match at all. The data reflects a narrow slice of musical diversity and should not be taken as representative.

---

## 5. Strengths

The system works best when the user's preferences align closely with a well-represented genre. The Chill Lofi profile is the clearest example — three lofi songs exist in the catalog, all with consistent audio features, and the top three results all made intuitive sense with high scores above 8.0. The mood soft-matching also works well in practice: a user asking for "chill" music still surfaces "relaxed" and "focused" songs in the lower ranks rather than leaving those slots empty, which feels more useful than a strict binary match. The reasons printed alongside each result make the scoring transparent — you can see exactly why a song ranked where it did, which is something real recommenders rarely show you.

---

## 6. Limitations and Bias

The most significant weakness is genre monopoly: 13 of the 15 genres in the catalog have exactly one song, which means the +2.0 genre bonus permanently locks that single song into the top position for any user of that genre — even when it mismatches every numeric target. Testing confirmed this directly: a user asking for high-energy classical music received Midnight Sonata (energy 0.22) as their top result because the genre label outweighed five badly-scored audio features combined. A second structural bias exists in the relationship between energy and acousticness: every high-energy song in the catalog has very low acousticness and vice versa, with no songs occupying the high-energy acoustic space, so a user who enjoys energetic acoustic music (such as live folk or acoustic punk) cannot be matched accurately — the two most heavily weighted features point in opposite directions with nothing in the catalog to satisfy both. Finally, when a user's preferred genre does not appear in the catalog at all, the maximum achievable score silently drops from 9.0 to 7.0 because the genre bonus never fires, but the output still displays scores out of 9.0 with no warning that the genre preference went completely unmet — a quiet failure that is easy to miss.

---

## 7. Evaluation

Five user profiles were tested: Chill Lofi, High-Energy Rock, Deep Intense Rock, a Classical adversarial profile designed to expose genre-anchoring bias, and a Reggae profile where the genre does not appear in the catalog at all.

**Chill Lofi** returned Library Rain and Midnight Coding tied at 8.71/9.0, with Focus Flow close behind at 8.12. All three are lofi songs, and the top two both carry an exact mood match — the results matched intuition closely.

**High-Energy Rock** correctly surfaced Storm Runner (8.37) as a clear #1, with a gap of over 2.5 points to #2 Gym Hero. Because there is only one rock song in the catalog, the genre bonus had nowhere to spread and the remaining results were filled by non-rock songs with strong numeric proximity.

**Deep Intense Rock** also returned Storm Runner at #1 (7.22), but with a smaller lead than High-Energy Rock because its target values (energy=0.97, tempo=165, angry mood) were a closer numeric fit for Blackout Riff (metal) than for Storm Runner (rock). The genre label was the only reason Storm Runner won.

**Classical adversarial** — the most revealing test — returned Midnight Sonata at #1 (5.30) despite targeting energy=0.95, acousticness=0.05, and tempo=160, the exact opposite of Midnight Sonata's actual values (energy=0.22, acousticness=0.96, tempo=68). Blackout Riff, which was numerically almost perfect for the targets, ranked #2 at 5.33 — losing by only 0.06 points because it had no genre or mood bonus to draw from.

**Reggae (no genre in catalog)** showed the system fall back cleanly to mood and numeric proximity, with Focus Flow at 5.30 and a tight cluster below it. However, the scores displayed as out of 9.0 with no indication that the genre bonus was permanently unavailable, making the results appear weaker than expected without explanation.

Two experiments were also run to stress-test the weights. Doubling the energy weight and halving the genre weight fixed the Classical adversarial problem but broke the rock profiles. Removing mood matching entirely caused the Chill Lofi profile to surface a "focused" study song as its top result instead of an actual chill track, showing that mood is a load-bearing signal the system cannot function well without. The most surprising finding overall was that Storm Runner and Blackout Riff each appeared in the top 3 across three of the five profiles — including profiles where neither had any genre or mood match — confirming that a small catalog amplifies the influence of individual songs regardless of weight tuning.

A diversity penalty was then added to the recommendation logic to address this. Artist repeats carry a -1.50 deduction and genre-group repeats (defined by a GENRE_GROUPS lookup that treats rock and metal as the same group, jazz and blues as the same group, and so on) carry a -0.75 deduction; both penalties can stack on the same song. This resolved the co-appearance problem in the Classical adversarial profile, where Storm Runner was correctly pushed to #5 after Blackout Riff claimed the metal/rock group slot at #2, and in High-Energy Rock, where Blackout Riff dropped from #3 to #5. However, in Deep Intense Rock, Storm Runner and Blackout Riff still both appear because Blackout Riff's raw score advantage over the next competitor is 1.69 points — larger than the 0.75 genre-group penalty can overcome. Fully resolving this would require either raising the genre-group penalty above the score gap (which would distort results in other profiles) or introducing a hard cap that limits one song per genre group regardless of score, which is a more structural change to the selection logic.

---

## 8. Future Work

The most impactful improvement would be a larger and more balanced dataset. Adding at least three songs per genre would break the one-song-per-genre lock-in and give the scoring logic room to actually compare options within a genre rather than defaulting to the only available match.

Beyond data, the hand-coded weights are a limitation. In a real system, weights would be learned from user feedback — if someone skips a song despite a high score, that's a signal the weight for that feature was wrong. Starting from fixed numbers works for a classroom demo but wouldn't scale to real users with diverse tastes.

Collaborative filtering would also open up a different kind of recommendation entirely. Right now the system only knows about audio features — it has no idea that people who like lofi also tend to enjoy ambient music, or that jazz and blues listeners often overlap. Learning from patterns across many users would let the system surface surprising but accurate recommendations that pure feature-matching would never find.

Finally, the system currently gives every user the same five results regardless of how many good matches exist. Adding a diversity mechanism — for example, capping how many songs from the same genre can appear in one list — would make the top five feel less repetitive when one genre dominates the catalog.

---

## 9. Personal Reflection

What was your biggest learning moment during this project?
Building this made it clear how much a recommendation system depends on the quality of its data before any algorithm comes into play. Spending time tuning weights felt productive, but the weight experiments showed that no amount of adjustment could compensate for a catalog with only one song per genre — the data ceiling was always the real constraint.

How did using AI tools help you, and when did you need to double-check them?
Claude Code accelerated the implementation, but I had to correct the reasons output format and push back on the initial weight suggestions — the tool needed direction, not just a prompt.

What surprised you about how simple algorithms can still "feel" like recommendations?
The most interesting moment was the Classical adversarial test, which showed that a genre label alone can outweigh five audio features combined and push a completely mismatched song to the top of the list. That felt surprising at first, but it mirrors something real: streaming apps also over-rely on genre and playlist labels in ways that can feel off when you actually listen to the results.

What would you try next if you extended this project?
The transparency of the reasons output — seeing every contribution printed line by line — made it much easier to debug and understand the system than if it had just returned a ranked list with no explanation. That kind of explainability feels like something real recommendation systems should offer more of.
