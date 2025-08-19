#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from cyclopts import App
import subprocess
import tempfile

# --- Load API key ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = App(name="pdf2gem")

# Hardcoded contexts
MARKDOWN_CONTEXT = """
You are an expert in converting handwritten notes into clean, well-structured Obsidian markdown.
- Use markdown headers (#, ##, ###) appropriately.
- Format equations with inline $...$ or block $$...$$.
- Use lists, bullet points, and code blocks when appropriate.
- Keep it concise and readable for study purposes.
"""

LATEX_CONTEXT = """
You are an expert in converting handwritten notes into clean, well-structured LaTeX.
- Use proper LaTeX math mode for equations.
- Use \\section, \\subsection, and \\subsubsection for structure.
- Use itemize/enumerate environments for lists.
- Output should be valid standalone LaTeX source.
"""

def send_to_gemini(prompt: str, pdf_path: Path):
    """
    Send prompt + PDF to Gemini LLM.
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


@app.default
def pdf2gemini(
    pdf_path: Path,
    prompt: str,
    md: bool = False,
    latex: bool = False,
):
    """
    Send PDF + prompt (with optional markdown/latex context) to Gemini LLM.
    """

    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        print("❌ Error: Please provide a valid PDF file.")
        sys.exit(1)

    # Apply context if requested
    final_prompt = prompt
    if md:
        final_prompt = f"{MARKDOWN_CONTEXT}\n\n{prompt}"
    elif latex:
        final_prompt = f"{LATEX_CONTEXT}\n\n{prompt}"

    print(f"[1/1] Sending PDF to Gemini with prompt...")
    response = send_to_gemini(final_prompt, pdf_path)

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as tmp:
        tmp.write(response)
        tmp.flush()
        subprocess.run(["vim", tmp.name])

    # Open the response in Vim temporarily
    # subprocess.run(["vim", "-"], input=response.encode("utf-8"))

    # # Save response
    # output_path = pdf_path.with_name(pdf_path.stem + "_output.txt")
    # with open(output_path, "w") as f:
    #     f.write(response)

    # print(f"✅ Response saved to: '{output_path}'")
    # print("\n===== MODEL RESPONSE =====")
    # print(response)
    # print("==========================")

if __name__ == "__main__":
    app()
