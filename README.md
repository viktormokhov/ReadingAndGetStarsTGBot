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
- Python 3.12 or higher
- PostgreSQL
- MongoDB
- Redis
- Telegram Bot Token
- OpenAI API Key
- Google Gemini API Key
- Cloudflare API Key (for image generation)
- OpenRouter API Key (for DeepSeek models)
- ImgBB API Key (for image hosting)

### Steps
1. Clone the repository:
   ```
   git clone <repository-url>
   cd telegram-reading-bot
   ```

2. Install Poetry (if not already installed):
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   Or on Windows:
   ```
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

3. Install the required dependencies:
   ```
   poetry install
   ```

4. Activate the Poetry virtual environment:
   ```
   poetry shell
   ```

5. Create a `.env` file in the root directory with the following variables:
   ```
   # Telegram Configuration
   TG_ADMIN_ID=your_telegram_id
   TG_BOT_TOKEN=your_telegram_bot_token
   TG_WEBHOOK_URL=https://your-domain.com:8443/api/v1/telegram/telegram-webhook
   TG_WEBHOOK_TOKEN=your_webhook_token

   # AI Service API Keys
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
   GOOGLE_GEMINI_PROXY_URL=https://your-proxy-url/v1/models/
   CLOUDFLARE_API_KEY=your_cloudflare_api_key
   CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
   OPENROUTER_API_KEY=your_openrouter_api_key
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   GROK_API_KEY=your_grok_api_key
   IMGBB_API_KEY=your_imgbb_api_key

   # Database Configuration
   POSTGRES_USER=your_postgres_user
   POSTGRES_PASSWORD=your_postgres_password
   POSTGRES_DB=your_postgres_db
   # MongoDB is configured in settings.py with default values:
   # mongodb_uri=mongodb://localhost:27017
   # mongodb_name=telegram_bot

   # Backend Communication
   BACKEND_URL=https://your-backend-url.com/api
   BACKEND_API_KEY=your_backend_api_key
   ```

6. Run the bot:
   ```
   # Using Poetry
   poetry run python main.py

   # Or if you're already in the Poetry shell
   python main.py
   ```

   This will start both the Telegram bot and the FastAPI server.

## Configuration
The bot's behavior can be configured through the `config/` directory:

### Main Settings (`config/settings.py`)
This file contains the configuration for:
- Telegram bot settings
- AI service providers (OpenAI, Google Gemini, Cloudflare, DeepSeek)
- Database connections (PostgreSQL, MongoDB)
- Backend communication

### Constants (`config/constants.py`)
This file contains various constants used throughout the application:
- `DAILY_LIMIT_PER_THEME`: Maximum number of questions per theme per day
- `CARDS_PER_PAGE`: Number of cards displayed per page
- `MAX_ATTEMPTS`: Maximum number of wrong attempts allowed per quiz
- `MAX_RETRY`: Maximum number of retries for API calls

### Content (`config/content.py`)
This file contains definitions for:
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
- **main.py**: Entry point, sets up the FastAPI application, database connections, and routers
- **config/**: Configuration files
  - **settings.py**: Environment variables and settings
  - **constants.py**: Application constants
  - **content.py**: Content definitions (topics, badges, etc.)
- **core/**: Core functionality using a clean architecture approach
  - **domain/**: Domain models and interfaces
    - **models/**: Domain entities (User, State, etc.)
    - **interfaces/**: Abstract interfaces
    - **services/**: Domain-specific services
  - **application/**: Application services and use cases
    - **commands/**: Command handlers
    - **services/**: Application services
    - **interfaces/**: Repository interfaces
    - **security/**: Security-related functionality
  - **infrastructure/**: External services and data access
    - **clients/**: External API clients (MongoDB, PostgreSQL, Redis, AI services)
    - **database/**: Database models and repositories
    - **storage/**: Storage services
    - **telegram/**: Telegram client implementation
  - **presentation/**: API endpoints and controllers
    - **health/**: Health check endpoints
    - **telegram/**: Telegram webhook handling
    - **user/**: User-related endpoints
- **bot/**: Telegram bot functionality
  - **handlers/**: Message and callback handlers
    - **admin/**: Admin panel handlers
    - **reading/**: Reading session handlers
    - **profile/**: User profile handlers
    - **users/**: User-related handlers
  - **middleware/**: Request processing middleware
  - **services/**: Bot-specific services
  - **utils/**: Utility functions
- **api/**: Additional API endpoints
  - **routers/**: API endpoint routers
    - **reading.py**: Reading-related endpoints
    - **user.py**: User-related endpoints
    - **users.py**: User management endpoints

### Database
The bot uses PostgreSQL (via SQLAlchemy), MongoDB, and Redis:
- PostgreSQL: User data, progress, and statistics
- MongoDB: Generated texts, questions, and cards
- Redis: Caching, session data, and rate limiting

### AI Integration
The bot uses multiple AI services to generate texts, questions, and images:
- OpenAI API for text generation (GPT models) and image generation (DALL-E)
- Google Gemini API for text generation
- Cloudflare AI for image generation (Stable Diffusion XL)
- DeepSeek models via OpenRouter API for text generation
- ImgBB API for image hosting

## API for External Calls

The bot includes a FastAPI application that exposes certain functionality for external calls. The API server runs alongside the Telegram bot on port 8000 by default.

### Server Configuration

You can configure the API server by setting the following environment variables in your `.env` file:

```
# API Server Configuration
API_SERVER_HOST=0.0.0.0  # Bind to all network interfaces
API_SERVER_PORT=8000     # Port to listen on
# API_SERVER_SSL_CERT=path/to/cert.pem  # Path to SSL certificate for HTTPS
# API_SERVER_SSL_KEY=path/to/key.pem    # Path to SSL key for HTTPS
```

- Setting `API_SERVER_HOST` to `0.0.0.0` allows connections from any IP address
- To restrict access to local connections only, set `API_SERVER_HOST` to `127.0.0.1`
- For HTTPS support, uncomment and set the `API_SERVER_SSL_CERT` and `API_SERVER_SSL_KEY` variables

When the server starts, it will display a message showing the host and port it's listening on.

### Accessing the API from External Clients

External clients can access your API using the following URL format:

```
http://<your-server-ip>:<port>/endpoint
```

For example, if your server's public IP address is 94.131.111.168 and you're using port 8000:

```
http://94.131.111.168:8000/health  # Health check endpoint
http://94.131.111.168:8000/users/123456  # Get user info
```

If you've enabled HTTPS with SSL certificates:

```
https://94.131.111.168:8000/health
```

#### Network Configuration

To allow external access to your API server:

1. Make sure your firewall allows incoming connections on the configured port (8000 by default)
2. If your server is behind a router, configure port forwarding to direct traffic to your server
3. Consider using a domain name instead of an IP address for easier access

#### Security Considerations

When exposing your API to the internet:

1. Always use HTTPS in production environments
2. Implement proper authentication for all endpoints
3. Consider using a reverse proxy like Nginx for additional security features
4. Regularly update your SSL certificates

### Endpoints

#### Reading Endpoints

- `POST /reading/generate`: Generate reading content with questions
  - Request body: `{ "user_id": int, "category": string, "theme": string }`
  - Response: `{ "text": string, "questions": array, "card_title": string, "word_count": int }`

- `POST /reading/check-limit`: Check if a user has exceeded their daily limit for a theme
  - Request body: `{ "user_id": int, "theme": string }`
  - Response: `{ "limit_exceeded": boolean, "current_count": int, "max_limit": int }`

#### User Endpoints

- `POST /users/create`: Create a new user
  - Request body: `{ "user_id": int, "name": string }`
  - Response: User information with stats

- `GET /users/{user_id}`: Get user information
  - Response: User information with stats

- `PATCH /users/update-age`: Update user age
  - Request body: `{ "user_id": int, "age": int }`
  - Response: Updated user information

- `GET /users/{user_id}/stats`: Get detailed user statistics
  - Response: User statistics including theme-specific stats

### Example Usage

```python
import requests

# Generate reading content
response = requests.post(
    "http://localhost:8000/reading/generate",
    json={"user_id": 123456, "category": "Science", "theme": "Astronomy"}
)
content = response.json()
print(f"Generated text with {content['word_count']} words")

# Get users stats
response = requests.get("http://localhost:8000/users/123456/stats")
stats = response.json()
print(f"User has {stats['stars']} stars and {stats['total_questions']} total questions")
```

### Backend Communication

The API can communicate with an external backend server using the configured BACKEND_URL and BACKEND_API_KEY. To use this functionality:

1. Set the appropriate values in your `.env` file:
   ```
   BACKEND_URL=https://your-backend-url.com
   BACKEND_API_KEY=your_api_key_here
   ```

2. Use the backend client in your code:
   ```python
   from api import backend_client

   # Make a GET request to the backend
   data = await backend_client.get("endpoint/path")

   # Make a POST request with data
   response = await backend_client.post("endpoint/path", {"key": "value"})

   # Make a PUT request
   result = await backend_client.put("endpoint/path", {"id": 1, "name": "Updated"})

   # Make a DELETE request
   await backend_client.delete("endpoint/path", {"id": 1})
   ```

## Running at System Startup

To configure the bot to start automatically when your Windows system boots up, follow these steps:

### Creating a Startup Script

1. Create a batch script `start_bot.bat` in the repository root with the following content:
   ```batch
   @echo off
   cd /d %~dp0
   call poetry run python main.py
   pause
   ```

2. This script:
   - Changes to the bot's directory
   - Runs the bot using Poetry
   - Pauses to keep the window open if there are errors

3. You can run this script manually to start the bot:
   ```
   .\start_bot.bat
   ```

### Setting Up Automatic Startup with Windows Task Scheduler

1. Open Windows Task Scheduler (search for "Task Scheduler" in the Start menu)
2. Click "Create Basic Task" in the right panel
3. Enter a name (e.g., "Telegram Reading Bot") and description, then click Next
4. Select "When the computer starts" as the trigger, then click Next
5. Select "Start a program" as the action, then click Next
6. Browse to select the `start_bot.bat` file in your bot's directory, then click Next
7. Review your settings and click Finish

### Additional Configuration Options

For more advanced configuration:
1. After creating the basic task, right-click it and select "Properties"
2. Go to the "General" tab and check "Run with highest privileges"
3. Go to the "Settings" tab and configure additional options as needed:
   - Check "Run task as soon as possible after a scheduled start is missed"
   - Check "If the task fails, restart every:" and set appropriate values

## Limitations
- Daily limit of questions per theme
- Limited number of wrong attempts per quiz
- Access restricted to approved users only
- API access is for external calls only

## License
This project is licensed under the terms of the license agreement provided with the source code. Please contact the repository owner for more information about licensing terms and conditions.
