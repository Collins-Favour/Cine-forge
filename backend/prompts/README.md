# AI Prompts Directory

This directory contains all AI prompt templates used in CineForge AI.

## Files:

### `script_generation.txt`
**Used by:** `services/groq_service.py` → `generate_screenplay()`
**Purpose:** Generate complete screenplay from project synopsis
**Variables:**
- `{title}` - Project title
- `{genre}` - Film genre
- `{logline}` - One-line story summary
- `{synopsis}` - Full story synopsis

**Output:** JSON with scenes, characters, dialogue, mood, lighting, camera notes

---

### `storyboard_prompt_generation.txt`
**Used by:** `services/gemini_service.py` → `generate_storyboard_prompt()`
**Purpose:** Convert scene description into image generation prompt
**Variables:**
- `{scene_description}` - Scene text from script
- `{style}` - Visual style (cinematic, noir, etc.)

**Output:** Detailed image prompt for Gemini Imagen 3

---

## How to Edit Prompts:

1. Open the `.txt` file you want to modify
2. Edit the text while keeping variable placeholders: `{variable_name}`
3. Save the file
4. Restart the backend server
5. New prompts will be used immediately

## Testing Prompts:

Check backend terminal logs to see:
- Full prompts being sent to AI
- AI responses
- Any errors

Enable detailed logging in services for debugging.
