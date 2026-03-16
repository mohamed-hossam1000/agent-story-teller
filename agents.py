"""Story Generation and Image Creation Agents

This module contains two agents that work together:
1. story_agent: Generates story scenes from user prompt using Google Gemini
2. image_agent: Generates images for each story scene using Flux model
"""
from google import genai
from google.genai import types
from deapi import DeapiClient
from typing import TypedDict, Optional
import re
from dotenv import load_dotenv

# State schema for the story generation workflow
class StoryState(TypedDict):
    prompt: str  # User's original story prompt
    num_scenes: int  # Number of scenes to generate
    story: Optional[list[str]]  # Generated scene descriptions
    image_url: Optional[list[str]]  # URLs of generated images

# Initialize Gemini API client
load_dotenv()
story_client = genai.Client()

def get_story_prompt(num_scenes: int) -> str:
    """Build system prompt for story generation with dynamic scene count.
    
    Args:
        num_scenes: Number of scenes to generate
    
    Returns:
        System prompt string with formatting instructions
    """
    scenes_format = "\n".join([f"SCENE_{i+1}: [scene description]" for i in range(num_scenes)])
    return f"""You are a creative visual storyteller. Given a user prompt,
              generate a short story told across exactly {num_scenes} scenes.

              Output ONLY in this exact format, nothing else before or after:

              {scenes_format}

              Rules for each scene description:
                - Write it as an image generation prompt, not as narrative prose
                - Start every scene by describing the main character's consistent appearance (e.g. "a young woman with red hair and a brown leather jacket")
                - Describe the setting, lighting, mood, and action happening in that specific scene
                - Make each scene descriptive enough to be visually distinct, but ensure all scenes are clearly part of the same story
                - Ensure smooth transitions between scenes
                - Make the description as long as needed to maintain consistent visual details across all scenes especially for maintaining character consistency, but do not exceed 100 words per scene
                - Do not use character names, only visual descriptions.
                - Maintain consistent visual details (character appearance, art style, color palette) across all scenes"""


def story_agent(state: StoryState) -> StoryState:
    """Generate story scenes from user prompt using Google Gemini.
    
    Uses regex to extract SCENE_N formatted outputs from model response.
    """
    # Build dynamic system prompt based on number of scenes
    sys_prompt = get_story_prompt(state["num_scenes"])
    response = story_client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=sys_prompt),
    contents=state["prompt"]
    )

    # Extract scene descriptions using regex
    scenes = re.findall(r'SCENE_\d+:\s*(.+)', response.text)
    state["story"] = scenes

    return state

# Initialize image generation client
image_client = DeapiClient()

def image_agent(state: StoryState) -> StoryState:
    """Generate images for each story scene using Flux model.
    
    Iterates through story scenes and creates corresponding images.
    """
    # Initialize image URL list to store results
    state["image_url"] = []
    for i, scene in enumerate(state["story"]):
        # Submit image generation job with fixed parameters
        job = image_client.images.generate(
            prompt=scene,
            model="Flux1schnell",
            width=1024,
            height=512,
            steps=10,
            seed=42,
            )
        
        # Wait for job completion and collect result URL
        response = job.wait()
        state["image_url"].append(response.result_url)

    return state