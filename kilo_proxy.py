#!/usr/bin/env python3
"""
Kilo OpenAI-Compatible Proxy Server
Wraps 'kilo run' CLI to provide OpenAI-compatible API for PicoClaw

Usage:
    python3 kilo_proxy.py

Then configure PicoClaw:
    ~/.picoclaw/config.json:
    {
      "providers": {
        "openai": {
          "api_key": "dummy",
          "api_base": "http://127.0.0.1:8765/v1"
        }
      },
      "agents": {
        "defaults": {
          "model": "kilo/z-ai/glm-5:free"
        }
      }
    }
"""

from flask import Flask, request, jsonify, Response
import subprocess
import json
import uuid
import time
import sys

app = Flask(__name__)

AVAILABLE_MODELS = [
    "kilo/z-ai/glm-5:free",
    "kilo/arcee-ai/trinity-large-preview:free",
    "kilo/corethink:free",
    "kilo/minimax/minimax-m2.5:free",
    "kilo/stepfun/step-3.5-flash:free",
    "kilo/x-ai/grok-code-fast-1:optimized:free",
    "kilo/openrouter/free",
]


@app.route("/v1/models", methods=["GET"])
def list_models():
    return jsonify(
        {
            "object": "list",
            "data": [
                {"id": model, "object": "model", "owned_by": "kilo"}
                for model in AVAILABLE_MODELS
            ],
        }
    )


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    data = request.json
    messages = data.get("messages", [])
    model = data.get("model", "kilo/z-ai/glm-5:free")
    stream = data.get("stream", False)

    # Build context from messages
    context = ""
    for msg in messages[:-1]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        context += f"{role}: {content}\n"

    # Get last user message
    user_message = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            user_message = msg["content"]
            break

    # Prepend context if exists
    if context:
        user_message = f"Context:\n{context}\n\nCurrent message: {user_message}"

    print(f"[Kilo Proxy] Model: {model}", file=sys.stderr)
    print(f"[Kilo Proxy] Message: {user_message[:100]}...", file=sys.stderr)

    try:
        # Use full path to kilo and set working directory
        import os
        kilo_path = os.path.expanduser("~/.kilo/bin/kilo")
        if not os.path.exists(kilo_path):
            kilo_path = "kilo"  # Fallback to PATH
        
        # Use home directory as working directory
        work_dir = os.path.expanduser("~")
            
        result = subprocess.run(
            [kilo_path, "run", "-m", model, user_message, "--format", "json", "--auto"],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=180,
        )

        if result.returncode != 0:
            print(f"[Kilo Proxy] Error: {result.stderr}", file=sys.stderr)
            return jsonify({"error": result.stderr}), 500

        response_text = ""
        for line in result.stdout.strip().split("\n"):
            try:
                event = json.loads(line)
                if event.get("type") == "text":
                    response_text += event.get("part", {}).get("text", "")
            except json.JSONDecodeError:
                pass

        print(f"[Kilo Proxy] Response: {response_text[:100]}...", file=sys.stderr)

        if stream:

            def generate():
                chunk_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
                yield f"data: {json.dumps({'id': chunk_id, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': model, 'choices': [{'index': 0, 'delta': {'role': 'assistant', 'content': ''}, 'finish_reason': None}]})}\n\n"

                for char in response_text:
                    yield f"data: {json.dumps({'id': chunk_id, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': model, 'choices': [{'index': 0, 'delta': {'content': char}, 'finish_reason': None}]})}\n\n"

                yield f"data: {json.dumps({'id': chunk_id, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': model, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
                yield "data: [DONE]\n\n"

            return Response(generate(), mimetype="text/event-stream")

        return jsonify(
            {
                "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": response_text},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
            }
        )

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Request timeout"}), 504
    except Exception as e:
        print(f"[Kilo Proxy] Exception: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("=" * 50, file=sys.stderr)
    print("Kilo OpenAI-Compatible Proxy Server", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print("Server: http://127.0.0.1:8765", file=sys.stderr)
    print("Models endpoint: http://127.0.0.1:8765/v1/models", file=sys.stderr)
    print("Chat endpoint: http://127.0.0.1:8765/v1/chat/completions", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    app.run(host="127.0.0.1", port=8765, debug=False)
