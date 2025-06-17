# Telegram Flat Tracker

Telegram Flat Tracker is a web app that automatically collects flat/apartment rental listings from Telegram groups and displays them in a dashboard for easier tracking and analysis.

## Features

- Fetches flat/apartment listings from Telegram groups using Telegram API
- Extracts and structures listing information (e.g. price, location, size, contact info)
- Store listings in a local SQLite database
- Displays listings in an interactive, searchable, and filterable dashboard
- Helps renters keep track of available flats in one centralized place

## Usage

This app simplifies the flat hunting process by aggregating listings from multiple Telegram channels into one interface, allowing users to:

- Browse available flats
- Filter listings based on preferences
- Avoid missing out on new listings posted across various Telegram groups

## Tech Stack

- Backend: Python, FastAPI
- Frontend: React
- Database: SQLite

📦 Setup
Clone the repo:

```bash
git clone https://github.com/Dimri/teleflattracker.git
cd teleflattracker
```

# Install dependencies:
## Backend
```bash
cd backend
uv venv 
source .venv/bin/activate
uv pip install -r requirements.txt
```
## Frontend
```bash
cd frontend
npm install
```

Setup environment variables
```bash
export OPENAI_API_KEY=sk-xxx
# this is for telegram client
export API_HASH=xxx
export API_ID=xxx
```

Start the application:

# Backend
```bash
cd backend/src/flattracker/api
uvicorn app:app --reload
```

# Frontend
```bash
cd frontend
npm run dev
```

📄 License


MIT License
