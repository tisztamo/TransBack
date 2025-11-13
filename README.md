# TransBack - Translation Tool

A Python script that translates text files using OpenRouter API and performs back-translation to verify accuracy.

## Features

- Translate text files from one language to another
- Automatic back-translation to verify translation quality
- Uses OpenRouter API with Qwen models
- Supports custom source/target languages

## Prerequisites

- Python 3.7+ (with type hints support for `str|None` syntax, Python 3.10+ recommended)
- OpenRouter API key

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenRouter API key:**
   
   On Windows (PowerShell):
   ```powershell
   $env:OPENROUTER_API_KEY="your-api-key-here"
   ```
   
   On Windows (Command Prompt):
   ```cmd
   set OPENROUTER_API_KEY=your-api-key-here
   ```
   
   On Linux/Mac:
   ```bash
   export OPENROUTER_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file (requires python-dotenv package):
   ```
   OPENROUTER_API_KEY=your-api-key-here
   ```

## Usage

### Option 1: Web UI (Recommended)

The easiest way to use TransBack is through the web interface:

1. **Start the API server:**
   ```bash
   python api.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Use the interface:**
   - Enter your text in the textarea
   - Configure source/target languages (default: hu → en)
   - Click "Translate" button
   - View the translated text, back-translation, and quality review

The web UI provides a clean, modern interface with real-time feedback.

### Option 2: API Endpoint

Use the REST API directly for integration with other applications:

**Endpoint:** `POST http://localhost:5000/translate`

**Request:**
```json
{
  "text": "Your text to translate",
  "source": "hu",
  "target": "en",
  "model": "qwen/qwen3-235b-a22b-2507"
}
```

**Response:**
```json
{
  "translated": "Translated text",
  "back_translated": "Back-translated text",
  "review": "Quality review result"
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Helló világ", "source": "hu", "target": "en"}'
```

### Option 3: Command Line

Basic usage:
```bash
python translate.py input.txt output.txt
```

With custom languages:
```bash
python translate.py input.txt output.txt --source hu --target en
```

With custom model:
```bash
python translate.py input.txt output.txt --model qwen/qwen3-235b-a22b-2507
```

#### Arguments

- `input_file` - Path to the input text file to translate (required)
- `output_file` - Path to save the translated output (required)
- `--source` - Source language code (default: `hu`)
- `--target` - Target language code (default: `en`)
- `--model` - Model to use (default: `qwen/qwen3-235b-a22b-2507`)
- `--app-url` - Optional HTTP referer URL
- `--app-title` - Optional app title

#### Output Files

- `output.txt` - Contains the translated text
- `back.txt` - Contains the back-translated text (translated back to source language)
- `review.txt` - Contains the quality review

## Example

```bash
# Translate Hungarian to English
python translate.py input.txt output.txt --source hu --target en
```

This will:
1. Read text from `input.txt`
2. Translate it from Hungarian to English
3. Save the translation to `output.txt`
4. Back-translate to Hungarian and save to `back.txt`
5. Compare meanings and save review to `review.txt`

## Getting an OpenRouter API Key

1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for an account
3. Navigate to your API keys section
4. Create a new API key
5. Set it as the `OPENROUTER_API_KEY` environment variable

## Railway Deployment

TransBack is configured for easy deployment on [Railway](https://railway.app/).

### Quick Deploy

1. **Connect your repository to Railway:**
   - Sign up/login to [Railway](https://railway.app/)
   - Click "New Project"
   - Select "Deploy from GitHub repo" (or your Git provider)
   - Choose the TransBack repository

2. **Set environment variables:**
   - In your Railway project, go to the "Variables" tab
   - Add `OPENROUTER_API_KEY` with your API key value

3. **Deploy:**
   - Railway will automatically detect the `Procfile` and deploy your app
   - The app will be available at a Railway-provided URL

### Configuration Files

- `Procfile` - Tells Railway how to run the app using gunicorn
- `railway.json` - Railway-specific configuration
- `requirements.txt` - Python dependencies (includes gunicorn for production)

The app automatically:
- Uses the `PORT` environment variable provided by Railway
- Disables debug mode in production
- Runs with gunicorn as the production WSGI server

### Environment Variables

Required:
- `OPENROUTER_API_KEY` - Your OpenRouter API key

Optional:
- `PORT` - Port number (automatically set by Railway)
- `RAILWAY_ENVIRONMENT` - Automatically set by Railway (used to disable debug mode)

