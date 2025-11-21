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
        """Generate a complete screenplay from synopsis"""
        prompt = f"""Please generate a complete movie script based on the following information:

Title: {title}
Genre: {genre}
Logline: {logline}

Synopsis:
{synopsis}

Generate a professional screenplay with:
1. Properly formatted scene headings (INT./EXT., LOCATION, TIME)
2. Detailed scene descriptions and visual storytelling
3. Character dialogue with proper formatting
4. Scene transitions
5. At least 5-8 key scenes that tell the complete story

Provide the response in JSON format with:
- synopsis: A brief 2-3 sentence summary
- characters: Array of character objects with 'name' and 'description'
- scenes: Array of scene objects with 'heading', 'description', 'dialogue' (array), 'action'
- themes: Array of main themes
- tone: Overall tone of the script
- pacing: Description of the pacing"""
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a professional screenwriter with expertise in crafting compelling movie scripts. Generate detailed, well-structured screenplays with proper formatting and visual storytelling."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 8000
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
                print(f"Error parsing Groq screenplay response: {e}")
                print(f"Raw content: {content}")
        
        return None
    
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
