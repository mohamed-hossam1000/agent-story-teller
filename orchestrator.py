from langgraph.graph import StateGraph, START, END
from agents import StoryState, story_agent, image_agent


workflow = StateGraph(StoryState)
workflow.add_node("generate_story", story_agent)
workflow.add_node("generate_image", image_agent)
workflow.add_edge(START, "generate_story")
workflow.add_edge("generate_story", "generate_image")
workflow.add_edge("generate_image", END)

app = workflow.compile()

def run(user_prompt: str):
    state = {"prompt": user_prompt}
    state = app.invoke(state)
    print("Generated Story:\n", state["story"][-1])
    print("Image saved at:", state["image_path"][-1])

if __name__ == "__main__":
    user_input = input("Enter a prompt for the story: ")
    run(user_input)
