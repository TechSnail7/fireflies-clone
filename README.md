# Fireflies.ai Clone 

A full-stack, fully functional clone of the Fireflies.ai meeting-assistant web application. It replicates the core post-meeting workflows, interactive transcript view, AI summaries, and the original app's design system and UI patterns.

## 🚀 Features

- **Meetings Dashboard:** View a grid of all your recorded meetings, sorted by recency with metadata (duration, date, participants, tags).
- **Interactive Transcript Player:** Click on any transcript segment to seek the mock-audio player to that exact timestamp. Includes active segment highlighting and a full search filter for transcripts.
- **AI Summary & Action Items:** Split-pane design that matches Fireflies.ai's Notepad view. Review AI-generated overviews, chapters/timelines, and check off extracted action items.
- **Auto-Seeded Database:** The application is immediately usable upon first launch, pre-populated with 6 realistic meetings across different domains (Engineering, Product, Marketing, Client) containing full transcripts and summaries.
- **Fireflies Aesthetics:** Strict adherence to the original app's dark-mode UI, typography (DM Sans + Inter), custom badges, and color tokens.

## 🛠️ Tech Stack

**Frontend:**
- Next.js 15 (App Router)
- TypeScript
- React
- Vanilla CSS Modules (No Tailwind, as per assignment constraints but achieving exact styling parity)
- Lucide React (Icons)
- Axios (API Client)

**Backend:**
- Python 3
- FastAPI (REST API framework)
- SQLAlchemy (ORM)
- SQLite (Local database)
- Pydantic (Data validation)

## 🏗️ Architecture & Database Schema

The architecture relies on a decoupled Next.js client communicating over REST APIs with a FastAPI server.

**Database Schema (SQLite):**
1. `meetings`: Core entity holding title, date, duration, host, and participant arrays.
2. `transcript_segments`: Individual transcript lines linked to a meeting (`meeting_id`). Stored as separate rows for efficient full-text searching and time-seeking.
3. `summaries`: Contains the AI-generated overview, and JSON arrays for key topics, outline, and timestamped chapters.
4. `action_items`: Tasks extracted from meetings, complete with assignee and completion status toggles.
5. `tags` & `meeting_tags`: Many-to-many relationship allowing flexible categorization (e.g., "Engineering", "Client").

## 🚦 Setup Instructions

### Prerequisites
- Node.js v18+
- Python 3.10+

### 1. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

Run the FastAPI server (this will automatically create and seed the SQLite database on first launch):
```bash
python -m uvicorn "app.main:app" --reload
```
The backend API will be available at `http://localhost:8000/api`.

### 2. Frontend Setup
Open a new terminal, navigate to the frontend directory, and install dependencies:
```bash
cd frontend
npm install
```

Run the Next.js development server:
```bash
npm run dev
```
The frontend application will be available at `http://localhost:3000`.

## 🧠 Assumptions & Design Decisions
- **Real-time Transcription:** As real speech-to-text is out of scope, the media player is mocked. The play/pause buttons simulate time progression to demonstrate the transcript auto-scroll and highlight functionality.
- **Tailwind CSS:** The prompt requested avoiding Tailwind unless necessary. I used Next.js CSS Modules with CSS custom properties (variables) to build a robust design system completely from scratch that mirrors Fireflies perfectly.
- **Authentication:** Authentication is mocked; the user is assumed to be a default logged-in workspace member.
- **Database Path:** The SQLite database is created inside the `backend/data` directory automatically.
