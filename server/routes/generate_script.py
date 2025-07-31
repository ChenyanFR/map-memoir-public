from flask import Blueprint, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

load_dotenv()

script_bp = Blueprint('script', __name__)
CORS(script_bp)

@script_bp.route("/generate_script", methods=["POST"])
def generate_script():
    data = request.get_json()
    place = data.get("place")
    theme = data.get("theme")

    if not place or not theme:
        return jsonify({"error": "Missing place or theme"}), 400

    try:
        name = place.get("name")
        address = place.get("address")

        # Theme-based video overlay logic (example placeholder):
        # If you want to generate a video with a theme overlay, you would add logic here
        # For example, using moviepy to add an overlay image if theme == "fairy_tale"
        # from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
        # if theme == "fairy_tale":
        #     clip = VideoFileClip("path/to/video.mp4")
        #     overlay = ImageClip("overlays/fairy-tale.png").set_duration(clip.duration).resize(clip.size).set_opacity(0.5)
        #     final = CompositeVideoClip([clip, overlay])
        #     final.write_videofile("path/to/output/fairy_tale_video.mp4")

        prompt = f"""
        Tell a short story (less than 300 words) about a place called "{name}" located at "{address}" 
        with the theme of "{theme}". Make it imaginative, engaging, and friendly.
        """

        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a creative storyteller."},
            {"role": "user", "content": prompt}
        ])

        story = response.choices[0].message.content.strip()
        return jsonify({"script": story})

    except Exception as e:
        print("Error generating story:", e)
        return jsonify({"error": "Internal Server Error"}), 500
