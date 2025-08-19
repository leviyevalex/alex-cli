#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# --- Load API key ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def send_to_gemini(prompt: str, pdf_path: Path):
    """
    Send prompt + optional PDF to Gemini LLM.
    """
    model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
    content = [prompt]

    if pdf_path:
        pdf_bytes = pdf_path.read_bytes()
        content.append({
            "data": pdf_bytes,
            "mime_type": "application/pdf"
        })

    response = model.generate_content(content)
    return response.text.strip()

def main():
    parser = argparse.ArgumentParser(
        description="Send PDF + prompt (with optional context.txt) to Gemini LLM"
    )
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    parser.add_argument("prompt", type=str, help="Prompt/query for the LLM")
    parser.add_argument("-c", "--context", action="store_true",
                        help="Use context.txt if available")

    args = parser.parse_args()
    pdf_path = Path(args.pdf_path)

    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        print("Error: Please provide a valid PDF file.")
        sys.exit(1)

    final_prompt = args.prompt
    if args.context:
        context_file = Path("context.txt")
        if context_file.exists():
            context = context_file.read_text()
            final_prompt = f"{context}\n\n{args.prompt}"
        else:
            print("Warning: context.txt not found, proceeding without it.")

    print(f"[1/1] Sending PDF to Gemini with prompt...")
    response = send_to_gemini(final_prompt, pdf_path)

    # Save response
    output_path = pdf_path.with_name(pdf_path.stem + "_output.txt")
    with open(output_path, "w") as f:
        f.write(response)

    print(f"✅ Response saved to: '{output_path}'")
    print("\n===== MODEL RESPONSE =====")
    print(response)
    print("==========================")

if __name__ == "__main__":
    main()