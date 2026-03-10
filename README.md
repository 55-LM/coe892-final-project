# Real-Time City Waste Collection Management System

A **distributed cloud-style prototype** for a course project in Distributed Cloud Computing Systems. The system simulates how a city manages waste collection across neighbourhoods and households, with separate services for **planning**, **operations**, and **analytics**, and a **dashboard** frontend.

## Project Purpose

- Demonstrate **distributed system design**: multiple backend services with clear responsibilities, communicating via REST APIs.
- Simulate **city waste collection**: weekly schedules, daily truck routes, pickup simulation (completed/missed/delayed), and analytics.
- Provide a **working prototype** suitable for a university course demo, with mock data, Docker support, and a presentable UI.

## Architecture

The system is split into four components:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Frontend Dashboard (React)                        │
│  Weekly Schedule | Daily Routes | Pickup Status | Analytics               │
└───────────────────────────────┬─────────────────────────────────────────┘
                                 │ REST (JSON)
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Planning Service│    │Operations Service│    │ Analytics       │
│ (FastAPI :8000) │    │ (FastAPI :8001)  │    │ Service (:8002) │
│                 │    │                  │    │                 │
│ • City data     │◄───│ • Simulate route │    │ • Reads events  │
│ • Weekly sched  │    │ • Pickup events  │───►│   from Ops      │
│ • Daily routes  │    │ • completed/     │    │ • Reads houses  │
│ • SQLite        │    │   missed/delayed  │    │   from Planning │
│                 │    │ • SQLite         │    │ • Summary &     │
└─────────────────┘    └─────────────────┘    │   breakdowns    │
                                               └─────────────────┘
```

- **Planning Service**: Owns city data (neighbourhoods, houses, bin types), collection rules (weekdays, 7 AM–5 PM), and generates weekly schedules and daily routes. Data stored in SQLite.
- **Operations Service**: Receives route IDs, fetches route details from the Planning Service, simulates pickups per stop, and records events (completed/missed/delayed) in its own SQLite DB. Event data flows to Analytics.
- **Analytics Service**: Stateless aggregation; fetches pickup events from Operations and house/neighbourhood data from Planning via HTTP, then computes summary metrics, by-neighbourhood, by-waste-type, and missed-pickup lists.
- **Frontend**: React + Vite + Tailwind + Recharts. Calls all three backends (via proxy in dev or nginx in Docker) to display schedule, routes, pickup status, and charts.

**Distributed design**: Each service has a single responsibility, its own data where needed, and communicates only through REST APIs. No shared database; event data flows from Operations to Analytics by API calls.

## How to Run the System

### Option 1: Docker Compose (recommended)

From the project root:

```bash
docker compose up --build
```

- **Frontend**: http://localhost:80  
- **Planning API**: http://localhost:8000  
- **Operations API**: http://localhost:8001  
- **Analytics API**: http://localhost:8002  

The frontend at port 80 is served by nginx, which proxies `/api/planning`, `/api/operations`, and `/api/analytics` to the respective backends.

### Option 2: Local development (without Docker)

1. **Backend (three terminals)**  
   Create a virtualenv in each service directory and run:

   ```bash
   # Terminal 1 - Planning
   cd planning-service && pip install -r requirements.txt && uvicorn main:app --reload --port 8000

   # Terminal 2 - Operations (ensure Planning is running)
   cd operations-service && pip install -r requirements.txt && set PLANNING_SERVICE_URL=http://localhost:8000 && uvicorn main:app --reload --port 8001

   # Terminal 3 - Analytics
   cd analytics-service && pip install -r requirements.txt && set OPERATIONS_SERVICE_URL=http://localhost:8001 && set PLANNING_SERVICE_URL=http://localhost:8000 && uvicorn main:app --reload --port 8002
   ```

   On Linux/macOS use `export` instead of `set`.

2. **Frontend**  
   Uses Vite proxy to forward `/api/planning`, `/api/operations`, `/api/analytics` to the backends:

   ```bash
   cd frontend && npm install && npm run dev
   ```

   Open http://localhost:5173

## How Each Service Works

### Planning Service

- **Seed data**: On first run, seeds 5 neighbourhoods, ~80 houses (50–100 range), and collection rules (garbage Mon/Wed, recycling Tue/Thu, organics Fri; 7 AM–5 PM).
- **Endpoints**:  
  `GET /api/neighbourhoods`, `GET /api/houses`, `POST /api/generate-schedule`, `GET /api/schedule`, `POST /api/generate-route`, `GET /api/routes`, `GET /api/routes/{id}`.
- **Logic**: Schedule generation assigns each neighbourhood × waste type to a weekday from rules. Route generation builds one route per neighbourhood × waste type for a given date with an ordered list of house stops (no advanced optimization).

### Operations Service

- **Simulation**: `POST /api/simulate-route/{route_id}` fetches the route from Planning, then creates one pickup event per stop with random status (completed/missed/delayed) and timestamps.
- **Endpoints**:  
  `POST /api/simulate-route/{route_id}`, `POST /api/pickup-events`, `GET /api/pickup-events`, `GET /api/pickup-events/route/{route_id}`.
- **Data**: Stores only pickup events in SQLite; no copy of city or route structure.

### Analytics Service

- **Computation**: Calls Operations for pickup events and Planning for houses and neighbourhoods; aggregates in memory.
- **Endpoints**:  
  `GET /api/metrics/summary`, `GET /api/metrics/by-neighbourhood`, `GET /api/metrics/by-waste-type`, `GET /api/metrics/missed-pickups`.
- **No database**: Pure aggregation over HTTP; reflects distributed “read from other services” pattern.

### Frontend Dashboard

- **Pages**: Dashboard (summary metrics), Weekly Schedule (generate/view), Daily Routes (generate + simulate per route), Pickup Status (events with filters), Analytics (Recharts: by waste type, by neighbourhood, completion rate).
- **Flow**: Generate schedule → generate routes for a weekday → simulate one or more routes → see events in Pickup Status and metrics in Dashboard/Analytics.

## How the Distributed Design Is Reflected

- **Separate codebases**: `planning-service/`, `operations-service/`, `analytics-service/`, `frontend/` with no shared business logic.
- **Clear boundaries**: Planning = data and schedule/route generation; Operations = execution and events; Analytics = read-only aggregation.
- **Communication via REST**: Operations calls Planning to get route details; Analytics calls Operations and Planning for data. All JSON over HTTP.
- **Data flow**: Events created in Operations are consumed by Analytics through API calls, illustrating event-driven style without a message queue.
- **Deployable independently**: Each service has its own Dockerfile and can be scaled or replaced independently; Docker Compose wires them together.

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Recharts, React Router.
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Pydantic.
- **Database**: SQLite (per service that needs persistence).
- **Containerization**: Docker and Docker Compose.

## Project Structure

```
coe892project/
  planning-service/     # City data, schedules, routes
  operations-service/   # Pickup simulation, events
  analytics-service/    # Metrics from events + planning data
  frontend/             # React dashboard
  docker-compose.yml
  README.md
```

## Testing (Backend)

From each service directory (e.g. `planning-service`):

```bash
pip install pytest httpx
pytest
```

Example test (optional): add `tests/test_planning.py` that calls `GET /api/health` and `GET /api/neighbourhoods` and asserts status 200.

## Scope and Limitations

- **In scope**: Mock data, weekly schedule, simple ordered routes, pickup simulation, dashboard with metrics and charts, Docker, clear separation of services.
- **Out of scope**: Advanced route optimization, authentication, message queues, production-grade cloud infrastructure.

This prototype is intended for a **course demo**: it shows a distributed, microservice-inspired design applied to a concrete coordination problem (city waste collection) and remains manageable for a student project.
