import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY is not set.")
    exit(1)

genai.configure(api_key=api_key)

print("Checking available models for your API key...")
try:
    models = list(genai.list_models())
    generate_models = [m.name for m in models if "generateContent" in getattr(m, "supported_generation_methods", [])]
    print(f"Total models available: {len(models)}")
    print("Models supporting generateContent:")
    for m in generate_models:
        print(f" - {m}")
except Exception as e:
    print(f"Error accessing Gemini API: {e}")
