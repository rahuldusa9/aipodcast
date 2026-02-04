"""
Test Google Gemini API Integration
Verify that your API key is working correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("🤖 Testing Google Gemini API Integration")
print("=" * 60)
print()

# Check if API key is configured
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ GEMINI_API_KEY not found")
    print()
    print("Setup Instructions:")
    print("1. Get free API key: https://makersuite.google.com/app/apikey")
    print("2. Copy .env.example to .env")
    print("3. Add your key: GEMINI_API_KEY=your_key_here")
    print("4. Run this test again")
    print()
    print("ℹ️  The system will still work using template generation")
    exit(0)

print(f"✓ API key found: {api_key[:20]}...")
print()

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    print("✓ google-generativeai package installed")
except ImportError:
    print("❌ google-generativeai not installed")
    print("   Run: pip install -r requirements.txt")
    exit(1)

print()
print("Testing API connection...")

try:
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Test with a simple prompt
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello in 5 words")
    
    result_text = response.text.strip()
    
    print("✓ API connection successful!")
    print()
    print(f"Test response: '{result_text}'")
    print()
    print("=" * 60)
    print("✅ Gemini API is working correctly!")
    print("=" * 60)
    print()
    print("You can now generate AI-powered podcast scripts.")
    print("Try: python app.py")
    
except Exception as e:
    print(f"❌ API test failed: {str(e)}")
    print()
    print("Common issues:")
    print("- Invalid API key")
    print("- API key not activated")
    print("- Network/firewall blocking requests")
    print()
    print("Get a new key: https://makersuite.google.com/app/apikey")
    exit(1)
