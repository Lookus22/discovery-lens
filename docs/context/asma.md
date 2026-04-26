# Discovery Lens — Asma's Personal Context

Paste this file into your Claude Project **alongside CLAUDE.md** before every session.
Last updated: Apr 22, 2026.

Add new sections at the bottom as the project progresses. Never delete old sections —
they are a record of your decisions and reasoning.

---

## Week 1 — My tasks

### 1. Synthetic data — Asana

**Product:** Asana (B2B SaaS, project management)
**Goal for the demo:** "Increase the percentage of new teams that complete their first
project within 30 days of signing up"

Generate a synthetic discovery dataset that is **extensive, varied, and deliberately messy**.
The goal is to stress-test the pipeline — contradictions, tangents, and noise are features,
not bugs. Aim for ~15–20 documents total across the following types.

Note: Asana is a B2B product, so the voice of the data is different from consumer apps.
Interviewees are team leads, project managers, ops people — not general consumers.
The pain points are about team coordination, not personal use.

#### Document types to generate

**User interview transcripts (4 interviews, ~800–1200 words each)**
- Participants: a marketing manager at a 20-person startup, an operations lead at a
  mid-size e-commerce company, a freelance project manager juggling multiple clients,
  an engineering team lead who was forced to adopt Asana by their PM
- Each interview should have: an interviewer asking open-ended questions, the participant
  going off-topic (e.g. complaining about their company culture instead of the tool),
  at least one contradiction (e.g. "we use it every day" but "nobody really checks it"),
  genuine insight buried in rambling answers
- Topics to surface naturally: task assignment confusion, notification overload,
  onboarding new team members, timeline/Gantt view frustrations, integration with Slack
  or Google Drive, the difference between how PMs use it vs how ICs use it,
  pricing and seat management pain, mobile vs desktop experience

**Usability test session notes (3 sessions)**
- Written by an observer in real time — bullet points, abbreviations, half-sentences
- Tasks tested: setting up a new project from a template, assigning tasks to multiple
  team members, finding an overdue task across projects
- Include: hesitation moments, wrong clicks, "where is that?" moments, verbal confusion,
  observer notes like "P tried to use search instead of the sidebar" or "P didn't notice
  the dependencies feature"

**G2 / Capterra reviews (20–30 reviews, mix of 1–5 stars)**
- B2B review style — more detailed and structured than app store reviews
- 1-star: too expensive for small teams, overwhelming for non-PMs, bad mobile app,
  poor customer support, forced migration from old interface
- 3-star: "great for PMs, confusing for everyone else", feature bloat, good but pricey
- 5-star: great for cross-team visibility, timeline view, integration ecosystem
- Mix of short and long, some with bullet points inside the review text (common in B2B)
- Include a few from clearly non-target users ("we used it for our 2-person shop, overkill")

**Customer support tickets (8–10 tickets)**
- Mix of: billing and seat count questions, SSO/admin setup issues, data export requests,
  feature requests (recurring tasks, better reporting), bug reports (task not syncing,
  notifications not firing), onboarding help requests
- Some tickets are from admins, some from end users — the tone and vocabulary differ
- Include at least 2 multi-message threads (ticket + reply + follow-up)

**Sales team / CS internal feedback notes (2–3 notes)**
- Written by account executives or customer success managers summarising customer calls
- Informal, uses internal sales jargon ("the champion loved it but the blocker is IT",
  "churn risk — team never adopted beyond basic task lists")
- Include: common objections heard in sales calls, features requested by enterprise
  customers, reasons for churn or downgrade

**Reddit threads (2–3 threads from r/projectmanagement or r/asana)**
- If you can scrape using praw (see note below), do so — real data is better here.
- If not, generate realistic threads: "is Asana worth it for a 5-person team?",
  8–12 replies covering cost, alternatives (Notion, Monday, Trello), specific pain points,
  one enthusiastic power user defending it, one person who switched away

#### Reddit scraping (preferred over generating)

```python
import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="discovery-lens-research"
)

subreddits = ["projectmanagement", "asana", "productivity", "startups"]
for sub in subreddits:
    for post in reddit.subreddit(sub).search("Asana", limit=10):
        print(post.title, post.selftext)
        post.comments.replace_more(limit=0)
        for comment in post.comments.list()[:20]:
            print(comment.body)
```

Register a Reddit app at https://www.reddit.com/prefs/apps (free, instant).

#### File naming convention

```
data/synthetic/asana/
├── interview_asana_01.txt   # marketing manager
├── interview_asana_02.txt   # ops lead
├── interview_asana_03.txt   # freelance PM
├── interview_asana_04.txt   # engineering lead
├── usability_asana_01.txt   # new project setup task
├── usability_asana_02.txt   # task assignment task
├── usability_asana_03.txt   # finding overdue tasks task
├── reviews_asana.csv        # G2/Capterra reviews, columns: rating, text, date, reviewer_role
├── tickets_asana.csv        # support tickets, columns: id, type, text, reply
├── sales_notes_asana.txt    # CS/sales team internal notes
└── reddit_asana.csv         # reddit threads, columns: post_title, post_text, comment
```

#### What to tell Claude when generating each document

Start your Claude session with:
> "I am generating synthetic discovery data for Asana (B2B SaaS project management tool)
> for a product analytics tool called Discovery Lens. The data will be used to stress-test
> an NLP pipeline that chunks text, embeds it, clusters it, and frames opportunities in
> JTBD language. I need [document type] that is realistic, messy, and contains
> contradictions and tangents. The product goal is: increase the percentage of new teams
> that complete their first project within 30 days of signing up."

Ask for one document type at a time. If the output feels too polished or structured,
ask Claude to add noise, contradictions, jargon, or off-topic moments.

---

### 2. EDA — Twitter Customer Support dataset

**Dataset:** Customer Support on Twitter (Kaggle)
**Link:** https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter
**Your notebook:** `notebooks/eda_twitter_support_asma.ipynb`

#### What to investigate

**Dataset structure**
- How many rows? What columns exist? (tweet_id, author_id, inbound, text, created_at, etc.)
- What does the inbound flag mean? (True = customer message, False = support reply)
- What companies are represented? List the top 20 by volume.

**Relevance filtering**
- Filter for tech companies only: Apple, Spotify, Xbox, Uber, Amazon, Google, etc.
- Separate customer messages (inbound=True) from support replies (inbound=False)
- For our pipeline, customer messages are the signal — support replies are secondary
- How many customer messages remain after filtering for tech companies?

**Text quality**
- Average tweet length in words — tweets are short, so most will be single chunks
- How many tweets are too short to be useful (< 5 words, e.g. just "@CompanySupport")?
- What percentage contain URLs, @mentions, or hashtags that will need cleaning?
- Sample 20 customer tweets manually — do they contain real pain points or just noise?

**Conversation reconstruction (important)**
- This dataset has threaded conversations. Can you reconstruct them by matching
  inbound tweets to their replies?
- A reconstructed thread (customer message + support reply) makes a much richer chunk
  than a single tweet. Explore whether this is feasible.

**Output**
Write a findings summary at the bottom of the notebook (markdown cell):
- How many usable customer messages remain after filtering?
- Should we use individual tweets or reconstructed threads as the unit of text?
- What text cleaning is needed before chunking?
- Recommended sample size for the demo (target: ≤100 chunks from this dataset)

#### What to tell Claude during EDA

> "I am doing EDA on the Twitter Customer Support dataset for Discovery Lens, an NLP
> pipeline that chunks text into 2–4 sentence segments, embeds them, and clusters them.
> Help me [specific task: filter for tech companies / reconstruct conversation threads /
> assess text quality for chunking]."

---

## How to update this file

When you complete a task or make a decision, add a dated section below:

```
## Apr 23 — synthetic data decisions
- Decided to use G2 review format over Capterra because...
- Interview length settled at ~900 words — longer felt unrealistic for B2B
- Reddit data: successfully scraped r/projectmanagement, 12 threads saved
```

This log is your memory across Claude sessions and your contribution to the team's
shared knowledge.

---

## Apr 22 — Task 1 complete: synthetic Asana data

All 11 files generated and validated against spec. Final structure:

```
data/interviews/    interview_asana_01.txt  # marketing manager
                    interview_asana_02.txt  # ops lead (e-commerce, DTC apparel)
                    interview_asana_03.txt  # freelance PM
                    interview_asana_04.txt  # engineering lead
data/usability/     usability_asana_01.txt  # new project setup — observer notes format
                    usability_asana_02.txt  # task assignment — observer notes format
                    usability_asana_03.txt  # finding overdue tasks — observer notes format
data/reviews/       reviews_asana.csv       # 28 reviews, mix 1–5 stars, some with Pros/Cons bullets
data/tickets/       tickets_asana.csv       # 23 tickets incl. 3 multi-turn threads
data/sales/         sales_notes_asana.txt   # 6 accounts (2 expansions, 1 churn, 1 at-risk, 1 trial)
data/reddit/        reddit_asana.csv        # 8 threads, 36 rows (one row per comment)
```

Key decisions:
- Files kept in subdirectories (not flat `data/synthetic/asana/`) — pipeline reads by glob, structure doesn't matter
- Usability tests written as raw observer notes (bullets, abbreviations) not polished transcripts
- Ops lead participant is e-commerce/DTC, not logistics — closer to spec
- Pricing and seat management pain added to interview_asana_02 (seasonal worker seat cost, guest access limiots)
- Multi-turn ticket threads use same 4-column schema — full conversation embedded in text/reply fields
- Reddit: generated (not scraped) — 8 threads instead of 2–3, richer signal coverage

---

## Apr 22 — Task 2 complete: EDA on Twitter Customer Support dataset

Notebook: `eda_twitter_support_asma.ipynb` (21 cells, runs clean end to end)
Output: `twitter_support_sample.csv` — 100 cleaned threads ready for pipeline

**Dataset numbers:**
- Tech company reply tweets: 345,326
- Customer messages linked to tech companies: 324,180
- Final sample after cleaning and reconstruction: 100 threads

**Decisions:**
- Unit of text: **reconstructed threads** (customer message + company reply joined with ` | `) — raw tweets alone too short and ambiguous for meaningful clustering
- Tech companies filtered: AppleSupport, AmazonHelp, Uber_Support, SpotifyCares, XboxSupport, hulu_support, GooglePlay, TMobileHelp, comcastcares, VerizonSupport, Ask_Spectrum, ATVIAssist
- Minimum tweet length: 5 words after cleaning — shorter tweets dropped as uninformative
- Cleaning: strip @mentions, URLs, hashtags; collapse whitespace

