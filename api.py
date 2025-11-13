# api.py
import os
import sys
import json
import logging
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from translate import translate, compare_meanings

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@app.route('/')
def index():
    """Serve the HTML frontend"""
    return send_from_directory('.', 'index.html')

@app.route('/translate', methods=['POST'])
def translate_text():
    """
    Translate text endpoint.
    
    Expected JSON body:
    {
        "text": "Text to translate",
        "source": "hu",  // optional, default: "hu"
        "target": "en",  // optional, default: "en"
        "model": "qwen/qwen3-235b-a22b-2507"  // optional
    }
    
    Returns JSON:
    {
        "translated": "Translated text",
        "back_translated": "Back-translated text",
        "review": "Review/comparison result"
    }
    """
    try:
        # Get API key from environment
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            logging.error("OPENROUTER_API_KEY environment variable not set")
            return jsonify({"error": "Server configuration error: API key not set"}), 500
        
        # Parse request body
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400
        
        text = data.get('text')
        if not text:
            return jsonify({"error": "Missing required field: text"}), 400
        
        source = data.get('source', 'hu')
        target = data.get('target', 'en')
        model = data.get('model', 'qwen/qwen3-235b-a22b-2507')
        
        logging.info(f"Translation request: {len(text)} chars, {source} -> {target}, model: {model}")
        
        # Step 1: Translate to target language
        logging.info("Step 1/3: Translating to target language")
        translated = translate(text, source, target, api_key, model)
        
        # Step 2: Back-translate to source language
        logging.info("Step 2/3: Back-translating to source language")
        back_translated = translate(translated, target, source, api_key, model)
        
        # Step 3: Compare meanings
        logging.info("Step 3/3: Comparing meanings")
        review = compare_meanings(text, back_translated, source, api_key, model)
        
        logging.info("Translation completed successfully")
        
        return jsonify({
            "translated": translated,
            "back_translated": back_translated,
            "review": review
        })
    
    except Exception as e:
        logging.error(f"Translation error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/translate/stream', methods=['POST'])
def translate_text_stream():
    """
    Streaming translation endpoint using Server-Sent Events (SSE).
    
    Expected JSON body:
    {
        "text": "Text to translate",
        "source": "hu",  // optional, default: "hu"
        "target": "en",  // optional, default: "en"
        "model": "qwen/qwen3-235b-a22b-2507"  // optional
    }
    
    Returns SSE stream with events:
    - event: translated (data: {"translated": "..."})
    - event: back_translated (data: {"back_translated": "..."})
    - event: review (data: {"review": "..."})
    - event: complete (data: {})
    - event: error (data: {"error": "..."})
    """
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logging.error("OPENROUTER_API_KEY environment variable not set")
        def error_gen():
            yield f"event: error\ndata: {json.dumps({'error': 'Server configuration error: API key not set'})}\n\n"
        return Response(error_gen(), mimetype='text/event-stream')
    
    # Parse request body
    data = request.get_json()
    if not data:
        def error_gen():
            yield f"event: error\ndata: {json.dumps({'error': 'Request body must be JSON'})}\n\n"
        return Response(error_gen(), mimetype='text/event-stream')
    
    text = data.get('text')
    if not text:
        def error_gen():
            yield f"event: error\ndata: {json.dumps({'error': 'Missing required field: text'})}\n\n"
        return Response(error_gen(), mimetype='text/event-stream')
    
    source = data.get('source', 'hu')
    target = data.get('target', 'en')
    model = data.get('model', 'qwen/qwen3-235b-a22b-2507')
    
    logging.info(f"Streaming translation request: {len(text)} chars, {source} -> {target}, model: {model}")
    
    def generate(text, source, target, api_key, model):
        try:
            # Step 1: Translate to target language
            logging.info("Step 1/3: Translating to target language")
            translated = translate(text, source, target, api_key, model)
            event_data = json.dumps({'translated': translated})
            logging.info(f"Sending translated event: {len(event_data)} chars")
            yield f"event: translated\ndata: {event_data}\n\n"
            
            # Step 2: Back-translate to source language
            logging.info("Step 2/3: Back-translating to source language")
            back_translated = translate(translated, target, source, api_key, model)
            event_data = json.dumps({'back_translated': back_translated})
            logging.info(f"Sending back_translated event: {len(event_data)} chars")
            yield f"event: back_translated\ndata: {event_data}\n\n"
            
            # Step 3: Compare meanings
            logging.info("Step 3/3: Comparing meanings")
            review = compare_meanings(text, back_translated, source, api_key, model)
            event_data = json.dumps({'review': review})
            logging.info(f"Sending review event: {len(event_data)} chars")
            yield f"event: review\ndata: {event_data}\n\n"
            
            logging.info("Streaming translation completed successfully")
            yield f"event: complete\ndata: {json.dumps({})}\n\n"
        
        except Exception as e:
            logging.error(f"Streaming translation error: {str(e)}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(text, source, target, api_key, model), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    })

if __name__ == '__main__':
    # Check for API key on startup
    if not os.getenv("OPENROUTER_API_KEY"):
        print("ERROR: OPENROUTER_API_KEY environment variable not set", file=sys.stderr)
        print("Please set it before running the API server.", file=sys.stderr)
        sys.exit(1)
    
    # Get port from environment variable (Railway provides PORT)
    port = int(os.getenv("PORT", 5000))
    # Disable debug mode in production (Railway sets RAILWAY_ENVIRONMENT)
    debug = os.getenv("RAILWAY_ENVIRONMENT") is None
    
    print("=" * 60)
    print("TransBack API Server")
    print("=" * 60)
    print(f"Server starting on http://0.0.0.0:{port}")
    print(f"API endpoint: POST http://0.0.0.0:{port}/translate")
    print(f"Web UI: http://0.0.0.0:{port}/")
    print("=" * 60)
    
    app.run(debug=debug, host='0.0.0.0', port=port)

