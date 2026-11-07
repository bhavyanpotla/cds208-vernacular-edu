# Deploying to Streamlit Community Cloud

Free, no build step, and it deploys straight from this GitHub repo. Fifteen minutes
end to end, most of it waiting for the first build.

## 1. Before you deploy

- The repo must be **public** (Community Cloud reads public repos on the free tier).
- `app.py` is the entry point. It already calls `st.set_page_config` first and
  resolves `assets/styles.css` relative to the project root.
- `.streamlit/config.toml` sets the dark theme — commit it, or the deployed app
  will render light and the glass panels will look wrong.
- Never commit `.env`. It is gitignored, and `.env.example` documents the keys.

## 2. Create the app

1. Go to <https://share.streamlit.io> and sign in with GitHub.
2. **New app** → *Deploy a public app from GitHub*.
3. Repository: `bhavyanpotla/cds208-vernacular-edu` · Branch: `main` · Main file
   path: `app.py`.
4. **Advanced settings → Python version: 3.11** (the pins assume 3.11+).
5. Deploy. First build takes 3–6 minutes; `requirements.txt` is installed as-is.

## 3. Secrets

Only needed for live mode. In the app's dashboard: **Settings → Secrets**, and paste:

```toml
SARVAM_API_KEY = "your-key-here"
VE_PROVIDER = "auto"
```

Save; the app reboots. The sidebar badge flips from *Mock mode* to *Live · Sarvam AI*.

To run the demo deliberately in mock mode even with a key configured — useful when
the venue Wi-Fi is unreliable — set `VE_PROVIDER = "mock"` instead. Same app, same
clicks, labelled results.

## 4. The SQLite caveat, stated plainly

Community Cloud gives the container an **ephemeral filesystem**. That means:

- The database lives in `data/app.db` and is recreated empty on every restart,
  redeploy or long idle period.
- Anything a visitor does is real while the container lives, then gone.
- Two visitors share one database (it is a single process), which is fine for a
  demo and wrong for a product.

Two acceptable responses, in order of effort:

**a. Seed on demand (what this repo does).** After a deploy, run the seed once from
a terminal pointed at the same database — or simply click through the app for two
minutes. The dashboard fills with real events. For a scheduled version, add a
`st.button("Load demo data")` on the Analytics page that calls
`scripts/seed_demo.py`'s `main()`.

**b. Move to Postgres.** Supabase's free tier works. Only `core/db.py` changes:
`connect()` returns a Postgres connection, and the `?` placeholders become `%s`.
Nothing above the data layer knows the difference, which is exactly why the schema
was written Postgres-compatible from Phase 0.

Say which one you did in the README, so the examiner does not discover it by
refreshing twice.

## 5. Verify the deploy

In an incognito window, with no key configured:

1. Home renders dark, with the aurora background and the glass hero.
2. Sidebar shows **Mock mode**.
3. Learn → switch *Read in* to తెలుగు → segments appear in Telugu, labelled mock.
4. Tutor → ask "who won the cricket world cup?" → refusal, in Telugu.
5. Analytics → **Refresh export** → the health line shows row counts.
6. Resize to 390 px → single column, no horizontal scroll.

If step 1 is white, `.streamlit/config.toml` did not make it into the repo. If
step 3 throws, check the `data/` directory is writable — the app calls `init_db()`
on first load.

## 6. CI badge

`.github/workflows/ci.yml` runs ruff, pytest and an import smoke test on every push
to `main`. The badge in the README reads from it. If the badge shows *failing*,
open the Actions tab — the usual cause is a test that depends on a package missing
from `requirements.txt`, which is why new dependencies must be added there in the
same commit that uses them.

## 7. What to say about deployment in the viva

"The deployed link runs the same code as the local demo, with no key configured, so
it shows labelled mock results rather than failing. That is a deliberate design
choice: the grader's laptop may have no key and no internet, and a demo that only
works on my machine is not a demo. The database is ephemeral on the free tier,
which is documented in the README along with the one-file change to move to
Postgres."
