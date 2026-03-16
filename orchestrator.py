"""Story-to-Image Generation Orchestrator

Orchestrates a two-stage workflow:
1. Generate story scenes from user prompt (story_agent)
2. Generate images for each scene (image_agent)
"""
from langgraph.graph import StateGraph, START, END
from agents import StoryState, story_agent, image_agent
import os
import requests
from pathlib import Path


# Build the workflow graph: story generation → image generation
workflow = StateGraph(StoryState)
workflow.add_node("generate_story", story_agent)
workflow.add_node("generate_image", image_agent)
workflow.add_edge(START, "generate_story")
workflow.add_edge("generate_story", "generate_image")
workflow.add_edge("generate_image", END)

# Compile workflow into executable app
app = workflow.compile()

# Configuration constants
MAX_SCENES = 10
DEFAULT_SCENES = 5

def run(user_prompt: str, num_scenes: int = DEFAULT_SCENES):
    """Execute the story and image generation pipeline.
    
    Args:
        user_prompt: User's story prompt
        num_scenes: Number of scenes to generate (max 10)
    
    Returns:
        State dict containing generated story scenes and image URLs
    """
    if num_scenes > MAX_SCENES:
        num_scenes = MAX_SCENES
    state = {"prompt": user_prompt, "num_scenes": num_scenes}
    state = app.invoke(state)
    return state

if __name__ == "__main__":
    # Get story prompt from user
    user_prompt = input("Enter a prompt for the story: ")
    num_scenes = int(input(f"Enter number of scenes to generate (Max= {MAX_SCENES}) : "))
    state = run(user_prompt, num_scenes)
    
    # Create output directory structure
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Write story scenes to text file
    with open(output_dir / "story.txt", "w") as f:
        f.write("Generated Story Scenes:\n")
        f.write("=" * 50 + "\n\n")
        for i, scene in enumerate(state["story"], 1):
            f.write(f"Scene {i}:\n{scene}\n\n")
    
    # Download and save generated images for each scene
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)
    
    for i, img_url in enumerate(state["image_url"], 1):
        try:
            # Fetch image from URL
            response = requests.get(img_url)
            if response.status_code == 200:
                # Save image file
                with open(images_dir / f"scene_{i}.png", "wb") as f:
                    f.write(response.content)
                print(f"✓ Saved Scene {i} image")
        except Exception as e:
            print(f"✗ Error saving Scene {i} image: {e}")
    
    # Display completion summary
    print(f"\n✓ Story saved to: {output_dir / 'story.txt'}")
    print(f"✓ Images saved to: {images_dir}")
