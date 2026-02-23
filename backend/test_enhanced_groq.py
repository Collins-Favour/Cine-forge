"""
Test Enhanced Groq Script Generation
Verifies all improvements to the screenplay generation system
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.groq_service import GroqService
import json


def test_screenplay_generation():
    """Test the enhanced screenplay generation"""
    print("\n" + "="*80)
    print("TESTING ENHANCED GROQ SCREENPLAY GENERATION")
    print("="*80 + "\n")
    
    # Initialize service
    try:
        groq_service = GroqService()
        print("✅ GroqService initialized successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize GroqService: {e}")
        return
    
    # Test cases for different genres
    test_cases = [
        {
            'title': 'The Last Horizon',
            'genre': 'Sci-Fi',
            'logline': 'A lone astronaut discovers a signal from beyond the edge of the known universe.',
            'synopsis': 'Commander Sarah Chen is on a routine deep space mission when her ship detects an impossible signal originating from beyond the observable universe. Against protocol, she decides to investigate, leading her on a journey that will challenge her understanding of reality, time, and human consciousness. As she ventures deeper into the unknown, she begins to question whether she\'s discovering something new or remembering something ancient.'
        },
        {
            'title': 'Midnight Confession',
            'genre': 'Thriller',
            'logline': 'A priest must decide whether to break his vow of confession to stop a serial killer.',
            'synopsis': 'Father Michael receives a chilling confession from someone claiming to be the notorious "Midnight Killer" terrorizing the city. Bound by his sacred vows, he cannot reveal what he knows to the police. But as more victims fall and the killer begins targeting people close to him, Michael must navigate the conflict between his faith, his conscience, and his desire to save innocent lives.'
        }
    ]
    
    # Test first case
    test = test_cases[0]  # Test Sci-Fi first
    
    print(f"📝 Test Case: {test['title']}")
    print(f"   Genre: {test['genre']}")
    print(f"   Logline: {test['logline'][:60]}...")
    print()
    
    try:
        result = groq_service.generate_screenplay(
            title=test['title'],
            synopsis=test['synopsis'],
            genre=test['genre'],
            logline=test['logline'],
            script_length='feature'
        )
        
        if result:
            print("\n" + "="*80)
            print("GENERATION RESULTS")
            print("="*80)
            print(f"✅ Screenplay generated successfully!")
            print()
            print(f"Title: {result.get('title')}")
            print(f"Genre: {result.get('genre')}")
            print(f"Tone: {result.get('tone')}")
            print(f"Pacing: {result.get('pacing')}")
            print()
            
            # Characters
            if result.get('characters'):
                print(f"📋 CHARACTERS ({len(result['characters'])})")
                for char in result['characters']:
                    print(f"   • {char.get('name')} - {char.get('role')}")
                    if char.get('motivation'):
                        print(f"     Motivation: {char['motivation'][:60]}...")
                print()
            
            # Scenes
            if result.get('scenes'):
                print(f"🎬 SCENES ({len(result['scenes'])})")
                
                # Group by act
                act1 = [s for s in result['scenes'] if s.get('act') == 1]
                act2 = [s for s in result['scenes'] if s.get('act') == 2]
                act3 = [s for s in result['scenes'] if s.get('act') == 3]
                
                print(f"   Act I (Setup): {len(act1)} scenes")
                print(f"   Act II (Confrontation): {len(act2)} scenes")
                print(f"   Act III (Resolution): {len(act3)} scenes")
                print()
                
                # Show first 3 scenes in detail
                print("📄 FIRST 3 SCENES:")
                for i, scene in enumerate(result['scenes'][:3], 1):
                    print(f"\n   Scene {scene.get('scene_number', i)}: {scene.get('heading')}")
                    if scene.get('story_beat'):
                        print(f"   Story Beat: {scene['story_beat']}")
                    print(f"   Mood: {scene.get('mood')}")
                    print(f"   Lighting: {scene.get('lighting', 'N/A')[:60]}...")
                    print(f"   Camera: {scene.get('camera_notes', 'N/A')[:60]}...")
                    if scene.get('sound_design'):
                        print(f"   Sound: {scene['sound_design'][:60]}...")
                    if scene.get('dialogue'):
                        print(f"   Dialogue lines: {len(scene['dialogue'])}")
                print()
            
            # Themes
            if result.get('themes'):
                print(f"🎭 THEMES: {', '.join(result['themes'])}")
                print()
            
            # Save full result to file for inspection
            output_file = 'test_screenplay_output.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Full screenplay saved to: {output_file}")
            print()
            
            # Validation checks
            print("="*80)
            print("VALIDATION CHECKS")
            print("="*80)
            
            checks = {
                'Has title': bool(result.get('title')),
                'Has genre': bool(result.get('genre')),
                'Has synopsis': bool(result.get('synopsis')),
                'Has characters (3+)': len(result.get('characters', [])) >= 3,
                'Has scenes (12+)': len(result.get('scenes', [])) >= 12,
                'Has themes': bool(result.get('themes')),
                'Scenes have act numbers': all(s.get('act') for s in result.get('scenes', [])),
                'Scenes have mood': all(s.get('mood') for s in result.get('scenes', [])),
                'Scenes have lighting': all(s.get('lighting') for s in result.get('scenes', [])),
                'Scenes have camera notes': all(s.get('camera_notes') for s in result.get('scenes', [])),
                'Characters have descriptions': all(c.get('description') for c in result.get('characters', [])),
                'Characters have motivations': all(c.get('motivation') for c in result.get('characters', [])),
                'Characters have arcs': all(c.get('arc') for c in result.get('characters', []))
            }
            
            passed = sum(checks.values())
            total = len(checks)
            
            for check, status in checks.items():
                symbol = "✅" if status else "❌"
                print(f"{symbol} {check}")
            
            print()
            print(f"Score: {passed}/{total} checks passed ({int(passed/total*100)}%)")
            print()
            
            if passed == total:
                print("🎉 ALL CHECKS PASSED! Enhanced generation working perfectly!")
            elif passed >= total * 0.8:
                print("✅ MOSTLY WORKING - Minor improvements needed")
            else:
                print("⚠️ NEEDS ATTENTION - Several issues found")
            
        else:
            print("❌ Generation returned None")
            
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_screenplay_generation()
