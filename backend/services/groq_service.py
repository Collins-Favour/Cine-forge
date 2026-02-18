"""
AI Service for Groq API Integration
"""
import os
import requests
from typing import Dict, Any, Optional
import json


class GroqService:
    """Service for interacting with Groq API for script analysis and NLP"""
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = os.getenv('model', 'GPT-4')
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict]:
        """Make API request to Groq"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Groq API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Error response text: {e.response.text}")
            return None
    
    def analyze_script(self, script_content: str) -> Optional[Dict]:
        """Analyze script and extract structure, characters, themes"""
        prompt = f"""Analyze the following script and provide:
1. Overall synopsis (2-3 sentences)
2. Main characters with descriptions
3. Scene breakdown with locations and time of day
4. Narrative themes and tone
5. Pacing analysis

Script:
{script_content}

Provide the response in JSON format with keys: synopsis, characters (array), scenes (array), themes (array), tone, pacing."""
        
        payload = {
            "model": "llama-3.3-70b-versatile",  # Updated to supported model
            "messages": [
                {"role": "system", "content": "You are a professional script analyst for film production."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        result = self._make_request("chat/completions", payload)
        
        if result and 'choices' in result:
            try:
                content = result['choices'][0]['message']['content']
                # Extract JSON from response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    return json.loads(content[json_start:json_end])
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing Groq response: {e}")
        
        return None
    
    def generate_screenplay(self, title: str, synopsis: str, genre: str = 'Drama', logline: str = '') -> Optional[Dict]:
        """Generate a complete screenplay from synopsis with mood and lighting suggestions"""
        
        # Load prompt template from file
        import os
        prompt_file = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'script_generation.txt')
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            print("✅ Loaded script generation prompt from file")
        except Exception as e:
            print(f"⚠️ Could not load prompt file: {e}, using fallback")
            # Fallback prompt
            prompt_template = """Please generate a complete movie script based on the following information:

Title: {title}
Genre: {genre}
Logline: {logline}

Synopsis:
{synopsis}

Generate a professional screenplay with scenes, dialogue, mood, lighting, and camera notes in JSON format."""
        
        # Fill in template variables
        prompt = prompt_template.format(
            title=title,
            genre=genre,
            logline=logline or 'Not provided',
            synopsis=synopsis
        )
        
        print("\n" + "="*80)
        print("📝 FULL SCRIPT GENERATION PROMPT")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a professional screenwriter with expertise in crafting compelling movie scripts. Generate detailed, well-structured screenplays with proper formatting and visual storytelling."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 8000
        }
        
        print("🚀 Sending request to Groq API (Llama 3.3 70B)...")
        result = self._make_request("chat/completions", payload)
        
        if result and 'choices' in result:
            try:
                content = result['choices'][0]['message']['content']
                print(f"📄 Groq response received ({len(content)} chars)")
                
                # Extract JSON from response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    parsed = json.loads(json_str)
                    print(f"✅ Successfully parsed JSON with {len(parsed.get('scenes', []))} scenes")
                    return parsed
                else:
                    print(f"❌ No valid JSON found in response")
                    print(f"Response preview: {content[:500]}")
                    
                    # Try to create a basic structure from the response
                    return {
                        'synopsis': synopsis[:200],
                        'scenes': [{
                            'heading': 'INT. LOCATION - DAY',
                            'description': content[:500] if content else synopsis[:200],
                            'dialogue': [],
                            'action': 'Scene in progress...',
                            'mood': 'Dramatic',
                            'lighting': 'Natural lighting',
                            'camera_notes': 'Standard framing'
                        }],
                        'characters': [],
                        'themes': [genre],
                        'tone': genre,
                        'pacing': 'Medium'
                    }
                    
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"❌ Error parsing Groq screenplay response: {e}")
                print(f"Raw content preview: {content[:500] if 'content' in locals() else 'No content'}")
                
                # Return a minimal valid structure instead of None
                return {
                    'synopsis': synopsis[:200],
                    'scenes': [{
                        'heading': 'INT. LOCATION - DAY',
                        'description': synopsis[:200],
                        'dialogue': [],
                        'action': 'Scene description unavailable. Please regenerate.',
                        'mood': 'Neutral',
                        'lighting': 'Standard lighting',
                        'camera_notes': 'Medium shot'
                    }],
                    'characters': [],
                    'themes': [genre],
                    'tone': genre,
                    'pacing': 'Medium'
                }
        
        print(f"❌ No valid result from Groq API")
        # Return minimal structure instead of None to prevent complete failure
        return {
            'synopsis': synopsis[:200],
            'scenes': [{
                'heading': 'INT. LOCATION - DAY',
                'description': synopsis[:200],
                'dialogue': [],
                'action': 'Script generation failed. Please try again.',
                'mood': 'Neutral',
                'lighting': 'Standard lighting',
                'camera_notes': 'Medium shot'
            }],
            'characters': [],
            'themes': [genre],
            'tone': genre,
            'pacing': 'Medium'
        }
    
    def generate_scene_description(self, scene_text: str) -> Optional[str]:
        """Generate detailed scene description"""
        prompt = f"""Analyze this scene and provide:
- Visual description (what we see)
- Mood and atmosphere
- Suggested lighting
- Camera angles and movement suggestions
- Key dramatic beats

Scene:
{scene_text}"""
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a cinematographer and film director."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        result = self._make_request("chat/completions", payload)
        
        if result and 'choices' in result:
            return result['choices'][0]['message']['content']
        
        return None
    
    def suggest_locations(self, scene_description: str) -> Optional[Dict]:
        """Suggest filming locations based on scene"""
        prompt = f"""Based on this scene description, suggest:
1. Ideal location types
2. Specific location suggestions
3. Alternative locations
4. Location scouting tips

Scene: {scene_description}

Provide response in JSON format."""
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a location scout for film productions."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        
        result = self._make_request("chat/completions", payload)
        
        if result and 'choices' in result:
            try:
                content = result['choices'][0]['message']['content']
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    return json.loads(content[json_start:json_end])
            except json.JSONDecodeError:
                pass
        
        return None
