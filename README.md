# FastAPI User Items Template

This project is a FastAPI application designed to manage users, items and categories. It includes features for user authentication, CRUD operations, unit and integration testing and basic CI/CD configuration.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [License](#license)

## Installation

To set up this project locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/fastapi-user-items-template.git


2. **Navigate to the project directory:**

   ```bash
   cd fastapi-user-items-template

3. **Create and activate a virtual environment:**

   ```bash
   pdm install

4. **Install dependencies:**

   ```bash
   pdm install

5. **Create a .env file:**

    The application relies on environment variables for configuration. Create a .env file in the root directory of your project with the following content:

    ```bash
    POSTGRES_USER="user"
    POSTGRES_PASSWORD="password"
    DEV_DATABASE_URL='postgresql+psycopg2://user:password@127.0.0.1:5433/db'
    TEST_DATABASE_URL="postgresql+psycopg2://user:password@127.0.0.1:5434/db"
    PROD_DATABASE_URL="postgresql+psycopg2://user:password@127.0.0.1:5435/db"
    FRONTEND_URL='http://localhost:8000'
    JWT_SECRET_KEY='your_jwt_secret_key'
    JWT_ALGORITHM='HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES=10080


## Usage


1. **Using Docker:**

    To run the FastAPI application using Docker, follow these steps:

    - Build and start the services:
        ```bash
        docker-compose up --build

    - Access Adminer:
    Adminer is a database management tool that you can use to interact with your PostgreSQL database. Once the services are running, you can access Adminer at:

        - Adminer UI: http://127.0.0.1:8080
        - Login to Adminer:
            - System: PostgreSQL
            - Server: db
            - Username: user
            - Password: password
            - Database: mydatabase

2. **Run Alembic migrations:**

    Before starting the server, ensure that your database schema is up-to-date with the latest migrations. Run the following commands:

    - Initialize Alembic (if not already done):
        ```bash
        pdm run alembic init alembic

    - Generate migration scripts:
        ```bash
        pdm run alembic revision --autogenerate -m "Description of changes"

    - Apply migrations to the database:
        ```bash
        pdm run alembic upgrade head

3. **Start the API server:**

   ```bash
   uvicorn app.main:app --reload


4. **Access the API documentation:**

    Once the server is running, you can access the API documentation at:

    - Swagger UI: http://127.0.0.1:8000/docs
    - ReDoc UI: http://127.0.0.1:8000/redoc

## Testing

To run tests and generate a coverage report, use:

   ```bash
   pdm run pytest -cov=app -cov-report=html
```

## License

This project is licensed under the MIT License
