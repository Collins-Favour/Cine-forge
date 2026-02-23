"""
Test Storyboard and Mood Board Generation
Verifies image generation with updated AI APIs
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.gemini_service import GeminiService
import json


def test_single_image_generation():
    """Test generating a single storyboard image"""
    print("\n" + "="*80)
    print("TEST 1: SINGLE STORYBOARD IMAGE GENERATION")
    print("="*80 + "\n")
    
    try:
        gemini_service = GeminiService()
        print("✅ GeminiService initialized\n")
        
        # Test prompt
        prompt = "Cinematic sci-fi opening shot: A lone spaceship drifting through a vast nebula with purple and blue cosmic clouds, dramatic lighting from a distant star, wide establishing shot, photorealistic, highly detailed, 8k quality"
        
        print(f"📝 Test prompt: {prompt[:100]}...")
        print()
        
        result = gemini_service.generate_image(
            prompt=prompt,
            negative_prompt="blurry, low quality, text, watermark"
        )
        
        if result:
            print("\n" + "="*80)
            print("✅ IMAGE GENERATION SUCCESSFUL!")
            print("="*80)
            print(f"Image data type: {type(result)}")
            print(f"Data URL prefix: {result[:50]}...")
            print(f"Total length: {len(result)} characters")
            
            # Save to file for inspection
            if result.startswith('data:image'):
                # Extract base64 data
                base64_data = result.split(',')[1]
                
                import base64
                image_bytes = base64.b64decode(base64_data)
                
                output_file = 'test_storyboard_image.png'
                with open(output_file, 'wb') as f:
                    f.write(image_bytes)
                
                print(f"\n💾 Image saved to: {output_file}")
                print(f"   File size: {len(image_bytes)} bytes")
                
                return True
        else:
            print("\n❌ IMAGE GENERATION FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mood_board_generation():
    """Test generating a complete mood board"""
    print("\n" + "="*80)
    print("TEST 2: MOOD BOARD GENERATION")
    print("="*80 + "\n")
    
    try:
        gemini_service = GeminiService()
        
        # Test project
        title = "Neon Nights"
        genre = "Cyberpunk Thriller"
        logline = "In a neon-lit megacity controlled by corrupt corporations, a rogue hacker discovers a conspiracy that could destroy the last remnants of human freedom."
        
        print(f"Project: {title}")
        print(f"Genre: {genre}")
        print(f"Logline: {logline}")
        print()
        
        mood_board = gemini_service.generate_mood_board(
            project_title=title,
            genre=genre,
            logline=logline,
            num_images=3  # Start with fewer for testing
        )
        
        if mood_board:
            print("\n" + "="*80)
            print(f"✅ MOOD BOARD GENERATED: {len(mood_board)} images")
            print("="*80)
            
            for i, img_data in enumerate(mood_board, 1):
                print(f"\n📸 Image {i}:")
                print(f"   Category: {img_data['category']}")
                print(f"   Description: {img_data['description']}")
                print(f"   Prompt: {img_data['prompt'][:80]}...")
                print(f"   Has image: {'✅' if img_data['image_data'] else '❌'}")
                
                # Save individual images
                if img_data['image_data'] and img_data['image_data'].startswith('data:image'):
                    base64_data = img_data['image_data'].split(',')[1]
                    import base64
                    image_bytes = base64.b64decode(base64_data)
                    
                    filename = f"test_mood_board_{i}_{img_data['category'].replace(' ', '_').lower()}.png"
                    with open(filename, 'wb') as f:
                        f.write(image_bytes)
                    print(f"   💾 Saved to: {filename}")
            
            # Save mood board data
            mood_board_json = {
                'title': title,
                'genre': genre,
                'images': [
                    {
                        'category': img['category'],
                        'description': img['description'],
                        'prompt': img['prompt']
                    }
                    for img in mood_board
                ]
            }
            
            with open('test_mood_board_data.json', 'w') as f:
                json.dump(mood_board_json, f, indent=2)
            
            print(f"\n💾 Mood board data saved to: test_mood_board_data.json")
            print(f"\n{'='*80}")
            print(f"MOOD BOARD TEST COMPLETE")
            print(f"Success rate: {len(mood_board)}/3 images generated")
            print(f"{'='*80}")
            
            return len(mood_board) > 0
        else:
            print("\n❌ MOOD BOARD GENERATION FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_status():
    """Test which image generation APIs are available"""
    print("\n" + "="*80)
    print("TEST 3: API AVAILABILITY CHECK")
    print("="*80 + "\n")
    
    try:
        gemini_service = GeminiService()
        
        print("📋 Available Image Generation APIs:\n")
        
        for i, api in enumerate(gemini_service.api_endpoints, 1):
            status = "✅ Enabled" if api.get('enabled') else "❌ Disabled"
            print(f"{i}. {api['name']}")
            print(f"   Type: {api['type']}")
            print(f"   Priority: {api['priority']}")
            print(f"   Status: {status}")
            
            if api['type'] != 'free':
                has_key = bool(api.get('api_key'))
                print(f"   API Key: {'✅ Set' if has_key else '❌ Not set'}")
            print()
        
        print(f"Total APIs configured: {len(gemini_service.api_endpoints)}")
        enabled_count = sum(1 for api in gemini_service.api_endpoints if api.get('enabled'))
        print(f"Enabled APIs: {enabled_count}")
        
        return enabled_count > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all storyboard generation tests"""
    print("\n" + "="*80)
    print("🎬 STORYBOARD & MOOD BOARD GENERATION TEST SUITE")
    print("="*80)
    
    results = []
    
    # Test 1: API Status
    print("\n")
    result1 = test_api_status()
    results.append(("API Availability", result1))
    
    if not result1:
        print("\n⚠️ No image generation APIs available. Tests cannot proceed.")
        return
    
    # Test 2: Single Image
    print("\n")
    result2 = test_single_image_generation()
    results.append(("Single Image Generation", result2))
    
    # Test 3: Mood Board
    print("\n")
    result3 = test_mood_board_generation()
    results.append(("Mood Board Generation", result3))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        symbol = "✅" if result else "❌"
        print(f"{symbol} {test_name}")
    
    print()
    print(f"Overall: {passed}/{total} tests passed ({int(passed/total*100)}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Storyboard generation is working!")
    elif passed >= total * 0.5:
        print("\n✅ PARTIAL SUCCESS - Some features working")
    else:
        print("\n⚠️ NEEDS ATTENTION - Multiple failures detected")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    run_all_tests()
