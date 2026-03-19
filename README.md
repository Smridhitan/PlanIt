# PlanIt: Event Management Database System

PlanIt is a desktop database utility designed to manage event organization, session resource allocation, and general inventory analytics. It is built in Python, showcasing a modern graphical user interface powered by the `ttkbootstrap` framework, and communicates with a local MySQL database instance.

This system specifically highlights database interaction techniques including Create, Read, Update, and Delete (CRUD) operations, alongside automated inventory management relying heavily on MySQL Database Triggers.

## Core Features

- **Event Registry:** Structured data entry for registering complex event entities (Workshops, Keynote Talks, Seminars, etc.) into the main database.
- **Resource Allocation Module:** Specifically designed to demonstrate and invoke automated MySQL backend triggers by securely deducting warehouse inventory during allocation requests.
- **Analytics Dashboard:** Read-only interactive data grids providing immediate feedback on present inventory metrics and registered events.
- **Modern Interface Architecture:** A modular, single-window frontend equipped with dynamic Light/Dark mode capabilities, replacing traditional multi-window dialog workflows.
- **Exception Sanitization:** Intelligent error parsing delivering human-readable feedback on common dataset issues (e.g., network connectivity failures, foreign key constraint violations, and duplicate entries).

## Prerequisites

Ensure the following dependencies are available on the host machine prior to execution:

1. **Python 3** (Version 3.8 or higher)
2. **MySQL Server**, running locally on the standard port, configured with:
   - Target Database Name: `Dbms_Project`
   - Target Username: `root`
   - Target Password: `----`
   *(Configuration parameters can be modified within the `database.py` logic if your local environment utilizes different credentials).*

## Installation and Execution Guide

It is recommended to host the application within an isolated Python virtual environment to prevent package version conflicts across the operating system.

1. Navigate to the root directory via the terminal:
   ```bash
   cd DBMS_krtk/
   ```

2. Initialize and activate the virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate 
   ```

3. Install the required external library dependencies:
   ```bash
   pip install mysql-connector-python ttkbootstrap
   ```

4. Execute the main script to launch the interface:
   ```bash
   python3 main.py
   ```
   *(Note: The historically used `dbms_ui.py` script remains as a valid, backwards-compatible entry point.)*

## Application Architecture

The application is refactored to prioritize software engineering best practices, specifically the separation of concerns:

- `main.py`: The primary entry point. Manages the core Tkinter loop, sidebar routing state, and top-level theme configurations.
- `ui_windows.py`: The presentation layer. Exclusively responsible for layout engineering, form fields, and rendering tree grids without relying on raw SQL strings.
- `database.py`: The Data Access Object (DAO). Serves as the single source of truth for all database cursor interactions, connection logic, and table queries.
- `styles.py`: The centralized design system containing padding integers, static typographic references, and theme logic.
