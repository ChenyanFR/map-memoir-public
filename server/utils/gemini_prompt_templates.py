def build_prompt(place, theme):
    name = place.get("name", "an unknown location")
    address = place.get("address", "")
    
    if theme == "fairy_tale":
        return f"""
        Write a magical fairy tale that takes place in {name}, located at {address}.
        Include mystical creatures, a protagonist, and an enchanted journey.
        Keep the tone whimsical and vivid, suitable for children.
        """

    elif theme == "documentary":
        return f"""
        Write a documentary-style narration about the history, culture, and current significance of {name}, located at {address}.
        Make it educational and informative, like a National Geographic script.
        """

    elif theme == "music_video":
        return f"""
        Write a poetic music video script inspired by the vibe and scenery of {name}, at {address}.
        Include short lyrics and scene transitions like a storyboard.
        """

    return f"Write a creative story set in {name}, located at {address}."
