"""Streamlit UI for the Story-to-Image Generation Pipeline

Run with: streamlit run app.py
Requires: orchestrator.py and agents.py in the same directory
"""

import re
import requests
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

def fetch_image_bytes(url: str) -> bytes | None:
    """Download image bytes from a URL. Returns None on failure."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception:
        return None

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

    # ── Save options ──────────────────────────────────────────────────────────

    st.divider()
    st.subheader("💾 Save")
    save_story_col, save_images_col = st.columns(2)

    with save_story_col:
        st.download_button(
            label="Download Story (.txt)",
            data=result.get("story", ""),
            file_name="story.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with save_images_col:
        if st.button("Download All Images (.zip)", use_container_width=True):
            import io, zipfile
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i, img_url in enumerate(images, start=1):
                    img_bytes = fetch_image_bytes(img_url)
                    if img_bytes:
                        zf.writestr(f"scene_{i}.png", img_bytes)
            st.download_button(
                label="Click to save images.zip",
                data=zip_buffer.getvalue(),
                file_name="story_images.zip",
                mime="application/zip",
                use_container_width=True,
            )
