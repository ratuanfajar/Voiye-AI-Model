# Voiye — Angkot Vision & LLM Verification

A small project that combines a YOLO-based detector and an LLM verifier to detect and validate "angkot" (Indonesian public minivan) routes from images.

---

## 🔍 Features

- Detect potential vehicles using YOLO (ultralytics) and OpenCV
- Verify whether a detected vehicle matches a target angkot route using an LLM (OpenRouter/OpenAI-compatible)
- Simple FastAPI service exposing an endpoint for image upload and verification
- Helper scripts to seed a Supabase table with route data

---

## 📁 Project Structure

```
voiye/
├── config/                  # YAML configs: app settings & prompt templates
├── data/                    # Raw and processed data (angkot routes, raw captures)
├── notebooks/               # Jupyter notebooks for validation/experiments
├── scripts/                 # Utility scripts (e.g., db seeder)
├── src/                     # Application source (API, vision, llm, utils)
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── yolov8n.pt               # (Example) model weights
```

---

## 🚀 Getting started

### Prerequisites

- Python 3.10+
- Git
- A Supabase project (optional; only if you use DB seeder)
- An OpenRouter/OpenAI API key for LLM verification

### Install

1. Clone the repo and create a virtual environment

```bash
git clone <repo-url>
cd voiye
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and set the following variables

```
OPENROUTER_API_KEY=<your-openrouter-or-openai-key>
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-key>
```

> Keep `.env` out of version control. The project uses `python-dotenv` to load these values.

### Configuration

- `config/config.yaml`: main app configuration (paths, model file, thresholds, external keys placeholder)
- `config/prompt_templates.yaml`: prompt templates used by the LLM verifier

Make sure the model weights referenced (default `yolov8n.pt`) exist in the project root or update `config/config.yaml` accordingly.

---

## 🧭 Usage

### Run the API (development)

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET /`
- Verify endpoint: `POST /verify-angkot` (multipart/form-data)

Example `curl`:

```bash
curl -X POST "http://localhost:8000/verify-angkot" \
  -F "file=@/path/to/image.jpg" \
  -F "route_name=Terminal - CICAHEUM" \
  -F "primary_color=Red" \
  -F "secondary_color=Blue" \
  -F "keywords=05, CICAHEUM"
```

The API returns a JSON object containing YOLO detection info, LLM analysis, and an action (`VIBRATE` / `IGNORE` / `STAY_SILENT`).

### Seed database (optional)

If you use Supabase, you can seed the `angkot_routes` table from the provided JSON:

```bash
python scripts/db_seeder.py
```

### Notebooks

- `notebooks/yolo_validation.ipynb`: Notebook for validating YOLO model behavior and predictions.

---

## 💡 Notes & Implementation details

- Detector: `src/vision/detector.py` uses `ultralytics.YOLO` to detect vehicles (classes: car, bus, truck).
- Verifier: `src/llm/verifier.py` formats prompt + image and calls the configured OpenRouter/OpenAI endpoint.
- DB connector: `src/utils/db_connector.py` expects `SUPABASE_URL` and `SUPABASE_KEY` in `.env`.
