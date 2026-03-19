"""Streamlit UI for the Story-to-Image Generation Pipeline

Run with: streamlit run app.py
Requires: orchestrator.py and agents.py in the same directory
"""

import re
import streamlit as st
from orchestrator import run

# ── Page setup ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="StoryForge AI", page_icon="🎬", layout="centered")
st.title("🎬 StoryForge AI")
st.caption("Enter a prompt and let AI write and illustrate your story.")

# ── Helpers ──────────────────────────────────────────────────────────────────

def parse_scenes(story_text: str) -> list[str]:
    """Extract individual scene texts from the SCENE_N: format."""
    scenes = re.findall(r"SCENE_\d+:\s*(.+?)(?=SCENE_\d+:|$)", story_text, re.DOTALL)
    return [s.strip() for s in scenes if s.strip()]

# ── Input form ───────────────────────────────────────────────────────────────

prompt = st.text_area(
    "Story Prompt",
    placeholder="A lone astronaut discovers an ancient signal from the dark side of the moon…",
    height=120,
)

num_scenes = st.slider("Number of Scenes", min_value=1, max_value=10, value=4)

generate = st.button("Generate Story", type="primary", use_container_width=True)

# ── Generation ───────────────────────────────────────────────────────────────

if generate:
    if not prompt.strip():
        st.warning("Please enter a story prompt.")
    else:
        with st.spinner("Generating your story and images… this may take a minute."):
            try:
                result = run(prompt.strip(), num_scenes)
                st.session_state["result"] = result
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ── Results ──────────────────────────────────────────────────────────────────

if "result" in st.session_state:
    result = st.session_state["result"]
    scenes = parse_scenes(result.get("story", ""))
    images = result.get("image_urls", [])

    st.divider()
    st.subheader("Your Story")

    for i, (scene_text, img_url) in enumerate(zip(scenes, images), start=1):
        st.markdown(f"**Scene {i}**")
        img_col, txt_col = st.columns(2)
        with img_col:
            st.image(img_url, use_container_width=True)
        with txt_col:
            st.write(scene_text)
        st.divider()

    with st.expander("📖 Full story text"):
        st.write(result.get("story", ""))
