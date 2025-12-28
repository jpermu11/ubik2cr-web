# Python Flask Application

## Overview
A Flask web application with PostgreSQL database integration.

## Project Structure
- `main.py` - Main Flask application with database configuration
- `models.py` - SQLAlchemy database models
- `pyproject.toml` - Python project dependencies

## Database
PostgreSQL database is configured using SQLAlchemy. The connection uses the `DATABASE_URL` environment variable.

### Models
- `User` - Basic user model with id, username, and email fields

## Running the Application
The Flask server runs on port 5000.

## Recent Changes
- Dec 28, 2025: Added PostgreSQL database with SQLAlchemy integration
