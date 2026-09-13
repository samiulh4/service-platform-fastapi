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
pip freeze > requirements.txt
python -m app.main
```

Server runs at `http://localhost:8889`

Build the Docker image
docker build -t service-platform-fastapi .

Run the container
docker run -d -p 8889:8889 --name service-platform-fastapi-container service-platform-fastapi

docker compose up --build