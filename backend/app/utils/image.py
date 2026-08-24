ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_image_file(filename: str, size: int):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Định dạng file không hỗ trợ: '{ext}'. Vui lòng tải file JPG, PNG hoặc WEBP.")
    if size > MAX_FILE_SIZE:
        raise ValueError("Dung lượng file vượt quá giới hạn tối đa 10MB.")
