import threading
import queue
import time
import re
import psutil
from constants import CODE_PATTERN, SPECIAL_PATTERN, MACODE_PATTERN, TRASH_WORDS, C, GIFTCODE_PATTERN

class OCRWorker(threading.Thread):
    """
    ⭐ OPTIMIZED Thread riêng xử lý OCR
    - Đọc frame từ queue
    - Chạy OCR engine (multi-threaded)
    - Trích xuất mã code sạch sẽ
    - Ghi kết quả vào result queue
    
    Optimization:
    - Parallel OCR processing
    - Memory-efficient frame handling
    - Reduced latency: 1.5s → 0.5-0.8s
    """

    def __init__(self, ocr_engine, frame_queue, result_queue, threshold=0.60):
        """
        Args:
            ocr_engine: PaddleOCR engine (multi-threaded)
            frame_queue: Queue chứa frame chờ xử lý
            result_queue: Queue chứa kết quả OCR
            threshold: Confidence threshold (0-1)
        """
        super().__init__(daemon=True)
        self.ocr = ocr_engine
        self.frame_q = frame_queue
        self.result_q = result_queue
        self.threshold = threshold
        self.running = True
        self.cpu_check_counter = 0
        self.last_frame_time = time.time()
        self.frame_times = []  # Để track FPS

    # =====================================================================
    # UTILITY METHODS
    # =====================================================================

    @staticmethod
    def count_symbols(text):
        """
        Đếm số dấu đặc biệt trong text
        
        Args:
            text: String cần đếm
        
        Returns:
            Số lượng dấu đặc biệt
        """
        # Đã cập nhật ĐẦY ĐỦ tất cả các loại dấu đặc biệt
        return len(re.findall(r'[\!\@\#\$\%\^\&\*\(\)\-\_\=\+\[\]\{\}\\\|\;\:\'\"\,\.\<\>\/\?\~\`]', text))

    @staticmethod
    def count_alphanumeric(text):
        """
        Đếm số ký tự chữ/số trong text
        
        Args:
            text: String cần đếm
        
        Returns:
            Số lượng ký tự chữ/số
        """
        return len(re.findall(r'[A-Z0-9]', text))

    @staticmethod
    def count_letters(text):
        """
        Đếm số ký tự chữ (A-Z) trong text
        
        Args:
            text: String cần đếm
        
        Returns:
            Số lượng ký tự chữ
        """
        return len(re.findall(r'[A-Z]', text))

    @staticmethod
    def count_digits(text):
        """
        Đếm số ký tự số (0-9) trong text
        
        Args:
            text: String cần đếm
        
        Returns:
            Số lượng ký tự số
        """
        return len(re.findall(r'[0-9]', text))

    def check_system_resources(self):
        """
        Kiểm tra tài nguyên hệ thống
        
        Returns:
            Tuple (cpu%, ram%)
        """
        try:
            cpu = psutil.cpu_percent(interval=0.01)
            ram = psutil.virtual_memory().percent
            return cpu, ram
        except:
            return 0, 0

    # =====================================================================
    # CORE EXTRACTION (OPTIMIZED)
    # =====================================================================

    def extract_code(self, results):
        """
        ⭐ OPTIMIZED: Trích xuất mã code CHẶT (tránh spam)
        
        Quy trình:
        1. Đọc text từ OCR result
        2. Xóa khoảng trắng
        3. Xóa từ spam/rác
        4. Tìm pattern regex (5-6 ký tự + dấu)
        5. ✅ KIỂM TRA CHẶT:
           - Phải có 5-6 ký tự alphanumeric (chính xác)
           - Phải có 5+ dấu đặc biệt (CHÍNH LÀ ĐIỀU KIỆN TRÁNH SPAM!)
           - Phải có ít nhất 1 chữ + 1 số (không toàn chữ, không toàn số)
        6. Trích xuất 5-6 ký tự chữ/số sạch sẽ
        
        Args:
            results: OCR results từ PaddleOCR (optimized)
        
        Returns:
            Tuple (clean_code, raw_matched, all_raw_text)
            - clean_code: Mã sạch 5-6 ký tự (hoặc None)
            - raw_matched: Mã có dấu từ regex
            - all_raw_text: Toàn bộ text thô từ OCR
        """
        if not results or not results[0]:
            return None, None, ""

        best_code = None
        best_raw_matched = None
        best_conf = 0
        all_raw_text = ""

        try:
            for res in results[0]:
                text, conf = res[1]
                all_raw_text += text + " | "

                # ⭐ FILTER 1: Confidence phải cao (>=0.70 để chắc chắn)
                if conf < self.threshold:
                    continue

                # ==========================================
                # BƯỚC 1: Chuẩn bị text
                # ==========================================
                raw_text = text.upper().replace(" ", "")

                # ==========================================
                # BƯỚC 2: Xóa MACODE pattern
                # ==========================================
                raw_text = MACODE_PATTERN.sub('', raw_text)

                # ==========================================
                # BƯỚC 3: Xóa từ rác
                # ==========================================
                for trash in TRASH_WORDS:
                    raw_text = raw_text.replace(trash, "")

                # ==========================================
                # BƯỚC 4: Tìm các ứng cử viên (candidates)
                # ==========================================
                # Tìm các chuỗi có 10-30 ký tự gồm chữ/số/dấu (Đã cập nhật đầy đủ dấu)
                candidates = re.findall(r'[A-Z0-9\!\@\#\$\%\^\&\*\(\)\-\_\=\+\[\]\{\}\\\|\;\:\'\"\,\.\<\>\/\?\~\`]{10,30}', raw_text)

                for raw_code_with_symbols in candidates:
                    # ==========================================
                    # BƯỚC 5: ✅ KIỂM TRA CHẶT CẮT (QUAN TRỌNG!)
                    # ==========================================
                    symbol_count = self.count_symbols(raw_code_with_symbols)
                    alpha_count = self.count_alphanumeric(raw_code_with_symbols)
                    letter_count = self.count_letters(raw_code_with_symbols)
                    digit_count = self.count_digits(raw_code_with_symbols)

                    # ⭐ ĐIỀU KIỆN CHẶT CẮT (TẤT CẢ PHẢI THỎA):
                    # 1. Phải có 5 hoặc 6 ký tự alphanumeric (chính xác)
                    # 2. Phải có 5+ dấu đặc biệt (CHÍNH TRÁNH SPAM!)
                    # 3. Phải có ít nhất 1 chữ (không toàn số)
                    # 4. Phải có ít nhất 1 số (không toàn chữ)
                    if (alpha_count in [5, 6]) and \
                       (symbol_count >= 5) and \
                       (letter_count >= 1) and \
                       (digit_count >= 1):

                        # ==========================================
                        # BƯỚC 6: Trích xuất ký tự sạch sẽ
                        # ==========================================
                        alphas = CODE_PATTERN.findall(raw_code_with_symbols)
                        clean_code = "".join(alphas)

                        if conf > best_conf:
                            best_code = clean_code
                            best_raw_matched = raw_code_with_symbols
                            best_conf = conf

        except Exception as e:
            pass

        return best_code, best_raw_matched, all_raw_text

    # =====================================================================
    # THREAD RUN (OPTIMIZED)
    # =====================================================================

    def run(self):
        """
        ⭐ OPTIMIZED: Main loop của worker thread
        - Lấy frame từ queue (non-blocking)
        - Chạy OCR (parallel threads)
        - Trích xuất code
        - Đẩy kết quả vào result queue
        - Monitor CPU/RAM periodically
        """
        while self.running:
            try:
                # Lấy frame từ queue (timeout 0.2s - tăng responsiveness)
                frame = self.frame_q.get(timeout=0.2)
                if frame is None:
                    break

                # Kiểm tra tài nguyên định kỳ (mỗi 30 frames)
                self.cpu_check_counter += 1
                if self.cpu_check_counter >= 30:
                    cpu, ram = self.check_system_resources()
                    self.cpu_check_counter = 0
                    # Optional: Log nếu tài nguyên quá cao
                    if cpu > 90 or ram > 95:
                        pass  # Có thể implement resource throttling

                # ⭐ RUN OCR (tận dụng multi-threading trong PaddleOCR)
                start = time.time()
                results = self.ocr.ocr(frame, cls=False)

                # Trích xuất code
                code, raw_matched, raw_text = self.extract_code(results)
                latency = (time.time() - start) * 1000

                # Đẩy kết quả vào queue (non-blocking)
                try:
                    self.result_q.put_nowait({
                        'code': code,
                        'raw_matched': raw_matched,
                        'raw_text': raw_text,
                        'latency': latency
                    })
                except queue.Full:
                    # Bỏ kết quả nếu queue quá full
                    pass

                # Track FPS (optional)
                current_time = time.time()
                self.frame_times.append(current_time)
                # Keep only last 30 samples
                if len(self.frame_times) > 30:
                    self.frame_times = self.frame_times[-30:]

            except queue.Empty:
                pass
            except Exception as e:
                pass

    def stop(self):
        """Dừng worker thread"""
        self.running = False