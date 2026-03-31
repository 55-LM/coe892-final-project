# City Waste Collection Management System

- **Planning Service**: Owns city data (neighbourhoods, houses, bin types), collection rules (weekdays, 7 AM–5 PM), and generates weekly schedules and daily routes. Data stored in SQLite.
- **Operations Service**: Receives route IDs, fetches route details from the Planning Service, simulates pickups per stop, and records events (completed/missed/delayed) in its own SQLite DB. Event data flows to Analytics by API calls.
- **Analytics Service**: Stateless aggregation; fetches pickup events from Operations and house/neighbourhood data from Planning via HTTP, then computes summary metrics, by-neighbourhood, by-waste-type, and missed-pickup lists.
- **Frontend**: React + Vite + Tailwind + Recharts. Calls all three backends (via proxy in dev) to display schedule, routes, pickup status, and charts.

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Recharts, React Router.
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Pydantic.
- **Database**: SQLite (per service that needs persistence).
- **Containerization**: Docker and Docker Compose.

## How to Run the System

From the **project root** (the folder that contains `planning-service`, `operations-service`, `analytics-service`, and `frontend`).  
**Prerequisites:** Python 3.11+ with `pip`, and [Node.js](https://nodejs.org/) (for `npm`).

Run the stack in **four terminals** (local development, no Docker). Start services in order **1 → 2 → 3 → 4**. The first time, run `pip install` / `npm install` in each folder; after that you can skip those steps.

#### Windows (PowerShell)

**Terminal 1 — Planning (port 8000)**

```powershell
cd planning-service
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 — Operations (port 8001)**  
(Wait until Planning is up.)

```powershell
cd operations-service
python -m pip install -r requirements.txt
$env:PLANNING_SERVICE_URL = "http://localhost:8000"
python -m uvicorn main:app --reload --port 8001
```

**Terminal 3 — Analytics (port 8002)**

```powershell
cd analytics-service
python -m pip install -r requirements.txt
$env:OPERATIONS_SERVICE_URL = "http://localhost:8001"
$env:PLANNING_SERVICE_URL = "http://localhost:8000"
python -m uvicorn main:app --reload --port 8002
```

**Terminal 4 — Frontend**

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

#### macOS / Linux (bash)

Use the same order. Set environment variables with `export` instead of `$env:...`:

```bash
# Terminal 2
export PLANNING_SERVICE_URL=http://localhost:8000

# Terminal 3
export OPERATIONS_SERVICE_URL=http://localhost:8001
export PLANNING_SERVICE_URL=http://localhost:8000
```

If you use **Command Prompt** (`cmd.exe`) on Windows, use `set PLANNING_SERVICE_URL=http://localhost:8000` (and similarly for the other variables) before `uvicorn`.

