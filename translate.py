# translate.py
import os, argparse, requests, sys, logging

API_URL = "https://openrouter.ai/api/v1/chat/completions"

def load_prompt(filename: str, **kwargs) -> str:
    """Load a prompt template from prompts/ directory and format it with kwargs."""
    prompt_path = os.path.join("prompts", filename)
    logging.debug(f"Loading prompt from {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read().strip()
    return template.format(**kwargs)

def translate(text: str, source: str, target: str, api_key: str,
              model: str, app_url: str|None=None, app_title: str|None=None) -> str:
    logging.info(f"Translating from {source} to {target} using model {model}")
    logging.debug(f"Text length: {len(text)} characters")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if app_url:
        headers["HTTP-Referer"] = app_url
    if app_title:
        headers["X-Title"] = app_title

    system_prompt = load_prompt("translate_system.txt", source=source, target=target)
    
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    }

    logging.debug(f"Sending translation request to {API_URL}")
    r = requests.post(API_URL, headers=headers, json=body, timeout=120)
    r.raise_for_status()
    result = r.json()["choices"][0]["message"]["content"]
    logging.info(f"Translation completed. Result length: {len(result)} characters")
    return result

def compare_meanings(original: str, back_translated: str, language: str, api_key: str,
                     model: str, app_url: str|None=None, app_title: str|None=None) -> str:
    logging.info(f"Comparing meanings in {language} using model {model}")
    logging.debug(f"Original length: {len(original)} characters, Back-translated length: {len(back_translated)} characters")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if app_url:
        headers["HTTP-Referer"] = app_url
    if app_title:
        headers["X-Title"] = app_title

    system_prompt = load_prompt("compare_system.txt", language=language)
    user_prompt = load_prompt("compare_user.txt", original=original, back_translated=back_translated)
    
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    logging.debug(f"Sending comparison request to {API_URL}")
    r = requests.post(API_URL, headers=headers, json=body, timeout=120)
    r.raise_for_status()
    result = r.json()["choices"][0]["message"]["content"]
    logging.info("Meaning comparison completed")
    return result

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logging.info("=" * 60)
    logging.info("TransBack Translation Tool - Starting")
    logging.info("=" * 60)
    
    p = argparse.ArgumentParser(description="File translator via OpenRouter/Qwen")
    p.add_argument("input_file")
    p.add_argument("output_file")
    p.add_argument("--source", default="en")
    p.add_argument("--target", default="af")
    p.add_argument("--model", default="qwen/qwen3-235b-a22b-2507")
    p.add_argument("--app-url", default=None)
    p.add_argument("--app-title", default=None)
    p.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = p.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug logging enabled")

    logging.info(f"Input file: {args.input_file}")
    logging.info(f"Output file: {args.output_file}")
    logging.info(f"Source language: {args.source}")
    logging.info(f"Target language: {args.target}")
    logging.info(f"Model: {args.model}")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logging.error("OPENROUTER_API_KEY environment variable not set")
        print("Set OPENROUTER_API_KEY env var.", file=sys.stderr)
        sys.exit(1)
    logging.debug("API key found")

    logging.info(f"Reading input file: {args.input_file}")
    with open(args.input_file, "r", encoding="utf-8") as f:
        src = f.read()
    logging.info(f"Input file read successfully. Length: {len(src)} characters")

    logging.info("-" * 60)
    logging.info("Step 1/3: Translating to target language")
    logging.info("-" * 60)
    out = translate(src, args.source, args.target, api_key,
                    args.model, args.app_url, args.app_title)

    logging.info(f"Writing translation to {args.output_file}")
    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(out)
    logging.info(f"Translation saved to {args.output_file}")

    logging.info("-" * 60)
    logging.info("Step 2/3: Back-translating to source language")
    logging.info("-" * 60)
    back = translate(out, args.target, args.source, api_key,
                     args.model, args.app_url, args.app_title)

    logging.info("Writing back-translation to back.txt")
    with open("back.txt", "w", encoding="utf-8") as f:
        f.write(back)
    logging.info("Back-translation saved to back.txt")

    logging.info("-" * 60)
    logging.info("Step 3/3: Comparing meanings")
    logging.info("-" * 60)
    review = compare_meanings(src, back, args.source, api_key,
                              args.model, args.app_url, args.app_title)

    logging.info("Writing comparison review to review.txt")
    with open("review.txt", "w", encoding="utf-8") as f:
        f.write(review)
    logging.info("Comparison review saved to review.txt")

    logging.info("=" * 60)
    logging.info("Translation process completed successfully!")
    logging.info("=" * 60)

if __name__ == "__main__":
    main()
