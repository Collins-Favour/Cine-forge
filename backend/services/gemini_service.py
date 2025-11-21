"""
Gemini AI Service for Image Generation
"""
import os
import google.generativeai as genai
from typing import Optional, Dict, Any


class GeminiService:
    """Service for interacting with Google Gemini API for image generation and vision"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
    
    def generate_storyboard_prompt(self, scene_description: str, style: str = "cinematic") -> Optional[str]:
        """Generate optimized image generation prompt from scene description"""
        prompt = f"""Convert this scene description into a detailed visual prompt for image generation.
Include:
- Camera angle and framing
- Lighting conditions
- Color palette
- Mood and atmosphere
- Specific visual elements
- Art style: {style}

Scene: {scene_description}

Generate a single, detailed prompt suitable for image generation AI."""
        
        try:
            print(f"Calling Gemini API for scene: {scene_description[:50]}...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                print(f"Gemini API returned prompt: {response.text[:100]}...")
                return response.text
            else:
                print(f"Gemini API returned empty response")
                return None
                
        except Exception as e:
            print(f"Gemini error generating prompt: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def enhance_prompt_for_consistency(self, base_prompt: str, project_style: Dict[str, Any]) -> str:
        """Enhance prompt with project-specific style for visual consistency"""
        style_keywords = project_style.get('mood_keywords', [])
        color_palette = project_style.get('color_palette', [])
        
        enhancements = []
        
        if style_keywords:
            enhancements.append(f"Style: {', '.join(style_keywords)}")
        
        if color_palette:
            enhancements.append(f"Color palette: {', '.join(color_palette)}")
        
        if enhancements:
            return f"{base_prompt}. {'. '.join(enhancements)}"
        
        return base_prompt
    
    def analyze_scene_for_mood(self, scene_text: str) -> Optional[Dict]:
        """Analyze scene and suggest mood, lighting, and atmosphere"""
        prompt = f"""Analyze this film scene and provide:
1. Overall mood (one word)
2. Emotional tone
3. Lighting suggestions (time of day, natural/artificial, quality)
4. Color temperature (warm/cool/neutral)
5. Atmosphere description

Scene: {scene_text}

Provide response in structured format."""
        
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                # Parse response (simplified)
                return {
                    'analysis': response.text,
                    'status': 'success'
                }
        except Exception as e:
            print(f"Gemini error analyzing mood: {e}")
        
        return None
    
    def generate_character_description(self, character_name: str, context: str) -> Optional[str]:
        """Generate detailed character visual description"""
        prompt = f"""Create a detailed visual description of the character "{character_name}" for a storyboard artist.
Include:
- Physical appearance (age, build, height, distinctive features)
- Clothing and style
- Demeanor and body language
- How they should be portrayed visually

Context: {context}"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text if response else None
        except Exception as e:
            print(f"Gemini error generating character: {e}")
            return None
