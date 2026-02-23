"""
List all available Gemini models to find the correct image generation model
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=api_key)

print("\n" + "="*80)
print("📋 AVAILABLE GEMINI MODELS")
print("="*80 + "\n")

try:
    for model in genai.list_models():
        print(f"Model: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print(f"  Supported methods: {model.supported_generation_methods}")
        print()
except Exception as e:
    print(f"❌ Error listing models: {e}")
