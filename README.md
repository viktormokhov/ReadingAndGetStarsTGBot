# Telegram Reading Bot

## Overview
This project is a Telegram bot designed to help users practice reading skills through interactive tasks and questions. The bot generates texts on various topics, asks questions about the content, and tracks users' progress. It features a reward system with stars and badges to motivate users.

## Features
- Text generation on various educational topics
- Interactive quizzes with multiple-choice questions
- Progress tracking and statistics
- Reward system with stars and badges
- Card collection feature
- Admin panel with user management and statistics

## Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB
- Telegram Bot Token
- OpenAI API Key
- Google Gemini API Key (optional)

### Steps
1. Clone the repository:
   ```
   git clone <repository-url>
   cd telegram-reading-bot
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   TG_ADMIN_IDS=your_telegram_id
   TG_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB_NAME=telegram_bot
   ```

5. Run the bot:
   ```
   python main.py
   ```

## Configuration
The bot's behavior can be configured through the `core/config.py` file:

- `DAILY_LIMIT_PER_THEME`: Maximum number of questions per theme per day (default: 5)
- `CARDS_PER_PAGE`: Number of cards displayed per page (default: 4)
- `MAX_ATTEMPTS`: Maximum number of wrong attempts allowed per quiz (default: 3)
- `MAX_RETRY`: Maximum number of retries for API calls (default: 4)

The file also contains definitions for:
- Reading topics organized by categories
- Badge system with different achievement levels
- Badge labels for different tiers

## Usage

### User Commands
- `/reading` - Start a reading session
- `/cards` - View your card collection
- `/stats` - View your statistics
- `/withdrawal` - Check your balance
- `/settings` - Adjust your settings
- `/admin` - Access admin panel (for admins only)

### Reading Flow
1. User selects a category and topic
2. Bot generates a text and presents it to the user
3. Bot asks questions about the text
4. User answers the questions
5. Bot provides feedback and rewards

### Reward System
- Users earn stars for correct answers
- The number of stars depends on text length and number of errors
- Additional bonuses are awarded for streaks of successful answers
- Progress is tracked by topic
- Users earn badges based on their total stars

## Architecture

### Main Components
- **main.py**: Entry point, sets up the bot, middleware, and routers
- **core/**: Core functionality
  - **config.py**: Configuration constants and tables
  - **database/**: Database initialization and models
  - **services/**: Business logic services
  - **middleware/**: Request processing middleware
  - **ai/**: AI integration for text generation
  - **ui.py**: User interface components
- **handlers/**: Telegram message and callback handlers
  - **admin/**: Admin panel handlers
  - **reading/**: Reading session handlers
  - **cards.py**: Card collection handlers
  - **users/**: User-related handlers

### Database
The bot uses both SQLite (via SQLAlchemy) and MongoDB:
- SQLite: User data, progress, and statistics
- MongoDB: Generated texts, questions, and cards

### AI Integration
The bot uses AI services to generate texts and questions:
- OpenAI API for text generation
- Google Gemini API (optional) for additional AI capabilities

## Limitations
- Daily limit of questions per theme
- Limited number of wrong attempts per quiz
- Access restricted to approved users only

## License
[Include license information here]