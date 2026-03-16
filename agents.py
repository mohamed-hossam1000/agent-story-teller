from unittest import result

from google import genai
from google.genai import types
from deapi import DeapiClient
from typing import TypedDict, Optional
from dotenv import load_dotenv

class StoryState(TypedDict):
    prompt: str
    story: Optional[str]
    image_path: Optional[str]

load_dotenv()
story_client = genai.Client()

story_sys_prompt = """You are a creative storyteller.
                      Write an engaging short story based on the user's prompt.
                      Keep it between 150-200 words."""

def story_agent(state: StoryState) -> StoryState:
    response = story_client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=story_sys_prompt),
    contents=state["prompt"]
    )

    state["story"] = [response.text]

    return state

image_client = DeapiClient()

image_sys_prompt = "Generate a vivid, detailed image that visually represents the story provided."

def image_agent(state: StoryState) -> StoryState:
    job = image_client.images.generate(
        prompt=image_sys_prompt + " " + state["story"][-1],
        model="Flux1schnell",
        width=1024,
        height=1024,
        steps=4,
        seed=-1,
        )
    
    response = job.wait()
    state["image_path"] = [response.result_url]

    return state