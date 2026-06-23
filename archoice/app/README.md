# ARCHOICE — Tech Prototype (test & deploy for display)

> v0.1 (2026-06-23). A runnable end-to-end slice of the loop —
> **camera → diagnose → plan → choose** — that you can open on a phone and demo today.

This is the *display/test* build, not the production app. It exists to prove the loop and
show it to people, while the native iOS app (ARKit/ARCore + React Native) remains the
Phase-3 target in `../business-plan.md`.

---

## What's here

```
app/
  web/index.html      Phone-ready web AR client (rear camera + viewfinder overlay + UI)
  server/
    main.py           FastAPI: /health, /diagnose, /plan, and serves the web client at /
    diagnosis.py      Real Claude path + honest offline stub; hard safety routing
    models.py         Pydantic models (Diagnosis, Plan, Recommendation slots)
    requirements.txt
```

---

## The phone → AR adoption path (honest version)

There are three layers; we deliberately ship the cheapest one first.

| Layer | What | Status here | When |
|---|---|---|---|
| **Web AR (this build)** | Phone-browser camera + 2D AR-style overlay, no install. | ✅ runnable now | Demos, user tests, investor display |
| **WebXR** | True world-anchored AR in-browser (where supported). | hook-ready (viewfinder is the seam) | Fast-follow |
| **Native ARKit / ARCore** | LiDAR depth, plane/anchor tracking, on-device capture, React Native. | designed for, not built | Phase 3 / MVP per `../mvp-scope.md` |

**Why web first:** zero App Store friction, runs on any modern phone, deployable as a static
page + one API. It's enough to validate the bet (does the diagnose→buy loop convert?) before
investing in native AR. The native build reuses the *same* backend contract (`/diagnose`,
`/plan`) — only the capture client changes.

---

## Run it

```bash
cd archoice/app/server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000/** (the server serves the web client at `/`).

### On a real phone
The camera needs **https or localhost**. Easiest options:
- run the server on your laptop and use a tunnel (e.g. `ngrok http 8000`), open the https URL on the phone; or
- host `web/` as a static site (Netlify/Vercel/GitHub Pages) and point it at a deployed API.

---

## Real AI vs. stub (both run the full loop)

- **No key:** every response is a clearly-labeled **stub** (`stub: true`, shown as a `stub`
  badge in the UI). The whole loop works with no key and no hardware — good for offline demos.
- **With key:** set `ANTHROPIC_API_KEY` and the server calls the **Claude API** (multimodal)
  for a real diagnosis from the captured photo, then a real plan. Badge shows `claude`.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export ARCHOICE_MODEL=claude-haiku-4-5-20251001   # optional; default fast model
```

If the web client can't reach the backend at all, it falls back to a local stub and labels
itself `offline` — so a demo never shows a blank screen.

---

## Safety is enforced server-side, not by the model alone

`diagnosis.py` keeps a `SAFETY_KEYWORDS` list (electrical, gas, structural, roofing…). Any
diagnosis touching those — or below the confidence floor — is forced to `requires_pro=true`
**regardless of model output**, which:
- suppresses the DIY plan and shows a "find a vetted pro" handoff, and
- removes all sponsored/product recommendations from that flow (advertising-spec §6.5).

This mirrors the project principle that the deterministic safety layer is authoritative and
AI is advisory — it never talks a user into unsafe DIY.

---

## API contract (stable seam for the native app)

```
POST /diagnose  { image_b64?, media_type?, note? }  -> { diagnosis, stub }
POST /plan      <Diagnosis>                          -> { plan, recommendations[], stub }
GET  /health                                         -> { ok, claude_configured }
```

`recommendations[].slots` carry the labeled `best_fit` / `sponsored` / `budget` structure
from `../advertising-spec.md`.

---

## What this prototype is NOT (yet)

- No LiDAR (web can't); measurements are simulated in the HUD.
- No real product catalog / live pricing — recommendation slots are illustrative.
- No accounts, persistence, or real checkout.
- Native AR tracking/anchoring is not implemented — that's the Phase-3 native build.

> Next tech steps: WebXR anchoring spike → real product-graph stub for one category →
> native React Native + ARKit capture client against this same API.
