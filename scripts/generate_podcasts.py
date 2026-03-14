#!/usr/bin/env python3
"""
Podcastfy-basierter Podcast-Generator als Ersatz für notebooklm-py
Verwendung: python3 scripts/generate_podcast.py --sources "url1,url2" --output /data/podcast.mp3
"""

import argparse
import os
import sys

def generate_podcast(sources: list[str], output_path: str, topic: str = None):
    try:
        from podcastfy.client import generate_podcast as pf_generate
    except ImportError:
        print("ERROR: podcastfy nicht installiert. Bitte 'pip install podcastfy' ausführen.")
        sys.exit(1)

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY nicht gesetzt.")
        sys.exit(1)

    os.environ["GEMINI_API_KEY"] = gemini_key

    print(f"Generiere Podcast aus {len(sources)} Quelle(n)...")
    print(f"Quellen: {sources}")

    try:
        # Podcastfy Konfiguration
        conversation_config = {
            "word_count": 2000,
            "conversation_style": ["formal", "educational"],
            "roles_person1": "Moderator",
            "roles_person2": "Experte",
            "dialogue_structure": [
                "Introduction",
                "Main Content",
                "Key Takeaways",
                "Conclusion"
            ],
            "podcast_name": "ENT Medical Update",
            "podcast_tagline": "HNO Fortbildung",
            "output_language": "German",
            "engagement_techniques": [
                "rhetorical questions",
                "anecdotes",
                "analogies"
            ],
            "creativity": 0.7
        }

        tts_config = {
            "default_tts_model": "edge",  # Kostenlos
            "output_directories": {
                "audio": os.path.dirname(output_path) or "/tmp"
            }
        }

        kwargs = {
            "conversation_config": conversation_config,
            "tts_model": "edge",
            "llm_model_name": "gemini-2.5-flash",
            "api_key_label": "GEMINI_API_KEY",
        }

        if sources and sources[0].startswith("http"):
            kwargs["urls"] = sources
        else:
            kwargs["text"] = "\n\n".join(sources)

        if topic:
            kwargs["topic"] = topic

        audio_file = pf_generate(**kwargs)

        if audio_file and os.path.exists(str(audio_file)):
            # Zieldatei kopieren
            import shutil
            shutil.copy(str(audio_file), output_path)
            print(f"SUCCESS: Podcast gespeichert unter {output_path}")
            return True
        else:
            print(f"ERROR: Podcast-Datei nicht gefunden: {audio_file}")
            return False

    except Exception as e:
        print(f"ERROR: Podcast-Generierung fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ENT Podcast Generator")
    parser.add_argument(
        "--sources",
        type=str,
        required=True,
        help="Kommagetrennte URLs oder Texte"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="/tmp/podcast.mp3",
        help="Ausgabepfad für die MP3-Datei"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Optionales Thema für den Podcast"
    )

    args = parser.parse_args()
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]

    success = generate_podcast(
        sources=sources,
        output_path=args.output,
        topic=args.topic
    )

    sys.exit(0 if success else 1)
  
