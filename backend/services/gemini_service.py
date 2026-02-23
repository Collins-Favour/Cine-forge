"""
Gemini AI Service for Image Generation
UPDATED: Uses multiple image generation APIs with fallback support
"""
import os
import google.generativeai as genai
import requests
import base64
from io import BytesIO
from PIL import Image
from typing import Optional, Dict, Any, List
import time
import json


class GeminiService:
    """Service for interacting with Google Gemini API for image generation and vision"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        # Text/analysis model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        # Image generation model - Nano Banana
        self.image_model = genai.GenerativeModel('gemini-2.5-flash-image')
        
        self.imagen_available = True
        self.api_endpoints = self._initialize_image_apis()
    
    def _initialize_image_apis(self) -> List[Dict[str, Any]]:
        """Initialize available image generation APIs with priority order"""
        apis = []
        
        # Gemini Nano Banana - Only image generation API
        apis.append({
            'name': 'Gemini Nano Banana',
            'type': 'gemini_imagen',
            'enabled': True,
            'priority': 1
        })
        
        return apis
    
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
        Generate image using multiple APIs with fallback support
        Returns base64 encoded image or None if all methods fail
        """
        print(f"\n{'='*80}")
        print(f"🎨 IMAGE GENERATION REQUEST")
        print(f"{'='*80}")
        print(f"📝 Prompt: {prompt[:200]}...")
        if negative_prompt:
            print(f"🚫 Negative: {negative_prompt}")
        print(f"{'='*80}\n")
        
        # Try each API in priority order
        for api in self.api_endpoints:
            if not api.get('enabled'):
                continue
            
            print(f"🔄 Trying {api['name']}...")
            
            try:
                if api['type'] == 'gemini_imagen':
                    result = self._generate_with_gemini_imagen(prompt, negative_prompt)
                else:
                    continue
                
                if result:
                    print(f"✅ Successfully generated image with {api['name']}!")
                    return result
                    
            except Exception as e:
                print(f"❌ {api['name']} failed: {e}")
                continue
        
        print(f"❌ All image generation methods failed")
        return None
    
    def _generate_with_gemini_imagen(self, prompt: str, negative_prompt: str = "") -> Optional[str]:
        """Generate image using Gemini Nano Banana (gemini-2.5-flash-image)"""
        
        print(f"   📤 Requesting from Gemini Nano Banana...")
        
        try:
            # Build the full prompt with negative prompt if provided
            full_prompt = f"Generate an image: {prompt}"
            if negative_prompt:
                full_prompt += f"\n\nAvoid: {negative_prompt}"
            
            # Generate image using Gemini Nano Banana
            response = self.image_model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.6,
                    candidate_count=1,
                )
            )
            
            # Check if response contains image data
            if response and hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'inline_data'):
                        # Get the image bytes
                        image_bytes = part.inline_data.data
                        
                        # Convert to PIL Image
                        img = Image.open(BytesIO(image_bytes))
                        
                        # Resize to target dimensions
                        img = img.resize((1024, 576), Image.Resampling.LANCZOS)
                        
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Convert to base64
                        buffer = BytesIO()
                        img.save(buffer, format='PNG', quality=95)
                        buffer.seek(0)
                        
                        base64_png = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        print(f"   ✅ Image generated: {img.size[0]}x{img.size[1]} pixels")
                        
                        return f"data:image/png;base64,{base64_png}"
            
            print(f"   ❌ No image data in response")
            return None
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle quota/rate limit errors with helpful message
            if '429' in error_msg or 'quota' in error_msg.lower() or 'ResourceExhausted' in str(type(e).__name__):
                print(f"   ⚠️  Quota exceeded for Gemini Nano Banana")
                print(f"   ℹ️  Please wait a moment and try again, or upgrade your API plan")
                print(f"   🔗 Check usage: https://ai.dev/rate-limit")
            else:
                print(f"   ❌ Gemini Nano Banana error: {e}")
                print(f"   ℹ️  Error type: {type(e).__name__}")
            
            return None
    
    def generate_mood_board(self, project_title: str, genre: str, logline: str, 
                          num_images: int = 4) -> List[Dict[str, Any]]:
        """
        Generate a mood board with multiple reference images
        Returns list of image data with descriptions
        """
        print(f"\n{'='*80}")
        print(f"🎨 MOOD BOARD GENERATION")
        print(f"{'='*80}")
        print(f"Project: {project_title}")
        print(f"Genre: {genre}")
        print(f"Images: {num_images}")
        print(f"{'='*80}\n")
        
        # Generate different prompts for mood board variety
        mood_prompts = self._generate_mood_board_prompts(
            project_title, genre, logline, num_images
        )
        
        mood_board = []
        
        for i, prompt_data in enumerate(mood_prompts, 1):
            print(f"🖼️ Generating image {i}/{num_images}: {prompt_data['category']}")
            print(f"   📝 Prompt: {prompt_data['prompt'][:100]}...")
            
            image_data = self.generate_image(
                prompt=prompt_data['prompt'],
                negative_prompt="text, watermark, low quality, blurry, distorted"
            )
            
            if image_data:
                mood_board.append({
                    'category': prompt_data['category'],
                    'description': prompt_data['description'],
                    'image_data': image_data,
                    'prompt': prompt_data['prompt']
                })
                print(f"   ✅ Image {i} generated successfully")
            else:
                print(f"   ❌ Image {i} generation failed")
            
            # Small delay between images
            if i < len(mood_prompts):
                time.sleep(2)
        
        print(f"\n✅ Mood board complete: {len(mood_board)}/{num_images} images generated\n")
        return mood_board
    
    def _generate_mood_board_prompts(self, title: str, genre: str, logline: str, 
                                    num_images: int) -> List[Dict[str, str]]:
        """Generate diverse prompts for mood board"""
        
        # Ask Gemini to create mood board prompts
        prompt = f"""Create {num_images} diverse visual prompts for a mood board:

Title: {title}
Genre: {genre}
Logline: {logline}

Generate {num_images} different image prompts covering:
1. Overall atmosphere
2. Color palette
3. Character mood
4. Visual style

For each, provide:
- Category
- Description (brief)
- Prompt (detailed visual description, 30-50 words)

Return as JSON array: [{{"category": "...", "description": "...", "prompt": "..."}}]"""
        
        try:
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Extract JSON
                text = response.text
                json_start = text.find('[')
                json_end = text.rfind(']') + 1
                
                if json_start != -1 and json_end > json_start:
                    prompts = json.loads(text[json_start:json_end])
                    print(f"✅ Generated {len(prompts)} mood board prompts via Gemini")
                    return prompts[:num_images]
        
        except Exception as e:
            print(f"⚠️ Gemini mood board prompt generation failed: {e}")
        
        # Fallback: Create generic prompts
        print(f"ℹ️ Using fallback mood board prompts")
        return [
            {
                'category': 'Atmosphere',
                'description': 'Overall visual atmosphere',
                'prompt': f"Cinematic {genre} film atmosphere, {logline}, highly detailed, atmospheric lighting, film grain"
            },
            {
                'category': 'Color Palette',
                'description': 'Color mood and tone',
                'prompt': f"{genre} color palette and mood, cinematic lighting, color grading reference, professional photography"
            },
            {
                'category': 'Character Mood',
                'description': 'Character emotion and style',
                'prompt': f"Character portrait in {genre} style, emotional expression, cinematic lighting, detailed face"
            },
            {
                'category': 'Visual Motif',
                'description': 'Key visual elements',
                'prompt': f"Key visual element from {genre} film, symbolic imagery, cinematic composition, artistic"
            }
        ][:num_images]
