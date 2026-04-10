# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

The most surprising finding was that Storm Runner and Blackout Riff each appeared in the top 3 across three of the five profiles — including the Classical profile where neither had any genre or mood match. This happened because energy and acousticness were weighted at 1.5 each, giving numerically extreme songs a gravity pull across profiles. Lowering both weights to 1.25 reduced individual scores but did not change the cross-profile count, confirming the underlying cause was catalog size rather than weighting alone.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
