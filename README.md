# Chatbot Interaction Study Platform

A Django-based platform for conducting chatbot interaction studies.

## Prerequisites

- Docker installed on your machine
- Access to a GPU-enabled environment (recommended for ML features)

## Running with Docker

### Building the Image

```bash
docker build -t general_purpose_pork .
```

### Running the Container

```bash
docker run -p 8086:8086 \
  -v $(pwd):/workspace \
  -e SECRET_KEY='your-secret-key-here' \
  -e DEBUG='True' \
  -e ALLOWED_HOSTS='localhost,127.0.0.1' \
  general_purpose_pork
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-5-154cd-x2z9e-)r2jrkkuhqyuwmhvsm=p!3yq%6np8%5%c%fa` |
| `DEBUG` | Enable debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Additional CSRF trusted origins | Empty |

### Accessing the Application

Once running, access the application at: **http://localhost:8086**

### Database Setup

On first run, you may need to apply migrations:

```bash
docker exec -it <container-id> python manage.py migrate
```

### Loading Initial Data

To load the IFS taxonomy data:

```bash
docker exec -it <container-id> python manage.py load_ifs_taxonomy
```

## Development

For local development without Docker:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8086
```

## Features

- User authentication and registration
- Chat interaction with AI models (Hugging Face, OpenRouter)
- Audio transcription via Whisper
- IFS taxonomy analysis
- Topic-based conversation flows
