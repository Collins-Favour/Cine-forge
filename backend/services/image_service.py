"""
Image Generation Service using Pollinations.ai (100% Free)
"""
import os
import requests
import base64
from io import BytesIO
from PIL import Image
from typing import Optional
import time
import urllib.parse


class ImageGenerationService:
    """Service for generating images using Pollinations.ai (completely free, no API key needed)"""
    
    def __init__(self):
        # Pollinations.ai doesn't require API keys - completely free!
        self.api_url = "https://image.pollinations.ai/prompt"
        print("✅ Using Pollinations.ai - 100% FREE image generation (no API key needed)")
    
    def generate_image(self, prompt: str, negative_prompt: str = "", retries: int = 3) -> Optional[str]:
        """
        Generate image from text prompt using Pollinations.ai
        Returns base64 encoded image string or None if failed
        Completely FREE - no API key or signup required!
        """
        # URL encode the prompt
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Build the URL with parameters
        # Pollinations.ai uses URL parameters for image generation
        image_url = f"{self.api_url}/{encoded_prompt}"
        
        # Add parameters for better quality
        params = {
            "width": 768,
            "height": 512,
            "seed": -1,  # Random seed for variety
            "nologo": "true",  # Remove watermark
            "enhance": "true"  # Better quality
        }
        
        # Add negative prompt if provided
        if negative_prompt:
            params["negative"] = negative_prompt
        
        for attempt in range(retries):
            try:
                print(f"🎨 Generating image with Pollinations.ai (attempt {attempt + 1}/{retries})...")
                print(f"   Prompt: {prompt[:100]}...")
                
                response = requests.get(
                    image_url,
                    params=params,
                    timeout=60
                )
                
                if response.status_code == 200:
                    # Get image bytes
                    image_bytes = response.content
                    
                    # Verify it's a valid image
                    try:
                        img = Image.open(BytesIO(image_bytes))
                        img.verify()
                        
                        # Reopen for processing (verify closes the file)
                        img = Image.open(BytesIO(image_bytes))
                        
                        # Convert to RGB if needed
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Save to bytes buffer
                        buffer = BytesIO()
                        img.save(buffer, format='PNG', quality=95)
                        buffer.seek(0)
                        
                        # Convert to base64
                        base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        print(f"✅ Image generated successfully! (FREE via Pollinations.ai)")
                        
                        return f"data:image/png;base64,{base64_image}"
                        
                    except Exception as img_error:
                        print(f"❌ Invalid image received: {img_error}")
                        if attempt < retries - 1:
                            time.sleep(5)
                            continue
                
                else:
                    print(f"❌ Image generation failed: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    
                    if attempt < retries - 1:
                        print(f"   Retrying in 5 seconds...")
                        time.sleep(5)
                        continue
                    
            except requests.exceptions.Timeout:
                print(f"⏱️ Request timeout (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(5)
                    continue
                    
            except Exception as e:
                print(f"❌ Error generating image: {e}")
                import traceback
                traceback.print_exc()
                if attempt < retries - 1:
                    time.sleep(5)
                    continue
        
        print(f"❌ Failed to generate image after {retries} attempts")
        return None
    
    def save_image_to_file(self, base64_image: str, filepath: str) -> bool:
        """Save base64 image to file"""
        try:
            # Remove data URI prefix if present
            if base64_image.startswith('data:image'):
                base64_image = base64_image.split(',')[1]
            
            # Decode and save
            image_data = base64.b64decode(base64_image)
            
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def generate_and_save(self, prompt: str, filepath: str, negative_prompt: str = "") -> Optional[str]:
        """Generate image and save to file, return file path"""
        base64_image = self.generate_image(prompt, negative_prompt)
        
        if base64_image:
            if self.save_image_to_file(base64_image, filepath):
                return filepath
        
        return None
