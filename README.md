# FastAPI Service Platform

## Project Structure

```
fastapi-service-platform/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   └── modules/
│       ├── authentication/
│       │   ├── models/
│       │   │   └── users_auth_token.py
│       │   └── routes/
│       │       └── router.py
│       └── user/
│           └── models/
│               └── users.py
├── .env
├── .gitignore
├── CmderRun.cmd
├── README.md
└── requirements.txt
```

## Getting Started

```bash
pip install -r requirements.txt
python -m app.main
```

Server runs at `http://localhost:8889`
