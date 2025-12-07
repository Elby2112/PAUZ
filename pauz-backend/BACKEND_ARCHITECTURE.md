# Backend Architecture

This document provides a detailed explanation of the backend architecture for the Pauz application.

## 1. Overview

The backend is a robust and well-structured FastAPI application. It follows a modular architecture with a clear separation of concerns, making it scalable and maintainable. The core components are:

-   **API Layer**: Handles incoming HTTP requests (managed by FastAPI routes).
-   **Business Logic Layer**: Contains the core application logic (managed by services).
-   **Data Layer**: Manages data persistence and interaction with the database (managed by SQLModel ORM).

Authentication is implemented using a standard Google OAuth 2.0 flow, with JWTs for session management.

## 2. Core Technologies

-   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - A modern, high-performance web framework for building APIs with Python.
-   **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) - A library for interacting with SQL databases from Python code, with Python objects. It is built on top of Pydantic and SQLAlchemy.
-   **Database**: [SQLite](https://www.sqlite.org/index.html) (default) / [PostgreSQL](https://www.postgresql.org/) (configurable) - A flexible setup allowing for a simple file-based database for development and a more robust database for production.
-   **Authentication**: [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2) & [JWT](https://jwt.io/) - Secure user authentication and session management.

## 3. Project Structure

The main application logic is contained within the `app/` directory.

```
app/
├── __init__.py
├── main.py               # Application entry point
├── database.py           # Database connection and session management
├── dependencies.py       # FastAPI dependencies
├── models/               # Data models (database schema)
│   └── all_models.py
├── routes/               # API endpoints (controllers)
│   ├── auth.py
│   ├── free_journal.py
│   ├── guided_journal.py
│   ├── garden.py
│   └── ...
├── services/             # Business logic
│   ├── auth_service.py
│   ├── journal_service.py
│   └── ...
└── utils/                # Utility functions
```

-   **`main.py`**: The entry point of the application. It initializes the FastAPI app, includes all the API routers from the `routes` directory, and sets up a startup event to create the database tables.
-   **`database.py`**: Configures the primary database connection using SQLModel. It defines how the application connects to the database and provides the session management dependency (`get_session`) used throughout the app.
-   **`models/`**: This directory contains the data models which define the database schema. `all_models.py` consolidates all data models.
-   **`routes/`**: This directory contains the API endpoint definitions. Each file corresponds to a specific feature or resource, promoting modularity.
-   **`services/`**: This directory contains the core business logic, separated from the routing layer. This separation allows for cleaner code and easier testing.

## 4. Key Features & Implementation

### 4.1. Authentication

-   **Flow**: The authentication process uses Google's OAuth 2.0.
    1.  The user initiates the login process via the `/api/auth/login` endpoint.
    2.  The user is redirected to Google for authentication.
    3.  After successful authentication, Google redirects the user back to the `/api/auth/callback` endpoint.
    4.  The backend verifies the user's information and generates a JWT (JSON Web Token).
    5.  This JWT is sent to the client and used to authenticate subsequent requests to protected endpoints.
-   **Relevant Files**: `app/routes/auth.py`, `app/services/auth_service.py`.
-   **Protected Routes**: Endpoints that require authentication use a dependency that verifies the JWT.

### 4.2. Journaling (Free & Guided)

-   **Free Journal**: Allows users to create, retrieve, update, and delete simple journal entries.
-   **Guided Journal**: Provides structured journaling prompts and stores user responses.
-   **Implementation**:
    -   **Models**: `FreeJournal` and `GuidedJournal` in `app/models/all_models.py`.
    -   **Routes**: `app/routes/free_journal.py` and `app/routes/guided_journal.py` define the CRUD API endpoints.
    -   **Services**: The `journal_service.py` (and potentially other service files) contains the business logic for managing journals.

### 4.3. Digital Garden

-   **Concept**: A space for users to cultivate their thoughts and ideas. The exact implementation details can be inferred from the `Garden` model.
-   **Implementation**:
    -   **Model**: `Garden` in `app/models/all_models.py`.
    -   **Routes**: `app/routes/garden.py`.

### 4.4. Hints

-   **Concept**: Provides users with helpful tips or prompts.
-   **Implementation**:
    -   **Model**: `Hint` in `app/models/all_models.py`.

## 5. Database

-   The application uses **SQLModel** as its Object-Relational Mapper (ORM), which simplifies database interactions by allowing developers to work with Python objects instead of raw SQL queries.
-   By default, it is configured to use **SQLite**, which is a lightweight, file-based database. This is convenient for development and testing.
-   The configuration can be easily switched to use **PostgreSQL** for a more robust production environment by changing the `DATABASE_URL` in the environment configuration.
-   The database schema is defined by the models in `app/models/all_models.py`, which includes tables for `User`, `FreeJournal`, `GuidedJournal`, `Garden`, and `Hint`.
