# Agent Story Teller

An AI-powered storytelling system that generates creative stories and corresponding images using Google Gemini and Flux models.

## Features

- **Story Generation**: Converts user prompts into multi-scene stories using Google Gemini AI
- **Image Generation**: Creates visual representations for each story scene using the Flux model
- **Automatic Output**: Saves generated stories and images to organized output directories
- **Dynamic Scene Control**: Configurable number of scenes (up to 10)
- **Consistent Characters**: Maintains visual consistency across scenes through AI instructions

## Project Structure

```
agent-story-teller/
├── agents.py          # Story and image generation agents
├── orchestrator.py    # Workflow orchestration and file handling
├── env/               # Python virtual environment
├── output/            # Generated stories and images
│   ├── story.txt      # Story scenes in text format
│   └── images/        # Generated PNG images
└── README.md          # Project documentation
```

## Requirements

- Python 3.8+
- Google Gemini API key
- DeAPI credentials for Flux image generation
- Required packages: `langgraph`, `google-genai`, `deapi-python-sdk`, `requests`, `python-dotenv`

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd agent-story-teller
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv env
   env\Scripts\activate  # On Windows
   source env/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   DEAPI_API_KEY=your_deapi_key
   ```

## Usage

Run the main script:
```bash
python orchestrator.py
```

Follow the prompt to enter your story idea:
```
Enter a prompt for the story: A brave knight embarks on a quest to find a hidden treasure
Enter number of scenes to generate (Max= 10) : 5
```

## Output

The script generates:
- **story.txt**: Contains all generated story scenes
- **images/**: Contains PNG files for each scene (scene_1.png, scene_2.png, etc.)

Example output structure:
```
output/
├── story.txt
└── images/
    ├── scene_1.png
    ├── scene_2.png
    ├── scene_3.png
    └── scene_4.png
```

## Configuration

Edit these constants in `orchestrator.py` to adjust behavior:
- `MAX_SCENES`: Maximum number of scenes to generate (default: 10)
- `DEFAULT_SCENES`: Default number of scenes (default: 5)

## How It Works

1. **Story Agent**: Receives user prompt and generates descriptive scene prompts using Gemini
2. **Image Agent**: Takes each scene description and generates a corresponding image using Flux
3. **Output Handler**: Saves stories as text and downloads/saves images locally

## API Integration

- **Google Gemini**: Creative text generation for story scenes
- **DeAPI/Flux**: High-quality image generation from text prompts
