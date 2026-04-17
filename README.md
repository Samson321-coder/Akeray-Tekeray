---
title: Akeray Tekeray Bot
emoji: 🏠
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# Akeray Tekeray Telegram Bot

This is a Telegram rental bot designed to run on Hugging Face Spaces using Docker and connect to a Neon.tech PostgreSQL database.

## Deployment Instructions

### 1. Setup Neon.tech Database
- Create a project at [neon.tech](https://neon.tech).
- Get your connection string (e.g., `postgres://user:password@host/dbname?sslmode=require`).

### 2. Configure Hugging Face Space
- Create a new **Space** on Hugging Face.
- Select **Docker** as the SDK.
- Go to **Settings > Variables and secrets**.
- Add the following **Secrets**:
  - `BOT_TOKEN`: Your Telegram Bot API token.
  - `ADMIN_IDS`: Comma-separated list of your Telegram User IDs.
  - `DATABASE_URL`: Your Neon.tech connection string.
  - `GEMINI_API_KEY`: Your Google AI Studio API key.
  - `WEBHOOK_URL`: (Recommended) The URL of your Space + `/` (e.g., `https://user-space.hf.space/`).

### 3. Local Development
To run locally, copy `.env.example` to `.env` and fill in the values, then:
```bash
pip install -r requirements.txt
python main.py
```

## Tech Stack
- **Bot Framework**: `python-telegram-bot`
- **Database**: PostgreSQL (Neon.tech) / SQLite (Fallback)
- **AI**: Google Gemini (gemini-2.0-flash-exp)
- **Image Processing**: Pillow (Watermarking)
