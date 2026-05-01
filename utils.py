import json
import os
import time
import tempfile
import cv2
import numpy as np
import psutil
import gc

from constants import PROJECT_ROOT, LOGS_DIR, CONFIG_DIR, C

# =====================================================================
# FILE I/O - JSON
# =====================================================================

def save_json(path, data):
    """
    ⭐ Lưu JSON an toàn (atomic write)
    - Tạo file tạm
    - Ghi dữ liệu
    - Replace file gốc (tránh file hỏng nếu crash)
    
    Args:
        path: Đường dẫn file JSON
        data: Dữ liệu cần lưu (dict/list)
    
    Returns:
        True nếu thành công, False nếu thất bại
    """
    if not os.path.isabs(path):
        path = os.path.join(PROJECT_ROOT, path)

    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    try:
        temp_fd, temp_path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, path)
        return True
    except Exception as e:
        print(f"{C.R}❌ Lỗi save_json: {e}{C.X}")
        return False

def load_json(path, default=None):
    """
    ⭐ Đọc JSON an toàn
    
    Args:
        path: Đường dẫn file JSON
        default: Giá trị mặc định nếu file không tồn tại
    
    Returns:
        Dữ liệu từ JSON hoặc default value
    """
    if not os.path.isabs(path):
        path = os.path.join(PROJECT_ROOT, path)

    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"{C.R}❌ Lỗi load_json: {e}{C.X}")
    return default

# =====================================================================
# FRAME PROCESSING
# =====================================================================

def frame_hash(frame):
    """
    ⭐ Tính hash frame để kiểm tra thay đổi
    - Tránh xử lý frame trùng lặp
    - Giảm CPU/RAM
    
    Args:
        frame: Frame từ OCR
    
    Returns:
        Hash của frame (int)
    """
    try:
        small = cv2.resize(frame, (16, 16))
        return hash(small.tobytes()[:128])
    except:
        return None

# =====================================================================
# SYSTEM MONITORING
# =====================================================================

def get_ram():
    """
    ⭐ Lấy % RAM sử dụng
    
    Returns:
        Phần trăm RAM đang dùng (0-100)
    """
    try:
        return psutil.virtual_memory().percent
    except:
        return 0

def get_cpu():
    """
    ⭐ Lấy % CPU sử dụng
    
    Returns:
        Phần trăm CPU đang dùng (0-100)
    """
    try:
        return psutil.cpu_percent(interval=0.05)
    except:
        return 0

def cleanup_ram():
    """
    ⭐ Clear garbage collection
    - Giải phóng bộ nhớ không dùng
    """
    gc.collect()

def get_process_memory():
    """
    ⭐ Lấy memory của process hiện tại (MB)
    
    Returns:
        Dung lượng RAM hiện tại (MB)
    """
    try:
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except:
        return 0