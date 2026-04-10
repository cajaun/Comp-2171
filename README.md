# Braeton Gate Wholesale Inventory System

A desktop inventory management system for a wholesale business, built with Python, Tkinter, SQLAlchemy, and PostgreSQL.

This application manages products, categories, users, stock movement, damaged and expired inventory, reports, slow-moving stock analysis, and dashboard analytics through a native desktop interface.

## Features

- Dashboard with summary cards and management charts
- Inventory CRUD operations
- Category management
- Stock adjustment tracking
- Damaged / expired / lost item recording
- Slow-moving and overstock analysis
- Report generation and export
- User management
- Login and authentication
- Configurable system settings

## Design Philosophy

This codebase is structured around two major goals:

1. follow a layered architecture
2. follow an object-oriented design with clear class responsibilities

The project uses classes, objects, and object collaboration as architectural building blocks rather than treating classes as syntax alone.

## Object-Oriented Approach

The application is organized around objects with explicit responsibilities.

### What object-oriented design means here

In this project, object-oriented design means:

- classes represent meaningful system responsibilities
- objects encapsulate behavior and state
- each class has a focused reason to change
- views collaborate with service objects instead of handling persistence themselves
- data is passed to the UI through dedicated objects instead of raw session-bound ORM entities

### Important object types in the project

#### 1. ORM model classes

The data layer defines persistent entity classes in `data/models.py`:

- `Category`
- `Item`
- `User`
- `StockAdjust`
- `ItemCondition`
- `Report`
- `SlowMovingOverstock`
- `Config`

These classes represent domain data and relationships.

#### 2. Service classes

The `services/` package contains class-based application services:

- `AuthService`
- `InventoryService`
- `CategoryService`
- `UserService`
- `StockAdjustmentService`
- `ConditionService`
- `ReportService`
- `SlowMovingService`
- `SettingsService`
- `DashboardService`

These objects own business rules, validation, orchestration, and data access workflows.

#### 3. View-model classes

The dataclasses in `services/view_models.py` are lightweight immutable objects that carry prepared data from the service layer to the presentation layer.

Examples include:

- `ItemSummary`
- `InventoryStats`
- `CategorySummary`
- `AdjustmentRecord`
- `ConditionRecord`
- `ReportRecord`
- `SlowMovingFlagRecord`
- `DashboardSnapshot`

These objects help keep the UI independent from live SQLAlchemy ORM instances.

#### 4. Service container object

`services/service_container.py` builds a `ServiceContainer` object that groups all application services together and injects them into the UI.

This gives the application a single composition root and makes dependency wiring explicit.

## Object Collaboration

The application is organized so that objects collaborate through clear responsibilities:

- views call service methods
- services own validation and workflow rules
- services manage session-scoped persistence work
- services return prepared view-model objects
- the UI renders those objects

That keeps responsibilities separated and makes the overall system easier to reason about.

## Layered Architecture

The application is divided into three main layers.

### 1. Presentation layer

Located in `ui/`

This layer handles:

- windows
- frames
- dialogs
- charts
- buttons and widgets
- user interaction flow

It does not query the database directly.

Important files:

- `ui/app.py`
- `ui/views/dashboard.py`
- `ui/views/inventory.py`
- `ui/views/reports.py`
- `ui/components/sidebar.py`
- `ui/components/rounded_shapes.py`

### 2. Business / application layer

Located in `services/`

This layer handles:

- validation
- use-case orchestration
- authentication
- stock movement rules
- condition recording rules
- report generation
- dashboard aggregation
- settings operations
- session lifecycle management

Important files:

- `services/base.py`
- `services/auth_service.py`
- `services/inventory_service.py`
- `services/stock_adjustments_service.py`
- `services/damaged_expired_service.py`
- `services/dashboard_service.py`
- `services/view_models.py`

### 3. Data layer

Located in `data/`

This layer handles:

- database engine creation
- session factory creation
- ORM model definitions
- database initialization
- seed data creation

Important files:

- `data/db.py`
- `data/models.py`
- `data/seed.py`

## How the Layers Work Together

The application flow is:

1. `main.py` initializes the database and builds a `ServiceContainer`
2. `App` receives the service container
3. Views receive the services they need
4. Views call service methods for business operations
5. Services access the database through SQLAlchemy sessions
6. Services return view-model objects or summaries to the UI
7. The UI renders those results

The dependency direction is:

`UI -> Services -> Data`

## Service Base and Session Management

`services/base.py` defines `ServiceBase`, which gives all services a shared `session_scope()` context manager.

That provides:

- consistent session creation
- automatic commit on success
- automatic rollback on failure
- automatic session close in all cases

In addition, `data/db.py` configures SQLAlchemy with `expire_on_commit=False`, which helps prevent detached-instance errors when the UI consumes service results.

## Project Structure

```text
Comp-2140/
|-- main.py
|-- README.md
|-- requirements.txt
|-- docker-compose.yml
|-- data/
|   |-- db.py
|   |-- models.py
|   `-- seed.py
|-- services/
|   |-- auth_service.py
|   |-- base.py
|   |-- category_service.py
|   |-- dashboard_service.py
|   |-- damaged_expired_service.py
|   |-- inventory_service.py
|   |-- report_service.py
|   |-- security.py
|   |-- service_container.py
|   |-- settings_service.py
|   |-- slow_moving_service.py
|   |-- stock_adjustments_service.py
|   |-- user_service.py
|   `-- view_models.py
|-- ui/
|   |-- app.py
|   |-- styles.py
|   |-- components/
|   |   |-- rounded_shapes.py
|   |   |-- scrollable_frame.py
|   |   `-- sidebar.py
|   `-- views/
|       |-- categories.py
|       |-- damaged_expired.py
|       |-- dashboard.py
|       |-- inventory.py
|       |-- login.py
|       |-- reports.py
|       |-- settings.py
|       |-- slow_moving.py
|       |-- stock_adjustments.py
|       `-- users.py
`-- tests/
    `-- test_core_logic.py
```

## Database Design

The persistence layer models the following core tables:

- `categories`
- `items`
- `users`
- `stock_adjust`
- `item_conditions`
- `reports`
- `slow_moving_overstock`
- `config`

These are defined as SQLAlchemy classes in `data/models.py`.

### ASCII Schema

```text
+----------------+        +----------------+        +----------------+
|   categories   |        |      items     |        |     users      |
+----------------+        +----------------+        +----------------+
| category_id PK |<-------| item_id PK     |        | user_id PK     |
| name           |        | name           |        | username       |
| description    |        | category_id FK |        | password_hash  |
+----------------+        | price          |        | role           |
                          | quantity       |        | last_login     |
                          | current_stock  |        | created_at     |
                          | unit           |        +----------------+
                          | reorder_level  |
                          | created_at     |
                          | updated_at     |
                          +----------------+

+--------------------+    +--------------------+    +----------------+
|    stock_adjust    |    |  item_conditions   |    |    reports     |
+--------------------+    +--------------------+    +----------------+
| adjust_id PK       |    | condition_id PK    |    | report_id PK   |
| item_id FK         |    | item_id FK         |    | report_type    |
| user_id FK         |    | condition_type     |    | start_date     |
| adjust_type        |    | quantity           |    | end_date       |
| quantity           |    | reason             |    | generated_at   |
| reason             |    | cause              |    | user_id FK     |
| created_at         |    | cost_impact        |    | parameters     |
| adjusted_at        |    | recorded_at        |    | report_data    |
+--------------------+    +--------------------+    +----------------+

+------------------------+    +----------------+
| slow_moving_overstock  |    |     config     |
+------------------------+    +----------------+
| sm_id PK               |    | config_id PK   |
| item_id FK             |    | parameter_name |
| last_adjust_id FK      |    | parameter_value|
| flagged_at             |    | updated_at     |
| last_sold_date         |    +----------------+
| stock_quantity         |
| threshold_days         |
| threshold_quantity     |
| suggested_action       |
+------------------------+
```

## Requirements

- Python 3.10+
- PostgreSQL 12+

Python 3.10+ is required because the codebase uses modern type syntax such as `str | None`.

## Installation

### 1. Create and activate a virtual environment

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the database

Create a PostgreSQL database named `inventory_db`:

```sql
CREATE DATABASE inventory_db;
```

If needed, update the connection string in `data/db.py`.

## Windows PostgreSQL Setup

If you are using Windows:

1. Download PostgreSQL from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Run the installer
3. Keep `pgAdmin` and `Command Line Tools` selected
4. Set a password for the `postgres` user
5. Leave the default port as `5432` unless you need a different one

Then open Command Prompt or PowerShell and run:

```powershell
psql -U postgres -h localhost
```

Then inside the PostgreSQL shell:

```sql
CREATE DATABASE inventory_db;
\q
```

If `psql` is not recognized, add PostgreSQL's `bin` folder to your `PATH`. A common path is:

```text
C:\Program Files\PostgreSQL\17\bin
```

After that:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=.
python data\seed.py
python main.py
```

## Database Initialization and Seed Data

Initialize the schema and seed the application with sample data:

```bash
PYTHONPATH=. python3 data/seed.py
```

This script:

- creates tables
- clears old seedable data
- inserts sample categories
- inserts sample items
- inserts sample users
- inserts stock adjustments
- inserts condition records
- inserts reports and slow-moving related data when applicable

## Running the Application

```bash
PYTHONPATH=. python3 main.py
```

## Default Accounts

After seeding, these users are available:

- `admin` / `admin123`
- `staff` / `staff123`

## Testing

Run the automated tests with:

```bash
python3 -m unittest discover -s tests -q
```

The test suite uses in-memory SQLite rather than PostgreSQL so tests can run quickly and in isolation.

## Dependencies

- `SQLAlchemy` for ORM mapping and session management
- `psycopg2-binary` for PostgreSQL connectivity
- `matplotlib` for dashboard rendering and PDF report generation

## Why This Structure Is Better

This structure improves:

- maintainability, because responsibilities are more isolated
- testability, because services can be tested independently of the UI
- readability, because logic lives in named objects with clear purposes
- extensibility, because new use cases can be added as service methods or new service classes
- UI stability, because views consume prepared data objects rather than raw session-bound ORM entities

In short, the project uses classes and collaborating objects as architectural building blocks.
