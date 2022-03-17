from typing import Tuple

from PIL import Image

def normalize(img: Image, target_size: Tuple[int, int]):
    print("➤ Image resolution:", img.size)
    target_width, target_height = target_size
    target_aspect_ratio = target_width / target_height

    # normalize aspect ratio
    aspect_ratio = img.width / img.height
    if aspect_ratio < target_aspect_ratio:  # too tall
        print("➤ Image too tall, cropping.")
        target_crop_height = round(target_height * img.width / target_width)
        print(f"➤ Target size: {(img.width, target_crop_height)}")
        excess_height = img.height - target_crop_height
        excess_top = excess_height // 2
        excess_bottom = excess_height - excess_top
        result = img.crop(
            (0, excess_top, img.width, img.height - excess_bottom)
        )
    elif aspect_ratio > target_aspect_ratio:  # too wide
        print("➤ Image too wide, cropping.")
        target_crop_width = round(img.height * target_width / target_height)
        print(f"➤ Target size: {(target_crop_width, img.height)}")
        excess_width = img.width - target_crop_width
        excess_left = excess_width // 2
        excess_right = excess_width - excess_left
        result = img.crop(
            (excess_left, 0, img.width - excess_right, img.height)
        )
    else:
        result = img

    print(f"➤ Resizing image to {(target_size)}")
    # Remove alpha channel (unsupported by JPEG),
    # and scale to target resolution.
    return result.convert("RGB").resize(target_size)
