# Study Anything - Backend Server

A Flask backend for a study planning and quiz generation application that leverages AI to help users prepare for exams.

## Features

- **Exam Management**: Create and store exam details, including materials, topics, and scheduling.
- **AI-Powered Study Plans**: Generate personalized study plans based on exam requirements and user preferences.
- **Quiz Generation**: Create topic-specific quizzes to test knowledge and reinforce learning.
- **External Knowledge Integration**: Optionally enhance content generation with real-world information via the Perplexity API.

## Project Structure

```
├── app/
│   ├── models/         # Database models and connection
│   ├── routes/         # API endpoints
│   ├── services/       # External service integrations (LLM, search)
│   └── utils/          # Helper functions
├── .env.example        # Template for environment variables
├── app.py              # Main application entry point
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Database Schema

The application uses Supabase as its database with the following tables:

- **Exams**: Stores exam details, topics, and user preferences
- **exam_materials**: References to study materials for an exam
- **StudyPlan**: High-level study plans generated for exams
- **StudyPlanDays**: Detailed day-by-day breakdown of study tasks
- **Quiz**: Metadata for generated quizzes
- **Questions**: Multiple-choice questions for quizzes

## API Endpoints

### Exam Management
- `POST /api/exams`: Create a new exam
- `GET /api/exams`: List all exams
- `GET /api/exams/{exam_id}`: Get exam details

### Study Plans
- `POST /api/plan/generate`: Generate a study plan for an exam
- `GET /api/plan/{exam_id}`: Get the study plan for an exam
- `POST /api/plan/day/{day_id}/complete`: Mark a study day as completed

### Quizzes
- `POST /api/quiz/generate`: Generate a quiz for an exam
- `GET /api/quiz/{quiz_id}`: Get a specific quiz with questions
- `GET /api/quiz/exam/{exam_id}`: Get all quizzes for an exam

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/study-anything-server.git
   cd study-anything-server
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase, OpenAI, and Perplexity API keys
   ```

4. Run the application:
   ```bash
   flask run
   # or
   python app.py
   ```

## Environment Variables

- `FLASK_APP`: Set to "app.py"
- `FLASK_ENV`: "development" or "production"
- `SECRET_KEY`: Flask secret key for sessions
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key
- `PERPLEXITY_API_KEY`: API key for Perplexity (for internet search)
- `OPENAI_API_KEY`: API key for OpenAI (for LLM functions)
- `JWT_SECRET_KEY`: Secret key for JWT authentication

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: Supabase (PostgreSQL)
- **AI Services**: 
  - OpenAI GPT for study plans and quiz generation
  - Perplexity API for additional exam information

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request 