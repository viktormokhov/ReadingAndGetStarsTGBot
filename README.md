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
   TG_ADMIN_ID=your_telegram_id
   TG_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB_NAME=telegram_bot
   BACKEND_URL=https://your-backend-url.com
   BACKEND_API_KEY=your_api_key_here

   # API Server Configuration
   API_SERVER_HOST=0.0.0.0
   API_SERVER_PORT=8000
   # API_SERVER_SSL_CERT=path/to/cert.pem
   # API_SERVER_SSL_KEY=path/to/key.pem
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
- **api/**: FastAPI application for external calls
  - **app.py**: Main FastAPI application
  - **server.py**: Server configuration and startup
  - **routers/**: API endpoint routers
    - **reading.py**: Reading-related endpoints
    - **users.py**: User-related endpoints

### Database
The bot uses both SQLite (via SQLAlchemy) and MongoDB:
- SQLite: User data, progress, and statistics
- MongoDB: Generated texts, questions, and cards

### AI Integration
The bot uses AI services to generate texts and questions:
- OpenAI API for text generation
- Google Gemini API (optional) for additional AI capabilities

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
   from api.clients import backend_client

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

### Using the Batch Script

1. A batch script `start_bot.bat` is included in the repository. This script:
   - Changes to the bot's directory
   - Activates the virtual environment (if needed)
   - Starts the bot

2. You can run this script manually to start the bot:
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
[Include license information here]
