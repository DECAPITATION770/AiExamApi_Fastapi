import os
from datetime import datetime
import uuid
import base64

from fastapi import UploadFile, File

from core.configs import settings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

async def save_image(upload_file: UploadFile, name_prefix: str = None) -> None | tuple[str, str]:
    folder = settings.UPLOAD_PATH
    if upload_file is None:
        return None

    save_dir = os.path.join(BASE_DIR, folder)
    os.makedirs(save_dir, exist_ok=True)

    ext = os.path.splitext(upload_file.filename)[1]
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{f'_{name_prefix}_' if name_prefix else ''}{uuid.uuid4()}{ext}"

    path = os.path.join(save_dir, filename)

    content = await upload_file.read()
    with open(path, "wb") as f:
        f.write(content)

    return path, os.path.join(folder, filename)


def image2base64(img_path: str):
    with open(img_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode("utf-8")
    return encoded
