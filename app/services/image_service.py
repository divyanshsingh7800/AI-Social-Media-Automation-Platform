import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


# --------------------------------------------------
# HUGGING FACE CLIENT
# --------------------------------------------------

client = InferenceClient(
    provider="auto",
    api_key=HF_TOKEN
)


# --------------------------------------------------
# PROJECT DIRECTORIES
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

IMAGE_DIR = BASE_DIR / "generated" / "images"

IMAGE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# IMAGE GENERATION
# --------------------------------------------------

def generate_image(
    prompt,
    filename
):

    try:

        print("Starting image generation...")

        image = client.text_to_image(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell"
        )

        image_path = IMAGE_DIR / filename

        image.save(image_path)

        print(
            f"Image saved: {image_path}"
        )

        return str(image_path)

    except Exception as e:

        print(
            f"Image generation failed: {e}"
        )

        return None


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    test_prompt = """
    A professional female doctor wearing a crisp white lab coat
    and stethoscope, interacting with a futuristic holographic
    AI interface in a modern medical research laboratory.

    Photorealistic commercial photography,
    cinematic lighting,
    realistic skin and fabric,
    clean futuristic medical environment,
    deep navy blue, white and teal color palette,
    eye-level medium shot,
    shallow depth of field,
    highly detailed,
    no text inside the image.
    """

    result = generate_image(
        test_prompt,
        "test_hf_image.png"
    )

    print(
        f"Generated image: {result}"
    )
