# ======= Updated app.py (Always RAG-based, no memory) =======
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from rag_helper import fetch_top_k_chunks

# Load API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


def build_prompt_with_rag(user_question, context_memory):
    context = context_memory or "[No product context available]"

    prompt = (
        "You are a helpful assistant. Use the product context below to answer the user's question naturally.\n\n"
        f"=== Product Context ===\n{context}\n\n"
        f"=== User Question ===\n{user_question}\n\n"
        "If a relevant product is found, respond with its details and end with:\nProduct: [exact title]\n"
        "If nothing relevant is found, say so and end with:\nProduct: NOT FOUND\n"
    )
    return prompt


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_question = data.get("message", "")

        if not user_question:
            return jsonify({"error": "No message provided"}), 400

        top_chunks = fetch_top_k_chunks(user_question, k=3)
        top_chunk = top_chunks[0] if top_chunks else None
        context_memory = top_chunk['chunk_text'] if top_chunk else ""

        prompt = build_prompt_with_rag(user_question, context_memory)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.choices[0].message.content.strip()

        # Extract product name from last line
        product_line = next(
            (line for line in answer.splitlines() if line.startswith("Product: ")),
            "Product: NOT FOUND"
        )
        product_name = product_line.replace("Product: ", "").strip()

        return jsonify({
            "response": answer,
            "product_name": product_name,
            "product_context": context_memory
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # default to 8080
    app.run(host="0.0.0.0", port=port)