# RiskPilot

**RiskPilot** is an ISO-aligned GRC platform for managing information-security assets, risks, controls and treatment actions.

The project is being built as a portfolio application to demonstrate practical skills in Governance, Risk and Compliance (GRC), FastAPI and Oracle Database.

## Planned capabilities

- Register and classify information assets.
- Assess risks using likelihood and impact scores.
- Calculate risk levels automatically.
- Track security controls and their implementation status.
- Create risk-treatment actions with owners and due dates.
- Provide an API health check and system settings endpoint.

## Tech stack

- Python
- FastAPI
- SQLAlchemy
- Oracle Database
- python-oracledb
- Uvicorn

## Project structure

```text
RISKPILOT/
├── server.py       # FastAPI application and Oracle Database configuration
├── routes.py       # API routes and endpoints
├── .env            # Local environment variables; never commit this file
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11 or later
- Oracle Database available locally or remotely
- An Oracle Database user for the application

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install the dependencies:

```bash
pip install fastapi "uvicorn[standard]" sqlalchemy oracledb python-dotenv
```

Create a `.env` file in the project root:

```env
ORACLE_USER=riskpilot
ORACLE_PASSWORD=replace_with_a_strong_password
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=FREEPDB1
```

## Running the API

From the project root, run:

```bash
uvicorn server:app --reload
```

The interactive API documentation will be available at:

```text
http://127.0.0.1:8000/docs
```

## Initial endpoints

- `GET /api/v1/health` — checks whether the API is available.
- `GET /api/v1/settings` — returns basic application settings.

## Security notes

- Do not commit `.env`, database passwords or Oracle Wallet files.
- Use a separate Oracle user with only the permissions needed by RiskPilot.
- Use sample or fictional data in the public portfolio version.

## License

This project is intended for educational and portfolio use.
