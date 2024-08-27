# GeoExplorer Server

This is the server component of the GeoExplorer project, built with FastAPI to log requests from the client component.

## Requirements

- Docker

## Running the Server

You can run the server using Docker Compose or directly with Uvicorn. Make sure the machine you are running the server on is publicly accessible on the chosen server port.

### Using Docker Compose

1. Make sure you have Docker and Docker Compose installed.
2. Run the following command in the server directory:

```bash
docker-compose up --build
```

### Using Uvicorn directly

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the following command:

`uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload`

## API Endpoints

- `GET /`: Welcome message
- `GET /log` or `GET /log/{additional_info}`: Log a request
- `GET /logged_ips`: Retrieve all logged requests

## Database

The server uses SQLite as the database. The database file will be created in the `./data` directory.

## Note

Ensure that the `data` directory exists and has the necessary permissions for the application to create and access the SQLite database file.
