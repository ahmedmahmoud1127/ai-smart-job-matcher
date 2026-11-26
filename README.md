# AI Smart Job Matcher

Login / Sign Up page with Google, GitHub and LinkedIn (shown first, see *Login* below). Pages: Dashboard (01), My Profile (02, SQLite), CV Analyzer (03), Smart Job Matching (04, the **Jobs** button), Learning Roadmap (05), Skill Gap Analysis (06), Analytics Dashboard (07, the **Analytics** button).

    python -m venv venv
    venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
    pip install -r requirements.txt
    streamlit run app.py

`data/ai_job_matcher.db` is created automatically on first run (delete it to reset all data).

## Structure
- `components/jobs/` - Smart Job Matching UI (`page`, `filters`, `cards`, `insights`, `styles`)
- `components/roadmap/` - Learning Roadmap UI (`page`, `form`, `view`, `styles`)
- `app.py` - routing + shared top navbar
- `components/` - dashboard sections; `components/profile/` - My Profile; `components/cv/` - CV Analyzer UI
- `services/` - `cv_extractor`, `skills_extractor`, `cv_parser`, `keyword_matcher`, `cv_scoring`, `recommendations`,
  `cv_analyzer` (orchestrator), `job_matching` (Smart Job Matching engine), `roadmap_generator` (Learning Roadmap rules), `profile_sync`, `cv_report` (PDF), `profile_completion`, `profile_data`
- `database/` - `db.py`, `schema.py`, `repository.py`, `cv_repository.py`, `job_repository.py` (saved jobs), `roadmap_repository.py` (roadmap + progress)
- `components/skill_gap/` - Skill Gap Analysis UI (`page`, `sections`, `state`, `styles`)
- `data/` - `skill_gap_requirements.py` (career requirements), `sample_data.py`, `skills_catalog.py`, `job_requirements.py`, `jobs_catalog.py` (36 sample jobs), `roadmaps.py` (9 predefined career roadmaps)

## Smart Job Matching (Feature 04)
Open it with the **Jobs** button (or *See All* on the dashboard). Everything is computed locally in Python, with no external AI API.

- **Inputs:** skills, education, experience, projects and career preferences from My Profile, plus skills/education/experience
  found in your latest CV Analyzer result.
- **Score (0-100):** required skills 40 + preferred skills 15 + education 15 + experience 15 + career preferences 15.
  A component that cannot be evaluated (e.g. preferences not set) is excluded and the rest are rescaled, never guessed.
  Skill credit depends on proficiency (Beginner 50%, Intermediate 80%, Advanced/Expert 100%); skills found only in the CV
  or projects count 70-80%; a closely related skill (e.g. MySQL for SQL) earns 50%.
- **Skills to Learn Next:** a what-if analysis re-scores your closest-fitting jobs as if you had each missing skill.
- **Saved jobs** are stored in the SQLite table `saved_jobs` (created automatically).
- The job list is a static sample dataset in `data/jobs_catalog.py` (fictional companies); replace it with a live source later.
- Tests: `python -m unittest tests.test_job_matching -v`

## Learning Roadmap (Feature 05)
Open it with the **Learning Roadmap** button (or *View Plan* on the dashboard).

- **Inputs:** target career, current skills (pick from the list, type extra ones, or import them from My Profile and the CV Analyzer),
  experience level (Beginner / Intermediate / Advanced) and study hours per day.
- **How it works (plain Python, no NLP / computer vision / machine learning / external AI API):** the student's skills are normalised
  with the existing skill dictionary and a few shorthand aliases, basics implied by known skills are added (e.g. Django -> Python),
  and everything is compared stage by stage with a predefined roadmap in `data/roadmaps.py`. Missing skills get hour estimates
  (base hours x level factor), converted to study days and weeks assuming 5 study days per week.
- **Shows:** career goal, current skills, missing skills (core vs bonus), learning stages with week ranges and durations, resources per
  skill, a mini-project per stage, and the planned finish date.
- **Progress tracking:** tick skills (or mark a whole stage); the overall percentage, per-stage progress and next skill update
  automatically and are stored in SQLite (`learning_roadmaps`, `roadmap_progress`).
- **Regenerate:** change any input and press *Regenerate Roadmap*. Skills completed in the previous roadmap can be counted as known.
- Resource links point to official documentation and well-known learning platforms; check them from time to time as sites change.
- Tests: `python -m unittest tests.test_roadmap -v`

## Skill Gap Analysis (Feature 06)
Open it with the **Skill Gap Analysis** button in the top navigation bar. Plain Python rules only: no NLP, computer vision,
machine learning or external AI API.

- **Inputs:** target career, experience level, study hours per day and learning focus (the **Edit** button), plus your current skills.
  Skills come from My Profile, the latest CV analysis, projects and experience (same source as Smart Job Matching). You can add
  skills (with a level), remove skills, or reset them. These edits only change this analysis, never My Profile.
- **Requirements:** `data/skill_gap_requirements.py` holds predefined requirements for the 9 careers of the Learning Roadmap.
  Each requirement has the skills that satisfy it (aliases such as *APIs* = *REST APIs*), the level needed, an importance weight,
  a complexity (1-5) and one of 3 learning stages.
- **Calculation (`services/skill_gap.py`):** every requirement earns credit 1.0 / 0.5 / 0.25 / 0 depending on how far your level is below
  the needed level. Match % = importance-weighted credit. *Skills You Have* = fully met, *Skills You Need* = partial or missing.
  Prerequisites are inferred (Django -> Python). Missing skills are grouped by category and ranked by priority.
- **Duration:** complexity hours x experience-level factor x share still missing, converted to weeks with your daily study hours
  (5 study days per week). The 3 stages show week ranges, month ranges and coverage progress.
- **Recommendations:** up to 3, generated from the missing skills (start with the top priority one, learn one from another area,
  practise a partly known skill). **Regenerate Roadmap** recalculates from the latest profile/CV data and saves a snapshot.
- **Start Learning Plan:** opens the existing Learning Roadmap. If you have no roadmap yet, one is created for you; if your current
  roadmap is for the same career it is kept (progress is not touched); if it is for another career the roadmap form is only filled in.
- **Storage:** SQLite table `skill_gap_state` (created automatically, also for existing databases).
- Tests: `python -m unittest tests.test_skill_gap -v`

## Analytics Dashboard (Feature 07)
Open it with the **Analytics** button in the top navigation bar. Plain Python only: no NLP, computer vision, machine learning,
external AI API, random or hard-coded numbers. Everything is calculated from data the app already stores.

- **Sections:** summary cards, Career Progress, Skills Analytics (current / acquired / missing by category), Recently Acquired Skills,
  Learning Activity (daily / weekly / monthly hours, weekly chart, heatmap, consistency), Learning Roadmap Analytics,
  Job Matching Analytics, CV Analytics and "Your Career Insights". The **7 Days / 30 Days / 90 Days / All Time** filter re-slices every period-based number.
- **Sources:** skills = `build_candidate` (profile, projects, CV); jobs = `rank_jobs`; readiness and missing skills = the saved Skill Gap
  settings (`services/skill_gap.py`); roadmap, progress and completion dates = `learning_roadmaps` / `roadmap_progress`; CV = `cv_analyses`.
- **Learning hours are estimates.** The app has no study timer, so when a roadmap skill is ticked, the hours planned for that skill are
  credited to that day. Consistency = active days / days in the period.
- **History:** `analytics_snapshots` (new table, created automatically) stores one row per day the page is opened (readiness, job match scores,
  CV score, roadmap %). Trend lines and "since ..." comparisons appear once two or more days exist. Regenerating a roadmap deletes its progress
  (existing behaviour), so learning hours restart with the new roadmap.
- **Empty states:** no target career, roadmap, CV or activity means a clear message with a shortcut button, never an invented value.
- **Files:** `services/analytics.py`, `database/analytics_repository.py`, `components/analytics/` (`page`, `sections`, `charts`, `styles`).
- Tests: `python -m unittest tests.test_analytics -v`

## Login
The app opens on a login page (`components/login/`: `page.py` logic + form, `styles.py` glassmorphism CSS, `art.py` logo and AI-robot SVG).
Everything else is only rendered after signing in (`app.py`); **Sign Out** is in the profile menu of the top bar.

- **Demo account:** the sample user's email (see My Profile) with password `Demo@1234`. It is created on first run in the new table
  `user_credentials` (`database/auth_repository.py`: salted PBKDF2-HMAC-SHA256, the `users` table is not changed). Set `SHOW_DEMO_HINT = False`
  in `components/login/page.py` to hide the hint under the card.
- **Sign In** has a loading state, validation, and a 30-second lock-out after 5 wrong attempts. The password field has the built-in show/hide eye.
- **Remember Me** keeps the email pre-filled after signing out (for the current browser session only).
- **Sign Up** (the link under the card switches the card to *Create Account*): full name, email, password (8+ characters with a letter and a number)
  and confirmation. The account is created empty and the user lands straight on the **Dashboard**.
- **Google / GitHub / LinkedIn** work in both *Sign In* and *Sign Up*: the first time creates an account (and opens the Dashboard with a welcome
  message), the next times sign in to it. If the provider returns a **verified** email that already has an account, the two are linked; an
  unverified email is never trusted. See *Social sign-in setup* below.
- **Every user has their own data.** Repository/service functions resolve the user from the session (`database/session.py`) instead of the old fixed
  sample user, and **Sign Out** clears the whole session. The demo account keeps the sample data; new accounts start empty.
- **Not wired yet:** Forgot Password (needs email sending); it shows an explanatory message.

### Social sign-in setup
Without credentials a provider button just shows a "not set up yet" message. To enable one, create an OAuth app and register this **redirect URI**
(it must match exactly; use your real address when deployed): `http://localhost:8501`

| Provider | Where to create the app | Needed scopes |
|---|---|---|
| Google | Google Cloud Console -> APIs & Services -> Credentials -> OAuth client ID (Web application) | `openid email profile` |
| GitHub | GitHub -> Settings -> Developer settings -> OAuth Apps | `read:user user:email` |
| LinkedIn | LinkedIn Developers -> your app -> Products: add **Sign In with LinkedIn using OpenID Connect** | `openid profile email` |

Then copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in the client IDs and secrets (or set the environment variables
`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, ..., `OAUTH_REDIRECT_URI`). **Never commit `secrets.toml`** (it is in `.gitignore`).
Code: `services/oauth.py` (authorization-code flow, HMAC-signed `state` with a 10-minute lifetime), UI in `components/login/page.py`.
- Tests: `python -m unittest tests.test_auth tests.test_oauth -v` (the OAuth tests mock the providers, no network needed)
