"""
YouTube Automation Bot - Main Pipeline
Runs all steps: Script → Voiceover → Video → Upload
"""

import os
import sys
import logging
from datetime import datetime

# Import all modules
from scripts.generate_script import generate_script
from scripts.generate_voice import generate_voiceover
from scripts.generate_video import generate_video
from scripts.upload_youtube import upload_to_youtube

# ─── LOGGING SETUP ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log")
    ]
)
log = logging.getLogger(__name__)

# ─── TOPIC CONFIG ─────────────────────────────────────────────────
# Change this list to whatever topics you want videos about
TOPICS = [
    "5 Amazing Facts About Space",
    "How Artificial Intelligence Works",
    "Top 5 Health Tips for 2025",
    "Interesting Facts About the Ocean",
    "How Bitcoin Works Simply Explained",
]

def run_pipeline(topic: str):
    log.info(f"=== Starting pipeline for: {topic} ===")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"output/video_{timestamp}"

    # Step 1: Generate Script
    log.info("Step 1: Generating script...")
    from scripts.generate_script import generate_script_offline
    script_data = generate_script_offline(topic)
    if not script_data:
        log.error("Script generation failed. Aborting.")
        return False
    
    log.info(f"Title: {script_data['title']}")

    # Step 2: Generate Voiceover
    log.info("Step 2: Generating voiceover...")
    audio_path = f"{base_name}.mp3"
    success = generate_voiceover(script_data["script"], audio_path)
    if not success:
        log.error("Voiceover generation failed. Aborting.")
        return False

    # Step 3: Generate Video
    log.info("Step 3: Creating video...")
    video_path = f"{base_name}.mp4"
    success = generate_video(script_data, audio_path, video_path)
    if not success:
        log.error("Video generation failed. Aborting.")
        return False

    # Step 4: Upload to YouTube
    log.info("Step 4: Uploading to YouTube...")
    video_id = upload_to_youtube(
        video_path=video_path,
        title=script_data["title"],
        description=script_data["description"],
        tags=script_data["tags"],
        thumbnail_path=script_data.get("thumbnail_path")
    )
    if video_id:
        log.info(f"SUCCESS! Video uploaded: https://youtube.com/watch?v={video_id}")
        return True
    else:
        log.error("Upload failed.")
        return False


if __name__ == "__main__":
    # Pick a topic (cycles through the list)
    import json

    state_file = "state.json"
    if os.path.exists(state_file):
        with open(state_file) as f:
            state = json.load(f)
    else:
        state = {"index": 0}

    topic_index = state["index"] % len(TOPICS)
    topic = TOPICS[topic_index]

    success = run_pipeline(topic)

    # Advance to next topic
    state["index"] = topic_index + 1
    with open(state_file, "w") as f:
        json.dump(state, f)

    sys.exit(0 if success else 1)
