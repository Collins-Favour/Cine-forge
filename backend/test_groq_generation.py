"""
Test script for Groq screenplay generation
"""
import os
from dotenv import load_dotenv
from services.groq_service import GroqService

# Load environment variables
load_dotenv()

def test_groq_api():
    """Test if Groq API key is configured and working"""
    
    # Check if API key exists
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Please add GROQ_API_KEY to your .env file")
        return False
    
    print(f"✅ GROQ_API_KEY found: {api_key[:10]}...")
    
    # Initialize service
    try:
        groq_service = GroqService()
        print("✅ GroqService initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize GroqService: {e}")
        return False
    
    # Test screenplay generation
    print("\n🎬 Testing screenplay generation...")
    print("-" * 50)
    
    test_title = "The Last Mission"
    test_synopsis = """A retired special forces operative must come out of retirement 
    when his former team is captured behind enemy lines. Racing against time, he assembles 
    a new team of specialists to execute a daring rescue mission in hostile territory."""
    
    print(f"Title: {test_title}")
    print(f"Synopsis: {test_synopsis[:100]}...")
    print("\n🤖 Calling Groq API...")
    
    try:
        result = groq_service.generate_screenplay(
            title=test_title,
            synopsis=test_synopsis,
            genre="Action",
            logline="One last mission to save his team"
        )
        
        if result:
            print("\n✅ SUCCESS! Screenplay generated")
            print(f"📊 Scenes: {len(result.get('scenes', []))}")
            print(f"👥 Characters: {len(result.get('characters', []))}")
            print(f"🎭 Themes: {result.get('themes', [])}")
            print(f"🎵 Tone: {result.get('tone', 'N/A')}")
            
            # Show first scene
            if result.get('scenes'):
                print("\n📝 First Scene Preview:")
                first_scene = result['scenes'][0]
                if isinstance(first_scene, dict):
                    print(f"Heading: {first_scene.get('heading', 'N/A')}")
                    print(f"Description: {first_scene.get('description', 'N/A')[:150]}...")
                else:
                    print(str(first_scene)[:200])
            
            return True
        else:
            print("❌ FAILED: No data returned from Groq API")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("🧪 Groq Screenplay Generation Test")
    print("=" * 50)
    
    success = test_groq_api()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed. Check the errors above.")
    print("=" * 50)
