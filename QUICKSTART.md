# StyleMail POC - Quick Start Guide

## 🚀 Getting Started in 2 Minutes

### 1. Start the Application

```bash
# Make sure you have Docker installed
docker compose up -d
```

Wait for the services to start (about 10 seconds).

### 2. Set Your OpenAI API Key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

Then restart:

```bash
docker compose down
docker compose up -d
```

### 3. Load Demo Data

```bash
python3 demo_seed.py
```

This will create 6 different users with unique writing styles.

### 4. Try the Web Interface

Open your browser to: **http://localhost:8000/static/demo.html**

Or use the API directly:

```bash
# Seed a user's style
curl -X POST "http://localhost:8000/seed" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "samples": [
      "Hey! Thanks for reaching out.",
      "Looking forward to chatting soon!",
      "Let me know if you need anything else."
    ]
  }'

# Generate an email
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "subject": "Quick Update",
    "prompt": "Let them know the meeting is rescheduled to Friday"
  }'
```

## 📚 Explore More

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Full README**: See [README.md](README.md)

## 🛑 Stopping the Application

```bash
docker compose down
```

## 🔧 Troubleshooting

**Port 8000 already in use?**

```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
```

**Redis connection issues?**

```bash
# Check if Redis is running
docker compose ps
```

**API not responding?**

```bash
# Check logs
docker compose logs app
```

## 💡 Next Steps

1. Try different writing samples to see how the AI adapts
2. Experiment with different prompts and subjects
3. Compare emails generated for different user profiles
4. Check out the code in `stylemail/` to understand how it works

---

Need help? Check the main [README.md](README.md) for detailed documentation.
