"""
Gemini AI Service for Image Generation
"""
import os
import google.generativeai as genai
import requests
import base64
from io import BytesIO
from PIL import Image
from typing import Optional, Dict, Any
import time


class GeminiService:
    """Service for interacting with Google Gemini API for image generation and vision"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        
        # Imagen 3 API endpoint
        self.imagen_url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict"
    
    def generate_storyboard_from_project(self, title: str, genre: str, logline: str, synopsis: str) -> Optional[str]:
        """Generate storyboard image prompt directly from project information (intelligent mode)"""
        
        # Load prompt template from file
        import os
        prompt_file = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'direct_storyboard_generation.txt')
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            print("✅ Loaded direct storyboard generation prompt from file")
        except Exception as e:
            print(f"⚠️ Could not load prompt file: {e}, using fallback")
            # Fallback prompt
            prompt_template = """Create a cinematic opening shot for:

Title: {title}
Genre: {genre}
Logline: {logline}
Synopsis: {synopsis}

Generate a detailed visual prompt for image generation that captures the story's essence."""
        
        # Fill in template variables
        prompt = prompt_template.format(
            title=title,
            genre=genre or 'cinematic film',
            logline=logline or 'Not provided',
            synopsis=synopsis or 'Not provided'
        )
        
        print("\n" + "="*80)
        print("🎬 INTELLIGENT STORYBOARD GENERATION (Direct from Project)")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")
        
        try:
            print(f"🧠 Calling Gemini Pro with intelligent project analysis...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                print("\n" + "="*80)
                print("✅ GEMINI GENERATED IMAGE PROMPT (Intelligent Mode)")
                print("="*80)
                print(response.text)
                print("="*80 + "\n")
                return response.text
            else:
                print(f"❌ Gemini API returned empty response")
                return None
                
        except Exception as e:
            print(f"❌ Gemini error generating prompt: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_storyboard_prompt(self, scene_description: str, style: str = "cinematic") -> Optional[str]:
        """Generate optimized image generation prompt from scene description"""
        
        # Load prompt template from file
        import os
        prompt_file = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'storyboard_prompt_generation.txt')
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            print("✅ Loaded storyboard prompt template from file")
        except Exception as e:
            print(f"⚠️ Could not load prompt file: {e}, using fallback")
            # Fallback prompt
            prompt_template = """Convert this scene description into a detailed visual prompt for image generation.

Scene: {scene_description}
Style: {style}

Generate a single, detailed prompt suitable for image generation AI."""
        
        # Fill in template variables
        prompt = prompt_template.format(
            scene_description=scene_description,
            style=style
        )
        
        print("\n" + "="*80)
        print("🎨 FULL STORYBOARD PROMPT GENERATION REQUEST")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")
        
        try:
            print(f"📞 Calling Gemini Pro to generate storyboard prompt...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                print("\n" + "="*80)
                print("✅ GEMINI GENERATED STORYBOARD PROMPT")
                print("="*80)
                print(response.text)
                print("="*80 + "\n")
                return response.text
            else:
                print(f"❌ Gemini API returned empty response")
                return None
                
        except Exception as e:
            print(f"❌ Gemini error generating prompt: {e}")
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
    
    def generate_image(self, prompt: str, negative_prompt: str = "", retries: int = 3) -> Optional[str]:
        """
        Generate image using Google Imagen 3
        Returns base64 encoded image or None if failed
        """
        # Build the request payload for Imagen
        payload = {
            "instances": [
                {
                    "prompt": prompt
                }
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "16:9",
                "safetyFilterLevel": "block_some",
                "personGeneration": "allow_adult"
            }
        }
        
        if negative_prompt:
            payload["parameters"]["negativePrompt"] = negative_prompt
        
        headers = {
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            try:
                print(f"🎨 Generating image with Gemini Imagen 3 (attempt {attempt + 1}/{retries})...")
                print(f"   📝 IMAGE PROMPT:")
                print(f"   {prompt}")
                print(f"   ---")
                if negative_prompt:
                    print(f"   🚫 Negative prompt: {negative_prompt}")
                
                print(f"   📤 Sending request to Imagen API...")
                response = requests.post(
                    self.imagen_url,
                    params={"key": self.api_key},
                    headers=headers,
                    json=payload,
                    timeout=120
                )
                
                print(f"   📥 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract image data from response
                    if "predictions" in result and len(result["predictions"]) > 0:
                        prediction = result["predictions"][0]
                        
                        # Imagen returns base64 encoded images
                        if "bytesBase64Encoded" in prediction:
                            base64_image = prediction["bytesBase64Encoded"]
                            
                            # Verify it's a valid image
                            try:
                                image_bytes = base64.b64decode(base64_image)
                                img = Image.open(BytesIO(image_bytes))
                                img.verify()
                                
                                # Reopen and convert to RGB if needed
                                img = Image.open(BytesIO(image_bytes))
                                if img.mode != 'RGB':
                                    img = img.convert('RGB')
                                
                                # Convert to PNG for consistency
                                buffer = BytesIO()
                                img.save(buffer, format='PNG', quality=95)
                                buffer.seek(0)
                                
                                base64_png = base64.b64encode(buffer.getvalue()).decode('utf-8')
                                print(f"✅ Image generated successfully with Gemini Imagen 3!")
                                
                                return f"data:image/png;base64,{base64_png}"
                            
                            except Exception as img_error:
                                print(f"❌ Invalid image received: {img_error}")
                                if attempt < retries - 1:
                                    time.sleep(5)
                                    continue
                    
                    print(f"❌ No image data in response: {result}")
                    if attempt < retries - 1:
                        time.sleep(5)
                        continue
                
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                    print(f"❌ Image generation failed: {response.status_code}")
                    print(f"   Error: {error_data}")
                    
                    if attempt < retries - 1:
                        print(f"   Retrying in 10 seconds...")
                        time.sleep(10)
                        continue
                
            except requests.exceptions.Timeout:
                print(f"⏱️ Request timeout (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(10)
                    continue
            
            except Exception as e:
                print(f"❌ Error generating image: {e}")
                import traceback
                traceback.print_exc()
                if attempt < retries - 1:
                    time.sleep(10)
                    continue
        
        print(f"❌ Failed to generate image after {retries} attempts")
        return None
