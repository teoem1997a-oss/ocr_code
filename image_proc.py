import cv2

def process_frame(frame):
    """
    ⚡⚡⚡ ULTRA-LIGHTWEIGHT - CHẾ ĐỘ ÉP XUNG TRỊ VÙNG F9 TO
    """
    try:
        if frame is None or frame.size == 0:
            return None

        # 1. Convert BGR → Grayscale để giảm dung lượng ảnh (1-3ms)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 2. 🔥 THU THUẬT ÉP XUNG: Thu nhỏ ảnh 50%
        # Nếu khung F9 bạn khoanh rộng hơn 400 pixel, tool sẽ tự động thu nhỏ ảnh đi một nửa.
        # AI vẫn đọc được chữ (vì chữ trên live thường to), nhưng tốc độ sẽ nhanh gấp 3-4 lần!
        height, width = gray.shape
        if width > 400 or height > 400:
            gray = cv2.resize(gray, (width // 2, height // 2), interpolation=cv2.INTER_LINEAR)

        return gray

    except Exception as e:
        return None