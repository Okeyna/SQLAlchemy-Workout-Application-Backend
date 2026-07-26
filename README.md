# Workout Tracker API

A complete backend API for a workout tracking application. Built with Flask, SQLAlchemy, and Marshmallow, it manages workouts, exercises, and their many‑to‑many relationships through a join table that tracks reps, sets, and duration.

## Project Description

Personal trainers can use this API to create workouts, manage exercises, and add exercises to specific workouts with performance metrics. All data is persisted in a SQLite database (easily changeable to PostgreSQL/MySQL). The API includes:

- **Full CRUD** for workouts and exercises (no update endpoints required).
- **Cascade delete** – removing a workout or exercise automatically deletes its join table entries.
- **Multiple layers of validation** – database constraints, model‑level validators, and Marshmallow schema validations.
- **Detailed responses** – GET endpoints for single resources include nested join data.

## Installation

1. **Clone the repository** and `cd` into the project root.

2. **Install dependencies** with Pipenv:

   ```bash
   pipenv install
   ```
3. **Enter the virtual environment:**

   ```bash
   pipenv shell
   ```
4. **Set up the database (SQLite by default). Run migrations:**

   ```bash
   flask db init          # only if migrations/ folder doesn't exist
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
5. **Seed the database with sample data:**

   ```bash
   python seed.py
   ```
## Run the API
**Start the Flask development server:**

   ```bash
   flask run
   ```