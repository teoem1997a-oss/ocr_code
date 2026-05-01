import re
import os

# ✅ FIX: PROJECT_ROOT chính xác
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")

# 🗑️ TRASH WORDS - Từ spam/rác cần loại bỏ
TRASH_WORDS = [
    "CHINHAP", "CHUCAI", "VASO", "6SONHA", "SONHA", "6SO",
    "MACODE", "LIXI", "FREE", "NHAPMA", "MM88", "RR88",
    "GG88", "XX88", "DAPAN", "CHAOMUNG", "MEGA", "LIVE",
    "KHUYENMAI", "DIEMDANH", "MM88MEGA", "LINK", "MADUTHUONG", "TONGTHANG"
]

# =====================================================================
# REGEX PATTERNS
# =====================================================================

# Bắt ký tự chữ/số (A-Z, 0-9)
CODE_PATTERN = re.compile(r'[A-Z0-9]')

# Bắt dấu đặc biệt
SPECIAL_PATTERN = re.compile(
    r'[\!\@\#\$\%\^\&\*\(\)\-\_\=\+\[\]\{\}\\\|\;\:\'\"\,\.\<\>\/\?\~\`]'
)

# Bắt từ "MACODE" (với các biến thể)
MACODE_PATTERN = re.compile(r'M?[AÃ]?CODE:?', re.IGNORECASE)

# ⭐ PATTERN CHÍNH: Bắt 5-6 ký tự chữ/số + xen kẽ 5+ dấu đặc biệt
# 
# ĐIỀU KIỆN CHẶT (Tránh spam):
#   1. Phải có 5-6 ký tự alphanumeric (chính xác)
#   2. Phải có 5+ dấu đặc biệt xen kẽ (CHÍNH YẾU TRÁNH SPAM!)
#   3. Phải có ít nhất 1 chữ + 1 số (không toàn chữ, không toàn số)
#
# Ví dụ PASS:
#   - T+5=K$X%T^3!   (5 ký tự T,5,K,X,T,3 + 5 dấu +,=,$,%,^,! + chữ + số) ✅
#   - A!B@C#1$2%     (5 ký tự A,B,C,1,2 + 5 dấu !,@,#,$,% + chữ + số) ✅
#   - T+5=K$X%T^3!!  (6 ký tự + 6 dấu) ✅
#
# Ví dụ FAIL:
#   - ABC123         (6 ký tự + 0 dấu) ❌
#   - ABCDEF         (6 ký tự + 0 dấu, toàn chữ) ❌
#   - 123456         (6 ký tự + 0 dấu, toàn số) ❌
#   - T+5=K          (5 ký tự + 2 dấu, không đủ 5 dấu) ❌
GIFTCODE_PATTERN = re.compile(
    r'[!@#$%^&*()_\-+=]*(?:[A-Z0-9][!@#$%^&*()_\-+=]+){5,6}[!@#$%^&*()_\-+=]*'
)

# =====================================================================
# COLORS (ANSI) - Cho console output
# =====================================================================
class C:
    G = '\033[92m'  # Green
    Y = '\033[93m'  # Yellow
    R = '\033[91m'  # Red
    C = '\033[96m'  # Cyan
    B = '\033[1m'   # Bold
    X = '\033[0m'   # Reset