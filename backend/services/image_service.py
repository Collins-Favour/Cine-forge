"""
Image Generation Service using Google Gemini Imagen 4
Generates high-quality cinematic storyboard visuals with movie title overlay.
"""
import os
import base64
import time
from io import BytesIO
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from PIL import Image
from utils.logger import get_logger

# Ensure .env is loaded even when this module is imported early
load_dotenv(override=True)

logger = get_logger('cineforge.ai')

# Imagen 4 model identifier (fast variant for responsive generation)
IMAGEN_MODEL = "imagen-4.0-fast-generate-001"


class ImageGenerationService:
    """Google Gemini Imagen 4 image generation service."""

    def __init__(self):
        # Try env var first, then Flask app config as fallback
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            try:
                from flask import current_app
                self.api_key = current_app.config.get('GEMINI_API_KEY')
            except (RuntimeError, ImportError):
                pass
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.model = IMAGEN_MODEL
            logger.info("ImageGenerationService initialized (Google Gemini Imagen 4)")
        except ImportError:
            raise ImportError(
                "google-genai package required. Install with: pip install google-genai"
            )

    # ------------------------------------------------------------------
    # Core prompt builder – movie title + synopsis → cinematic prompt
    # ------------------------------------------------------------------
    @staticmethod
    def build_cinematic_prompt(
        title: str,
        synopsis: str = "",
        style: str = "cinematic",
        extra: str = "",
    ) -> str:
        """
        Build a simple, effective image-generation prompt from movie title.
        Keeps it short to avoid over-constraining the model.
        """
        prompt = f'Cinematic {style} movie poster for "{title}". Dramatic lighting, professional color grading, 35mm film aesthetic.'
        if extra:
            prompt += f" {extra.strip()}"
        return prompt

    # ------------------------------------------------------------------
    # Generate a single image – returns data:image/png;base64,…
    # ------------------------------------------------------------------
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        retries: int = 2,
    ) -> Optional[str]:
        """
        Generate an image via Gemini Imagen 4.
        Returns a ``data:image/png;base64,...`` string or ``None`` on failure.
        """
        from google import genai
        from google.genai import types

        # Note: Gemini Imagen API does NOT support negative_prompt.
        # We ignore the parameter silently for backward compatibility.

        config = types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            person_generation="ALLOW_ADULT",
        )

        for attempt in range(1, retries + 1):
            try:
                logger.debug(f"Imagen 4 generation attempt {attempt}/{retries}")
                logger.debug(f"Prompt: {prompt[:200]}...")

                response = self.client.models.generate_images(
                    model=self.model,
                    prompt=prompt,
                    config=config,
                )

                if response and response.generated_images:
                    img_bytes = response.generated_images[0].image.image_bytes
                    # Validate
                    img = Image.open(BytesIO(img_bytes))
                    if img.mode != "RGB":
                        img = img.convert("RGB")

                    buf = BytesIO()
                    img.save(buf, format="PNG", quality=95)
                    buf.seek(0)

                    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                    logger.info(f"Image generated successfully ({img.size[0]}x{img.size[1]})")
                    return f"data:image/png;base64,{b64}"

                logger.warning("Imagen 4 returned no images")

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Imagen 4 error (attempt {attempt}): {error_msg}", exc_info=True)

                # Rate-limit / quota – back off
                if "429" in error_msg or "quota" in error_msg.lower():
                    logger.warning("Rate limit hit, backing off 10s ...")
                    time.sleep(10)
                elif attempt < retries:
                    time.sleep(3)

        logger.error(f"Image generation failed after {retries} attempts")
        return None

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------
    def generate_movie_poster(
        self,
        title: str,
        synopsis: str = "",
        genre: str = "cinematic",
        negative_prompt: str = "",
    ) -> Optional[str]:
        """Build a movie-poster prompt from metadata, then generate."""
        prompt = self.build_cinematic_prompt(
            title=title,
            synopsis=synopsis,
            style=genre,
        )
        return self.generate_image(prompt, negative_prompt)

    def generate_enhanced_image(
        self,
        scene_text: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
    ) -> Optional[str]:
        """Generate from a raw scene description (auto-enhanced)."""
        prompt = self._fallback_enhance(scene_text)
        return self.generate_image(prompt, negative_prompt, width, height)

    # ------------------------------------------------------------------
    # Batch generation
    # ------------------------------------------------------------------
    def generate_storyboard_batch(
        self,
        scene_texts: List[str],
        negative_prompt: str = "",
        delay: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """Generate images for multiple scenes."""
        results: List[Dict[str, Any]] = []

        for i, text in enumerate(scene_texts, 1):
            logger.info(f"Batch image {i}/{len(scene_texts)} ...")
            prompt = self._fallback_enhance(text)
            image_data = self.generate_image(prompt, negative_prompt)

            results.append({
                "index": i,
                "prompt": prompt,
                "image_data": image_data,
                "status": "completed" if image_data else "failed",
            })

            if i < len(scene_texts):
                time.sleep(delay)

        completed = sum(1 for r in results if r["status"] == "completed")
        logger.info(f"Batch complete: {completed}/{len(scene_texts)} images generated")
        return results

    # ------------------------------------------------------------------
    # Style-consistency helper (pure logic – no API call)
    # ------------------------------------------------------------------
    def enhance_prompt_for_consistency(
        self, base_prompt: str, project_style: Dict[str, Any]
    ) -> str:
        """Append project-specific style keywords to an image prompt."""
        parts = []
        kw = project_style.get("mood_keywords") or []
        cp = project_style.get("color_palette") or []
        if kw:
            parts.append(f"Style: {', '.join(kw)}")
        if cp:
            parts.append(f"Color palette: {', '.join(cp)}")
        if parts:
            return f"{base_prompt}. {'. '.join(parts)}"
        return base_prompt

    # ------------------------------------------------------------------
    # Mood board generation
    # ------------------------------------------------------------------
    def generate_mood_board(
        self,
        project_title: str,
        genre: str,
        logline: str,
        num_images: int = 4,
    ) -> List[Dict[str, Any]]:
        """Generate a set of mood-reference images for the project."""
        prompts = self._build_mood_prompts(project_title, genre, logline, num_images)
        mood_board: List[Dict[str, Any]] = []

        for i, pd in enumerate(prompts, 1):
            logger.info(f"Mood board image {i}/{num_images}: {pd['category']}")
            image_data = self.generate_image(pd["prompt"])
            if image_data:
                mood_board.append({
                    "category": pd["category"],
                    "description": pd["description"],
                    "image_data": image_data,
                    "prompt": pd["prompt"],
                })
                logger.info(f"Mood board image {i} generated")
            else:
                logger.warning(f"Mood board image {i} failed")

            if i < len(prompts):
                time.sleep(2)

        logger.info(f"Mood board complete: {len(mood_board)}/{num_images} images")
        return mood_board

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _fallback_enhance(text: str) -> str:
        """Build a cinematic prompt from raw text."""
        clean = text.strip()[:300]
        return (
            f"{clean}, cinematic movie poster composition, "
            "35mm film, dramatic lighting, highly detailed, "
            "professional color grading, depth of field, "
            "volumetric lighting, award-winning cinematography"
        )

    @staticmethod
    def _build_mood_prompts(
        title: str, genre: str, logline: str, n: int
    ) -> List[Dict[str, str]]:
        """Create diverse mood-board prompt dicts using movie title + logline."""
        templates = [
            {
                "category": "Atmosphere",
                "description": "Overall visual atmosphere",
                "prompt": (
                    f'Cinematic {genre} movie poster with bold title "{title}" displayed prominently. '
                    f"{logline}. Atmospheric lighting, film grain, moody, highly detailed."
                ),
            },
            {
                "category": "Color Palette",
                "description": "Color mood and tone",
                "prompt": (
                    f'Movie poster for "{title}" ({genre}). '
                    f'Title "{title}" in stylised typography. '
                    f"{logline}. Cinematic lighting, professional color grading."
                ),
            },
            {
                "category": "Character Mood",
                "description": "Character emotion and style",
                "prompt": (
                    f'Character-driven movie poster for "{title}" ({genre}). '
                    f'Title "{title}" overlay. '
                    f"{logline}. Emotional expression, cinematic lighting, detailed face."
                ),
            },
            {
                "category": "Visual Motif",
                "description": "Key visual elements",
                "prompt": (
                    f'Artistic movie poster for "{title}". '
                    f'Bold title text "{title}". '
                    f"{logline}. Symbolic imagery, cinematic composition."
                ),
            },
            {
                "category": "Setting",
                "description": "Primary location aesthetic",
                "prompt": (
                    f'Wide-angle establishing shot movie poster for "{title}" ({genre}). '
                    f'Title "{title}" across the top. '
                    f"{logline}. Golden hour, cinematic landscape, epic scope."
                ),
            },
            {
                "category": "Conflict",
                "description": "Dramatic tension visual",
                "prompt": (
                    f'Dramatic tension movie poster for "{title}". '
                    f'Title "{title}" in bold. '
                    f"{logline}. Chiaroscuro lighting, suspenseful, high contrast."
                ),
            },
            {
                "category": "Resolution",
                "description": "Closing mood reference",
                "prompt": (
                    f'Final act movie poster for "{title}" ({genre}). '
                    f'Title "{title}" displayed. '
                    f"{logline}. Poignant, hopeful or bittersweet, cinematic still."
                ),
            },
            {
                "category": "Texture",
                "description": "Surface and material feel",
                "prompt": (
                    f'Textured movie poster for "{title}" ({genre}). '
                    f'Title "{title}" embossed. '
                    f"{logline}. Detailed surfaces, tactile, film grain."
                ),
            },
        ]
        return templates[:n]
