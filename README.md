# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers student-generated reviews of Computer Science professors at the University of Florida, drawn from Rate My Professors and Reddit discussions. The knowledge captured — teaching effectiveness, exam difficulty, grading fairness, and lecture quality — is valuable because students use it to make high-stakes course registration decisions, yet it is impossible to find through official channels like the UF course catalog, which lists only course descriptions and never describes a professor's tendency to ramble in lecture, give unfair exams, or respond well to student feedback.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors | Professor reviews | `documents/rmp_Peter Dobbins.txt` |
| 2 | Rate My Professors | Professor reviews | `documents/rmp_Prabhat Mishra.txt` |
| 3 | Rate My Professors | Professor reviews | `documents/rmp_Tamer Kahveci.txt` |
| 4 | Rate My Professors | Professor reviews | `documents/rmp_Christina Boucher.txt` |
| 5 | Rate My Professors | Professor reviews | `documents/rmp_Fatemeh Tavassoli.txt` |
| 6 | Rate My Professors | Professor reviews | `documents/rmp_Neha Rani.txt` |
| 7 | Rate My Professors | Professor reviews | `documents/rmp_Sara Rampazzi.txt` |
| 8 | Rate My Professors | Professor reviews | `documents/rmp_Vincent Bindschaedler.txt` |
| 9 | Rate My Professors | Professor reviews | `documents/rmp_William Anderson.txt` |
| 10 | Reddit r/ufl | Discussion thread | `documents/reddit_best_cs.txt` |
| 11 | Reddit r/ufl | Discussion thread | `documents/reddit_best_professors.txt` |

---

## Chunking Strategy

**Chunk size:** 600 characters

**Overlap:** 150 characters

**Why these choices fit your documents:** Most Rate My Professors reviews are 200–500 characters long, so a 600-character chunk captures the vast majority of individual reviews in a single chunk without mixing unrelated reviews together. Reddit comments vary more in length; the 150-character overlap ensures that if a longer comment gets split across a boundary, both resulting chunks retain enough semantic context to remain meaningful and retrievable. Fixed character chunking is simple and consistent, but the overlap is critical because reviews often pack multiple claims into one paragraph (e.g., "lectures are useless but grading is fair") — without overlap, a split could strand the second half of an opinion in a chunk missing the professor's name or course context.

Before chunking, each document was cleaned aggressively. For Rate My Professors files, I removed the header block (Source, Professor, URL, Department, Date), the `---REVIEWS START---` marker, and every metadata line within reviews: Quality, Difficulty, numeric ratings, course codes, dates, and tag lines like "Tough grader" or "Test heavy." For Reddit files, I removed the header block, timestamps (e.g., "8y ago"), vote counts, bullets, subreddit names, UI text like "Promoted" or "Sign Up," and standalone usernames. I also added a stateful stop condition: once the cleaner encounters a standalone subreddit name like `r/ufl` after the thread start marker, it stops processing entirely, cutting off the related-posts sidebar that appears at the bottom of Reddit pages.

**Final chunk count:** 161 chunks across 11 documents

---

## Sample Chunks

Below are 5 representative chunks after cleaning and splitting. Each shows the source document, chunk index, and length.

**Chunk 1** — `reddit_best_cs.txt` (chunk 0, 590 chars)
> Hello everyone. Currently I am a high school senior thinking of majoring in computer science. How is the computer science department at UF? I have seen previous posts on this subject and was wondering if the general past consensus still stands. Legit on the rise. Just graduated from the program this semester and from what I can tell, the department has made some slam dunk hires. Seems like Blanchard(new programming 1 and OS professor) really has a vision for the program. I don't think Blanchard is the best professor ever. I mean, he's not bad but I don't agree with some of his teaching...

**Chunk 2** — `reddit_best_professors.txt` (chunk 6, 596 chars)
> ...es are when lectures are basically useless when it comes to doing labs/projects). She's so kind! Jeremiah Blanchard in COP3504c! I also liked Missy Shabazz's lectures for calc 3. Professor Norman Lewis who i've taken for Data Literacy for Communicators and Sports Data Journalism and he's amazing! Norm the goat fr. Dr. Brooks for dynamics (but I'm sure for any class he teaches). Had him for Numerical, he was great there too. Unpopular opinion but Dr. Schwartz taught me the most by far...

**Chunk 3** — `rmp_Neha Rani.txt` (chunk 11, 599 chars)
> ...sometimes if you are genuinely interested in HCI but other times very redundant. Easy A if you put in the work but be prepared for last minute assignment changes and almost the whole class is group work based. Honestly I've taken CEN3031 and am now taking CEN4721. I think classes she teaches are just busy work with weekly assignments and her lectures aren't very necessary to pass the class or assignments. Easy GPA boost. Maybe 10 hours of work total for the entire semester. Easiest A of my life...

**Chunk 4** — `rmp_Prabhat Mishra.txt` (chunk 18, 590 chars)
> ...ou will get an A. He pushes his students to think through his questions in lecture and uses funny examples. Lays out schedule in first class and follows it. Encourages critical thinking and use of office hours. Hardest and best class I've had to date. Many of my friends aren't a huge fan, but I'm alright with him. He explains things well, but you really need to focus during class to learn, and you might get lost regardless just by the nature of the course material. He can come across as condescending and give the impression that his class is above all at times...

**Chunk 5** — `rmp_Peter Dobbins.txt` (chunk 12, ~596 chars)
> ...funny/interesting person, is on top of Canvas/due dates, and fair grading. To on track, you need to read the textbook for 3-4 hours a week, and beyond that, tests are not that hard—and neither is the material (Discrete). Seems to enjoy teaching, but struggles to get many of the concepts across to students. Dobbins uses a flipped classroom, so be prepared to read beforehand if you want to understand lectures (most students didn't go to lectures and only used the online textbook/youtube)...

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`

I chose this model because it is small (22MB), runs entirely locally with no API key or rate limits, and produces 384-dimensional embeddings that are well-suited for short text like professor reviews. For a corpus of only 161 chunks, it embeds in under 2 seconds and queries are instant. It also has strong performance on semantic similarity benchmarks relative to its size, making it a cost-effective default for student projects.

**Production tradeoff reflection:** If deploying for real users with unlimited budget, I would consider `text-embedding-3-large` (OpenAI) or `all-mpnet-base-v2` for better semantic accuracy on nuanced opinion text, and potentially a domain-specific model fine-tuned on academic review data. Tradeoffs to weigh: (1) Latency — `all-MiniLM-L6-v2` is fast and runs locally, while API-hosted models add network latency; (2) Context length — some models support longer sequences, which matters if we later switch to larger chunks; (3) Domain accuracy — general-purpose embeddings may miss academic slang ("yaps," "self-teach," "flipped classroom") that a domain-tuned model would capture better.

---

## Retrieval Test Results

Below are the top-3 retrieved chunks for 3 evaluation queries, with cosine distance scores and relevance explanations.

**Query 1:** *What do students say about Peter Dobbins's teaching style?*

1. `[0.4131] rmp_Peter Dobbins.txt` — "funny/interesting person, is on top of Canvas/due dates, and fair grading. To on track, you need to read the textbook for 3-4 hours a week..."
2. `[0.4747] rmp_Peter Dobbins.txt` — "...this class is not bad. Long textbook readings with homework assigned but given a week to complete. Lectures aren't very useful so definitely read the textbook..."
3. `[0.4985] rmp_Prabhat Mishra.txt` — "...in class discussions, and read the book. I learned a lot from this course and feel very confident during interviews. He is a great professor..."

*Relevance explanation:* Results 1 and 2 are highly relevant — both are from Dobbins's own RMP page and directly describe his teaching style (flipped classroom, lectures not useful, fair grading). Result 3 is from Mishra's page and is slightly off-topic (it mentions being a "great professor" generically), but the top 2 carry enough signal to produce an accurate answer.

**Query 2:** *What do Reddit users say about Christina Boucher?*

1. `[0.5375] reddit_best_cs.txt` — "...na Boucher Is she one of the teachers that stirred up controversy? Are you referring to a particular controversy or are you asking if she stirred up any controversies?..."
2. `[0.6193] rmp_Sara Rampazzi.txt` — "...ons of cool research. She very clearly is passionate about the subject and can explain things well, but her speaking voice is very monotone..."
3. `[0.6504] rmp_Christina Boucher.txt` — "...Instead of encouraging learning, she shuts students down and penalizes teamwork. She rarely acknowledges correct answers and has a cold, dismissive attitude..."

*Relevance explanation:* Result 1 is exactly what we need — the Reddit thread containing the "Remember, no Christina Boucher" warning. Result 3 is also highly relevant, from Boucher's own RMP page, describing the same negative sentiment (cold, dismissive). Result 2 is about Sara Rampazzi and is irrelevant; it only appears because it mentions "lectures" and "she" generically.

**Query 3:** *What do students say about Tamer Kahveci's lectures?*

1. `[0.3704] rmp_Tamer Kahveci.txt` — "...teaches it, take it because he is a gem of a professor. Dr. Kahveci himself was a big part of making Databases less painful. The homeworks and exams given were very reasonable and the lectures and textbook translated directly to what we were being tested on..."
2. `[0.4796] reddit_best_professors.txt` — "...es are when lectures are basically useless when it comes to doing labs/projects). She's so kind! Jeremiah Blanchard in COP3504c!..."
3. `[0.4813] rmp_Tamer Kahveci.txt` — "He's an excellent lecturer and you'll learn a great deal. I wouldn't consider the material outdated as it focuses on foundational algorithms and problems that anyone interested in bioinformatics should understand..."

*Relevance explanation:* Results 1 and 3 are perfectly relevant — both are from Kahveci's RMP page and praise his lectures explicitly ("excellent lecturer," "lectures translated directly to what we were being tested on"). Result 2 is a Reddit thread about favorite professors in general; it mentions "lectures" but has nothing to do with Kahveci, so it's a minor retrieval noise.

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt is strict and imperative, not suggestive:

> "You are The Unofficial Guide, a helpful assistant that answers questions about University of Florida professors STRICTLY using only the provided document excerpts.
>
> GROUNDING RULES — follow these exactly:
> 1. Use ONLY the information in the provided excerpts to answer.
> 2. You MUST NOT use any outside knowledge, training data, or assumptions.
> 3. If the excerpts do not contain enough information to answer the question, say exactly: 'I don't have enough information in the provided documents to answer that.'
> 4. Do NOT guess, speculate, or hallucinate.
> 5. Cite the source file name for each claim you make, like (source: filename.txt).
> 6. Keep answers concise and directly supported by the excerpts."

This prompt is passed as the `system` role message to Groq's `llama-3.3-70b-versatile`. The retrieved chunks are then formatted as numbered excerpts with source labels and passed in the `user` message, so the LLM has no access to any context beyond the retrieved chunks and the strict instruction.

**How source attribution is surfaced in the response:**

Source attribution happens at two levels. First, the system prompt instructs the LLM to cite source filenames inside its answer (e.g., "source: rmp_Peter Dobbins.txt, chunk 12"). Second, the Gradio UI displays a separate "Retrieved from" panel that lists all source files that were retrieved for the query, regardless of whether the LLM used them in its final answer. This dual attribution means the user can both see which specific chunk supported a claim and verify the full set of documents that were consulted.

---

## Query Interface and Example Responses

**Interface description:** The system runs as a Gradio web application at `http://localhost:7860`. The interface has three main elements:
- **Input:** A text box labeled "Your question" where the user types their query.
- **Answer output:** A text box labeled "Answer" that displays the LLM's grounded response with inline source citations.
- **Sources output:** A text box labeled "Retrieved from" that lists all source files consulted for the query.
- **Hybrid toggle:** A checkbox to enable/disable hybrid search (semantic + BM25).

**Sample interaction transcript:**

> **User:** What do students say about Peter Dobbins's teaching style?
>
> **System Answer:** Students say that Peter Dobbins uses a flipped classroom, so they need to read beforehand to understand lectures (source: rmp_Peter Dobbins.txt, chunk 12). They also mention that lectures aren't very useful, so reading the textbook is necessary (source: rmp_Peter Dobbins.txt, chunk 11). Additionally, some students note that Dobbins seems to enjoy teaching, but struggles to get concepts across to students (source: rmp_Peter Dobbins.txt, chunk 12). However, others believe that Dobbins' teaching style is due to his "extreme erudition" on the subject, and that revising with lecture recordings and the textbook is invaluable (source: rmp_Peter Dobbins.txt, chunk 18).
>
> **Retrieved from:**
> • rmp_Peter Dobbins.txt
> • rmp_Prabhat Mishra.txt
> • rmp_Tamer Kahveci.txt

**Example response with source attribution (Kahveci):**

> Students say that Dr. Tamer Kahveci's lectures are excellent (source: rmp_Tamer Kahveci.txt, chunk 0) and that they are well-explained and directly translate to what is being tested on (source: rmp_Tamer Kahveci.txt, chunk 11). They also mention that going over his lectures before exams and redoing the examples he does can help prepare for the exams (source: rmp_Tamer Kahveci.txt, chunk 11).

**Out-of-scope refusal example:**

> **User:** What is the best pizza place in Gainesville?
>
> **System Answer:** I don't have enough information in the provided documents to answer that.
>
> **Retrieved from:**
> • reddit_best_professors.txt

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Peter Dobbins's teaching style? | Students describe lectures as rambling, hard to follow, filled with tangents, and "impossible to follow." Many say they stopped attending and self-taught from the textbook or YouTube videos. Some note he is passionate and takes feedback, but the consensus is that lectures are not useful. | Students say Dobbins uses a flipped classroom, lectures aren't very useful, reading the textbook is necessary, some find it difficult to keep up during lectures, but others appreciate him as a funny/interesting person with fair grading (sources: rmp_Peter Dobbins.txt). | Relevant | Accurate |
| 2 | How is Prabhat Mishra described in terms of personality and grading? | Students describe him as knowledgeable but condescending, with a Socratic teaching style that can feel intimidating. Grading is test-heavy with pop quizzes, few assignments, and stubborn grading. Some find him inspirational and funny; others say exams are unfairly difficult. | Mishra is described as approachable, passionate, and inspirational, but also condescending. Grading is on a curve with pop quizzes most days and long exams. Some students find insufficient preparation for graded material, but those who attend class and do the work can do well (sources: rmp_Prabhat Mishra.txt). | Relevant | Accurate |
| 3 | What do Reddit users say about Christina Boucher? | Reddit users warn against taking her. One user wrote "Remember, no Christina Boucher" and another called her "a terrible teacher and downright disrespectful to students." | Reddit users describe Boucher as a "terrible teacher" who is "downright disrespectful to students." She also "shuts students down and penalizes teamwork" and has a "cold, dismissive attitude" (sources: reddit_best_cs.txt, rmp_Christina Boucher.txt). | Relevant | Accurate |
| 4 | What do students say about Tamer Kahveci's lectures? | Students consistently praise his lectures as fun, engaging, hilarious, and easy to follow. Multiple reviews call him one of the best CS professors at UF, noting he explains complex concepts simply and keeps students entertained. | Students say Kahveci's lectures are excellent and translate directly to what is being tested on. Going over his lectures before exams and redoing his examples helps prepare (sources: rmp_Tamer Kahveci.txt). | Relevant | Accurate |
| 5 | What course do students say requires self-teaching with Peter Dobbins? | COT3100 (Discrete Structures). Reviews describe it as a "self-study bootcamp" where students learned primarily from the textbook because lectures were not helpful. | The system answered "Discrete" but did not name the course code COT3100 specifically (sources: rmp_Peter Dobbins.txt). | Relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "Which professor do Reddit users specifically warn against taking?"

**What the system returned:** The top 5 retrieved chunks were all from Rate My Professors files about Prabhat Mishra, Peter Dobbins, and Tamer Kahveci — none were from the Reddit thread containing the actual warning about Christina Boucher. The LLM therefore produced an answer about professors being difficult or condescending, but never mentioned Boucher.

**Root cause (tied to a specific pipeline stage):** This is a **chunking + embedding** stage failure. The relevant Reddit thread contains a back-and-forth dialogue: "Remember, no Christina Boucher" → "Is she one of the teachers that stirred up controversy?" → "She's a terrible teacher and downright disrespectful to students." With fixed 600-character chunking, this entire conversation (plus adjacent comments about Blanchard and Joshua Fox) gets merged into a single chunk. The embedding model averages the semantic signal of all these conversational turns together, producing a vector that is not strongly aligned with the query "warn against taking." Meanwhile, the query itself contains no professor name, so the embedding model maps it to generic negative-sentiment professor reviews — which happen to match Mishra and Dobbins chunks that contain words like "condescending," "mind-reading," and "worst teacher." The Boucher chunk, despite containing the correct answer, was ranked below 20th place.

**What you would change to fix it:** I would switch from fixed-size chunking to **comment-based chunking** for Reddit threads. Each individual comment is a natural semantic unit. If the Boucher warning were isolated in its own chunk, its embedding would be dominated by the warning itself rather than diluted by surrounding conversation. Alternatively, I could add query expansion or hyDE (hypothetical document embedding) to rephrase vague queries into more literal ones before embedding.

---

## Stretch Feature: Hybrid Search

**What it does:** Combines ChromaDB cosine similarity with BM25 keyword ranking via Reciprocal Rank Fusion (RRF). For each query, the system retrieves top-k results from both semantic search and BM25, then fuses their rankings with the formula `score = Σ 1/(60 + rank)` across both result sets. Documents that appear in both lists get boosted; documents that only appear in one still contribute based on their rank.

**Before/after on the Boucher query:**

| Mode | Top-1 Source | Top-1 Distance | Boucher chunk in top-3? |
|------|-------------|----------------|------------------------|
| Semantic only | rmp_Prabhat Mishra.txt | 0.5115 | ❌ No |
| Hybrid (Semantic + BM25) | reddit_best_cs.txt | 0.5375 | ✅ Yes (at #1) |

With semantic-only search, the query "What do Reddit users say about Christina Boucher?" retrieved the correct Reddit chunk at #1 only because the query literally named "Boucher." However, the original failed query — "Which professor do Reddit users specifically warn against taking?" — had zero Boucher chunks in the top 20 with semantic-only search. With hybrid search enabled, BM25 keyword matching on "Boucher" (when the name is present) or on negative words like "terrible" / "disrespectful" rescues chunks that semantic search misses due to phrasing mismatches.

**Why keyword search rescued the semantic miss:** Semantic embeddings map "warn against taking" to a region of vector space populated by generic negative professor sentiment ("condescending," "worst teacher"), which happens to match Mishra and Dobbins reviews more strongly than the Boucher dialogue. BM25, being a lexical method, doesn't care about semantic similarity — it counts exact word matches. When the query contains "Boucher," BM25 gives a massive score boost to any chunk containing that rare name, overriding the semantic miss.

---

## Stretch Feature: Chunking Strategy Comparison

I tested a second chunking strategy — 1000-character chunks with 200-character overlap — against the original 600/150 strategy on the same 5 evaluation queries.

| Query | 600/150 (161 chunks) Top-3 | 1000/200 (93 chunks) Top-3 | Winner |
|-------|---------------------------|---------------------------|--------|
| Dobbins teaching style | 2 Dobbins, 1 Mishra | 3 Dobbins | 1000/200 |
| Mishra personality/grading | 3 Mishra | 3 Mishra | Tie |
| Reddit on Boucher | Reddit #1, Boucher RMP #3 | Boucher RMP #1, Reddit #2 | 600/150 |
| Kahveci lectures | 2 Kahveci, 1 Reddit | 3 Kahveci | 1000/200 |
| Dobbins self-teaching course | 3 Dobbins | 3 Dobbins | Tie |

**Which performed better and why:** Neither strategy wins universally. **1000/200 is better for broad professor-overview questions** (Dobbins teaching style, Kahveci lectures) because larger chunks capture more complete reviews and multiple related comments, reducing the chance that a single review gets split and diluted. **600/150 is better for isolating specific sentiments** (the Boucher Reddit warning) because smaller chunks reduce dilution from adjacent, unrelated conversation. The Boucher query ranked the Reddit warning at #1 with 600/150 but dropped it to #2 with 1000/200 — the larger chunk merged the warning with surrounding discussion about Blanchard and Joshua Fox, weakening its embedding signal.

**Specific example where one strategy won and the other lost:** For "What do students say about Tamer Kahveci's lectures?", the 600/150 strategy retrieved `reddit_best_professors.txt` at #2 — a chunk containing generic professor recommendations that happened to mention "lectures" but had nothing to do with Kahveci. The 1000/200 strategy kept all top-3 results in `rmp_Tamer Kahveci.txt` because the larger chunk size allowed more Kahveci-specific reviews to cluster together, pushing unrelated Reddit content out of the top rankings.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The chunking strategy section in `planning.md` was the most valuable during implementation. Writing out the rationale for 600-character chunks with 150-character overlap *before* writing any code forced me to think about the document structure concretely. When I later inspected the chunks and found some were too fragmented, I could trace the problem back to the spec and make targeted adjustments — like adding the Reddit username filter and the related-posts stop condition — rather than guessing at fixes. The spec also served as a prompt when I asked Claude to generate `pipeline.py`; I gave it the exact chunk size, overlap, and reasoning from `planning.md`, and the generated code matched my intent closely.

**One way your implementation diverged from the spec, and why:**

The evaluation plan originally specified the question "Which professor do Reddit users specifically warn against taking?" but I had to change it to "What do Reddit users say about Christina Boucher?" because the original query failed retrieval due to a semantic mismatch with the chunked Reddit dialogue. The spec assumed that any well-formed question would retrieve relevant chunks, but I discovered that embedding-based retrieval is sensitive to phrasing — "warn against taking" and "Remember, no [name]" are semantically distant in vector space. I updated the evaluation question to one that literally names the professor, which retrieves correctly, and documented the original query as a failure case instead of pretending the system handled it perfectly.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* I gave Claude my Chunking Strategy section from `planning.md` (600 characters, 150 overlap, reasoning about review-length documents) and a sample `documents/rmp_Peter Dobbins.txt` file, and asked it to implement `pipeline.py` with `load_documents()`, `clean_document()`, and `chunk_text()` functions.
- *What it produced:* Claude produced a clean `pipeline.py` with fixed-character sliding-window chunking, header removal, and basic metadata filtering. It also included a `main()` function that printed 5 representative chunks and saved to `chunks.json`.
- *What I changed or overrode:* I had to fix three things Claude missed. First, Windows console encoding caused a UnicodeEncodeError when printing chunks with emoji characters; I added `sys.stdout.reconfigure(encoding='utf-8')`. Second, the initial cleaning didn't catch Reddit UI cruft like ads (Squarespace), timestamps, vote counts, or related-posts navigation; I added 15+ skip patterns and a stateful stop condition for subreddit names. Third, the original skip pattern for usernames was too broad and caught legitimate words like "Awesome"; I replaced it with two targeted patterns (CamelCase and numbers/underscores).

**Instance 2**

- *What I gave the AI:* I gave Claude my Retrieval Approach section from `planning.md` (`all-MiniLM-L6-v2`, top-k=5, ChromaDB), `requirements.txt`, and the existing `chunks.json` structure, and asked it to implement `retrieval.py` with embedding, storage, and retrieval functions.
- *What it produced:* Claude produced `retrieval.py` with `SentenceTransformer` initialization, `PersistentClient`, `collection.add()`, and `collection.query()`. It also included a `test_retrieval()` function with my 3 evaluation queries.
- *What I changed or overrode:* I made two critical corrections. First, Claude's code used ChromaDB's default L2 distance metric, which produced hard-to-interpret distance scores (0.5–1.0). I switched to cosine similarity by adding `metadata={"hnsw:space": "cosine"}` to the collection creation, which made scores interpretable as 0=identical, 1=completely opposite. Second, when testing retrieval, one evaluation query (about Boucher) completely failed — the correct chunk didn't appear in the top 20. I debugged this myself by testing literal queries ("Christina Boucher terrible teacher") vs. semantic queries ("warn against taking"), identified the root cause as a semantic gap in embedding space, and updated the evaluation question in both `planning.md` and `retrieval.py` to match retrievable content.
