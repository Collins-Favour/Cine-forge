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
    
    def generate_screenplay(self, title: str, synopsis: str, genre: str = 'Drama', 
                           logline: str = '', script_length: str = 'feature') -> Optional[Dict]:
        """Generate a complete screenplay from synopsis with advanced formatting
        
        Args:
            title: Film title
            synopsis: Story synopsis
            genre: Genre (Drama, Action, Thriller, Horror, Comedy, Romance, Sci-Fi, etc.)
            logline: One-line premise
            script_length: 'short' (5-8 scenes), 'medium' (10-12 scenes), 'feature' (12-18 scenes)
        """
        
        # Load prompt template from file
        import os
        prompt_file = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'script_generation.txt')
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            print("✅ Loaded enhanced script generation prompt from file")
        except Exception as e:
            print(f"⚠️ Could not load prompt file: {e}, using fallback")
            prompt_template = """Generate a professional {genre} screenplay for "{title}"
Synopsis: {synopsis}
Logline: {logline}

Return JSON with: title, genre, logline, synopsis, themes, tone, pacing, characters (with name, role, description, motivation, arc), scenes (with scene_number, act, heading, story_beat, description, dialogue, mood, lighting, camera_notes, sound_design, transition)."""
        
        # Fill in template variables
        prompt = prompt_template.format(
            title=title,
            genre=genre.capitalize(),
            logline=logline or 'Not provided',
            synopsis=synopsis
        )
        
        print("\n" + "="*80)
        print(f"📝 GENERATING {script_length.upper()} {genre.upper()} SCREENPLAY")
        print("="*80)
        print(f"Title: {title}")
        print(f"Genre: {genre}")
        print(f"Length: {script_length}")
        print(f"Synopsis length: {len(synopsis)} chars")
        print("="*80 + "\n")
        
        # Genre-specific temperature and parameters
        genre_params = self._get_genre_parameters(genre)
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system", 
                    "content": f"You are an award-winning {genre} screenwriter. Generate industry-standard, detailed screenplays with three-act structure, character development, and cinematic visual storytelling. Always return valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": genre_params['temperature'],
            "max_tokens": 16000,  # Increased for longer, detailed scripts
            "top_p": genre_params['top_p']
        }
        
        print(f"🚀 Sending request to Groq API (Llama 3.3 70B Versatile)")
        print(f"   Temperature: {genre_params['temperature']}, Top-P: {genre_params['top_p']}")
        
        result = self._make_request("chat/completions", payload)
        
        if result and 'choices' in result:
            try:
                content = result['choices'][0]['message']['content']
                print(f"📄 Groq response received ({len(content)} chars)")
                
                # Multiple JSON extraction strategies
                parsed = self._extract_and_parse_json(content)
                
                if parsed and parsed.get('scenes'):
                    scene_count = len(parsed['scenes'])
                    char_count = len(parsed.get('characters', []))
                    print(f"✅ Successfully parsed screenplay:")
                    print(f"   - {scene_count} scenes")
                    print(f"   - {char_count} characters")
                    print(f"   - {len(parsed.get('themes', []))} themes")
                    
                    # Validate and enhance the structure
                    return self._validate_and_enhance_screenplay(parsed, title, genre, synopsis)
                else:
                    print(f"❌ No valid scenes in parsed response")
                    return self._create_fallback_structure(title, genre, synopsis, content)
                    
            except Exception as e:
                print(f"❌ Error processing Groq screenplay response: {e}")
                import traceback
                traceback.print_exc()
                return self._create_fallback_structure(title, genre, synopsis, None)
        
        print(f"❌ No valid result from Groq API")
        return self._create_fallback_structure(title, genre, synopsis, None)
    
    def _get_genre_parameters(self, genre: str) -> Dict[str, float]:
        """Get genre-specific generation parameters"""
        genre_lower = genre.lower()
        
        # Genre-specific creativity vs. structure balance
        params = {
            'action': {'temperature': 0.85, 'top_p': 0.92},
            'thriller': {'temperature': 0.82, 'top_p': 0.90},
            'horror': {'temperature': 0.88, 'top_p': 0.93},
            'comedy': {'temperature': 0.90, 'top_p': 0.95},
            'drama': {'temperature': 0.78, 'top_p': 0.88},
            'romance': {'temperature': 0.80, 'top_p': 0.90},
            'sci-fi': {'temperature': 0.87, 'top_p': 0.94},
            'fantasy': {'temperature': 0.88, 'top_p': 0.94},
            'mystery': {'temperature': 0.80, 'top_p': 0.89},
            'crime': {'temperature': 0.81, 'top_p': 0.89}
        }
        
        return params.get(genre_lower, {'temperature': 0.82, 'top_p': 0.90})
    
    def _extract_and_parse_json(self, content: str) -> Optional[Dict]:
        """Extract and parse JSON with multiple strategies"""
        
        # Strategy 1: Find outermost JSON braces
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            try:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Strategy 2: Look for ```json code blocks
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            if end > start:
                try:
                    return json.loads(content[start:end].strip())
                except json.JSONDecodeError:
                    pass
        
        # Strategy 3: Try the entire content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _validate_and_enhance_screenplay(self, screenplay: Dict, title: str, 
                                        genre: str, synopsis: str) -> Dict:
        """Validate and enhance screenplay structure"""
        
        # Ensure required fields exist
        screenplay.setdefault('title', title)
        screenplay.setdefault('genre', genre)
        screenplay.setdefault('synopsis', synopsis[:300])
        screenplay.setdefault('themes', [genre, 'Character Development', 'Conflict'])
        screenplay.setdefault('tone', f'{genre} with emotional depth')
        screenplay.setdefault('pacing', 'Balanced')
        screenplay.setdefault('characters', [])
        
        # Enhance scenes
        if screenplay.get('scenes'):
            for i, scene in enumerate(screenplay['scenes'], 1):
                scene.setdefault('scene_number', i)
                scene.setdefault('act', self._determine_act(i, len(screenplay['scenes'])))
                scene.setdefault('mood', 'Dramatic')
                scene.setdefault('lighting', 'Natural lighting')
                scene.setdefault('camera_notes', 'Medium shot')
                scene.setdefault('sound_design', 'Ambient sound')
                scene.setdefault('transition', 'CUT TO:')
                scene.setdefault('dialogue', [])
        
        return screenplay
    
    def _determine_act(self, scene_number: int, total_scenes: int) -> int:
        """Determine which act a scene belongs to (three-act structure)"""
        act1_end = int(total_scenes * 0.25)
        act2_end = int(total_scenes * 0.75)
        
        if scene_number <= act1_end:
            return 1
        elif scene_number <= act2_end:
            return 2
        else:
            return 3
    
    def _create_fallback_structure(self, title: str, genre: str, 
                                   synopsis: str, content: Optional[str]) -> Dict:
        """Create fallback screenplay structure when generation fails"""
        
        return {
            'title': title,
            'genre': genre,
            'synopsis': synopsis[:300],
            'themes': [genre, 'Conflict', 'Resolution'],
            'tone': f'{genre} atmosphere',
            'pacing': 'Medium',
            'characters': [
                {
                    'name': 'PROTAGONIST',
                    'role': 'protagonist',
                    'description': 'Main character to be developed',
                    'motivation': 'To be determined',
                    'arc': 'Growth through adversity'
                }
            ],
            'scenes': [
                {
                    'scene_number': 1,
                    'act': 1,
                    'heading': 'INT. LOCATION - DAY',
                    'story_beat': 'Opening',
                    'description': content[:500] if content else synopsis[:300],
                    'dialogue': [],
                    'action': 'Scene establishes the world and characters.',
                    'mood': 'Establishing',
                    'lighting': 'Natural lighting',
                    'camera_notes': 'Wide establishing shot',
                    'sound_design': 'Ambient atmosphere',
                    'transition': 'CUT TO:'
                }
            ]
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
