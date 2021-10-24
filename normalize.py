from PIL import Image

TARGET_RES_W = 320
TARGET_RES_H = 180
TARGET_AR = TARGET_RES_W / TARGET_RES_H


def normalize(img: Image):
    print("➤ Image resolution:", img.size)
    # normalize aspect ratio
    aspect_ratio = img.width / img.height
    if aspect_ratio < TARGET_AR:  # too tall
        print("➤ Image too tall, cropping.")
        target_height = round(9 * img.width / 16)
        print(f"➤ Target size: {(img.width, target_height)}")
        excess = img.height - target_height
        excess_top = excess // 2
        excess_bottom = excess - excess_top
        result = img.crop(
            (0, excess_top, img.width, img.height - excess_bottom)
        )
    elif aspect_ratio > TARGET_AR:  # too wide
        print("➤ Image too wide, cropping.")
        target_width = round(img.height * 16 / 9)
        print(f"➤ Target size: {(target_width, img.height)}")
        excess = img.width - target_width
        excess_left = excess // 2
        excess_right = excess - excess_left
        result = img.crop(
            (excess_left, 0, img.width - excess_right, img.height)
        )
    else:
        result = img

    # Remove alpha channel (unsupported by JPEG)
    result = result.convert("RGB")

    # Scale
    target_size = (TARGET_RES_W, TARGET_RES_H)
    print(f"➤ Resizing image to {(target_size)}")
    return result.resize(target_size)
