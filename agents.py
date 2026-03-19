"""Story Generation and Image Creation Agents

This module contains agents for multi-stage story generation workflow:
1. story_agent: Generates story scenes from user prompt using Google Gemini
2. image_agent: Generates detailed image prompts for each story scene using Google Gemini
3. image_generation_tool: Creates images from prompts using Flux model
"""
from google import genai
from google.genai import types
from deapi import DeapiClient
from typing import TypedDict, Optional
import re
from dotenv import load_dotenv

# State schema for the story generation workflow
class StoryState(TypedDict):
    user_prompt: str  # User's original story prompt
    num_scenes: int  # Number of scenes to generate
    story: Optional[str]  # Generated scene descriptions
    scene_prompts: Optional[list[str]]  # Extracted prompts for image generation
    image_urls: Optional[list[str]]  # URLs of generated images

# Initialize Gemini API client
load_dotenv()
story_client = genai.Client()

STORY_PROMPT = """You are a creative storyteller. Given a user prompt, 
                  write a compelling short story told across exactly {num_scenes} scenes.

                  Output ONLY in this exact format, nothing else before or after:

                  {scenes_format}

                  Rules for each scene:
                  - Write in vivid narrative prose, describing action, emotion, and atmosphere
                  - Each scene should naturally flow into the next
                  - Keep each scene between 50-80 words
                  - Do not use any image generation language
                  - Give characters consistent traits and appearances across all scenes"""

IMAGE_PROMPT = """You are a visual prompt engineer. Given a story, convert each scene 
                  into a detailed image generation prompt.

                  Output ONLY in this exact format, nothing else before or after:

                  {scenes_format}

                  Rules for each scene prompt:
                  - Start every scene with a full description of the main character's appearance (e.g. "a young woman with red hair and a brown leather jacket")
                  - Describe setting, lighting, mood, and action in visual terms only
                  - Each prompt must be self-contained and visually understandable on its own
                  - Maintain consistent character appearance, art style, and color palette across all scenes
                  - Do not use character names, only visual descriptions
                  - Do not exceed 100 words per scene"""

def get_prompt(mode: str, num_scenes: int) -> str:
    """Return system prompt for story generation or image prompt generation.
    
    Args:
        mode: either "story" or "image"
        num_scenes: number of scenes to generate
    
    Returns:
        Formatted system prompt string
    """
    scenes_format = "\n".join([f"SCENE_{i+1}: [scene description]" for i in range(num_scenes)])
    
    if mode == "story":
        return STORY_PROMPT.format(num_scenes=num_scenes, scenes_format=scenes_format)
    elif mode == "image":
        return IMAGE_PROMPT.format(scenes_format=scenes_format)
    else:
        raise ValueError(f"Invalid mode '{mode}'. Use 'story' or 'image'.")

def story_agent(state: StoryState) -> StoryState:
    """Generate story scenes from user prompt using Google Gemini."""
    # Build dynamic system prompt based on number of scenes
    sys_prompt = get_prompt("story", state["num_scenes"])
    response = story_client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=sys_prompt),
    contents=state["user_prompt"]
    )

    # Store generated story with all scenes
    state["story"] = response.text

    return state

def image_agent(state: StoryState) -> StoryState:
    """Generate image prompts for each story scene using Google Gemini.
    
    Uses regex to extract SCENE_N formatted outputs from model response.
    """
    # Build dynamic system prompt based on number of scenes
    sys_prompt = get_prompt("image", state["num_scenes"])
    response = story_client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=sys_prompt),
    contents=state["story"]
    )

    # Extract scene prompts using regex from SCENE_N format
    scenes = re.findall(r'SCENE_\d+:\s*(.+)', response.text)
    state["scene_prompts"] = scenes

    return state

# Initialize image generation client
image_client = DeapiClient()

def image_generation_tool(state: StoryState) -> StoryState:
    """Generate images for each story scene using Flux model.
    
    Iterates through scene prompts and creates corresponding images via API.
    """
    # Initialize image URLs list to store all generated image URLs
    state["image_urls"] = []
    for i, scene in enumerate(state["scene_prompts"]):
        # Submit image generation job with Flux parameters
        job = image_client.images.generate(
            prompt=scene,
            model="Flux_2_Klein_4B_BF16",
            width=1024,
            height=512,
            steps=4,
            seed=42,
            )
        
        # Wait for completion and store generated image URL
        response = job.wait()
        state["image_urls"].append(response.result_url)

    return state