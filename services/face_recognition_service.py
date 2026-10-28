"""
FaceBox - Face Recognition Service
Nhận diện khuôn mặt dùng OpenCV built-in:
  - YuNet (face_detection_yunet_2023mar.onnx): Phát hiện khuôn mặt
  - SFace (face_recognition_sface_2021dec.onnx): Tạo embedding 128 chiều

Ưu điểm:
  - Không cần cài thêm thư viện nặng (InsightFace, ONNX Runtime riêng)
  - Chạy tốt trên CPU, hỗ trợ Python 3.15
  - Model chính thức từ OpenCV Model Zoo (Apache 2.0)

Nguồn model: https://github.com/opencv/opencv_zoo
Ngưỡng mặc định: cosine distance >= 0.363 (tài liệu SFace khuyến nghị)

CẢNH BÁO: Prototype - chưa có liveness detection.
Ảnh/video có thể đánh lừa hệ thống.
"""

import cv2
import numpy as np
import os
import logging
from typing import Optional, List, Tuple, Dict

logger = logging.getLogger(__name__)

# ---- Đường dẫn model ----
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_MODELS_DIR = os.path.join(_THIS_DIR, '..', 'models')

YUNET_PATH = os.path.join(_MODELS_DIR, 'face_detection_yunet_2023mar.onnx')
SFACE_PATH = os.path.join(_MODELS_DIR, 'face_recognition_sface_2021dec.onnx')

# ---- Ngưỡng nhận diện ----
# SFace dùng Cosine Similarity (cv2.FaceRecognizerSF.FR_COSINE):
#   - Phạm vi: -1.0 đến 1.0 (càng gần 1.0 càng giống nhau)
#   - Tài liệu OpenCV Model Zoo khuyến nghị: similarity >= 0.363 là cùng người
#   - Không nhầm lẫn giữa Cosine Similarity (lớn hơn = giống hơn) với Cosine Distance (nhỏ hơn = giống hơn)
DEFAULT_THRESHOLD = 0.363

# Số frame liên tiếp cùng kết quả để xác nhận
CONFIRMATION_FRAMES = 4


def calculate_confidence(similarity: float, threshold: float = DEFAULT_THRESHOLD) -> float:
    """
    Tính phần trăm độ tin cậy hiển thị trên giao diện (0.0 - 1.0) từ Cosine Similarity thực tế.
    
    Tách biệt rõ ràng 3 đại lượng:
      1. Cosine Similarity thực tế (đối với SFace, cùng người thường đạt 0.45 - 0.85).
      2. Ngưỡng xác nhận danh tính (threshold, mặc định 0.363).
      3. Phần trăm độ tin cậy giao diện (UI confidence %):
         - Dưới ngưỡng: 0.0 (chưa đạt)
         - Tại ngưỡng (0.363): 60% (đạt chuẩn xác nhận)
         - 0.50: ~73% (khớp tốt)
         - 0.65: ~86% (rất khớp)
         - 0.75: ~95% (khớp xuất sắc)
         - >= 0.80: 98% - 100%
    """
    if similarity < threshold:
        return 0.0

    target_high = 0.75
    if similarity >= target_high:
        extra = min(1.0, (similarity - target_high) / (1.0 - target_high))
        return min(1.0, 0.95 + 0.05 * extra)
    else:
        progress = (similarity - threshold) / (target_high - threshold)
        return 0.60 + 0.35 * progress


# Các hằng số hướng khuôn mặt (Head Pose)
POSE_STRAIGHT = "straight"   # Nhìn thẳng
POSE_LEFT     = "left"       # Quay trái (theo góc nhìn người dùng)
POSE_RIGHT    = "right"      # Quay phải (theo góc nhìn người dùng)
POSE_UP       = "up"         # Ngẩng mặt lên
POSE_DOWN     = "down"       # Cúi mặt xuống
POSE_UNKNOWN  = "unknown"    # Không xác định / góc trung gian


class FaceRecognitionService:
    """
    Service nhận diện khuôn mặt dùng OpenCV YuNet + SFace.
    
    Workflow:
    1. detect_faces(frame)   -> list các row YuNet khuôn mặt
    2. get_embedding(frame, face_box) -> vector 128 chiều đã chuẩn hóa L2
    3. find_match(embedding) -> so khớp Cosine Similarity với các mẫu đã lưu
    """

    def __init__(self):
        self._detector = None      # cv2.FaceDetectorYN (YuNet)
        self._recognizer = None    # cv2.FaceRecognizerSF (SFace)
        self._is_ready = False
        self._load_error: Optional[str] = None
        self._known_embeddings: List[dict] = []
        self._threshold = DEFAULT_THRESHOLD
        self._input_size = (320, 320)   # YuNet input size

    @staticmethod
    def estimate_head_pose(face_row: list) -> Tuple[str, float, float]:
        """
        Ước lượng hướng đầu (pose) dựa trên 5 điểm mốc khuôn mặt do YuNet trả về:
          face_row: [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt, x_rcm, y_rcm, x_lcm, y_lcm, score]

        Trả về:
          (pose_name, yaw_ratio, pitch_ratio)
          - yaw_ratio: ~0.50 khi nhìn thẳng; > 0.58 khi quay trái; < 0.42 khi quay phải (theo góc nhìn webcam)
          - pitch_ratio: ~0.52-0.74 khi thẳng; < 0.48 khi ngẩng lên; > 0.78 khi cúi xuống
        """
        if len(face_row) < 14:
            return POSE_UNKNOWN, 0.0, 0.0

        re_x, re_y = float(face_row[4]), float(face_row[5])
        le_x, le_y = float(face_row[6]), float(face_row[7])
        nose_x, nose_y = float(face_row[8]), float(face_row[9])
        rcm_x, rcm_y = float(face_row[10]), float(face_row[11])
        lcm_x, lcm_y = float(face_row[12]), float(face_row[13])

        eye_w = le_x - re_x
        if eye_w <= 8.0:
            return POSE_UNKNOWN, 0.0, 0.0

        # Tỷ lệ ngang: vị trí chóp mũi so với khoảng cách hai mắt
        yaw_ratio = (nose_x - re_x) / eye_w

        # Tỷ lệ dọc: khoảng cách từ đường mắt đến mũi so với từ đường mắt đến miệng
        eye_y = (re_y + le_y) / 2.0
        mouth_y = (rcm_y + lcm_y) / 2.0
        vert_span = mouth_y - eye_y
        if vert_span <= 8.0:
            return POSE_UNKNOWN, yaw_ratio, 0.0

        pitch_ratio = (nose_y - eye_y) / vert_span

        # Phân loại tư thế với ngưỡng tự nhiên, tránh xung đột vùng nhìn thẳng
        # Ưu tiên kiểm tra nhìn thẳng với dải dung sai thực tế trước
        if 0.38 <= yaw_ratio <= 0.62 and 0.46 <= pitch_ratio <= 0.78:
            return POSE_STRAIGHT, yaw_ratio, pitch_ratio
        elif pitch_ratio < 0.46 and 0.34 <= yaw_ratio <= 0.66:
            return POSE_UP, yaw_ratio, pitch_ratio
        elif pitch_ratio > 0.78 and 0.34 <= yaw_ratio <= 0.66:
            return POSE_DOWN, yaw_ratio, pitch_ratio
        elif yaw_ratio > 0.58:
            return POSE_LEFT, yaw_ratio, pitch_ratio
        elif yaw_ratio < 0.42:
            return POSE_RIGHT, yaw_ratio, pitch_ratio

        return POSE_UNKNOWN, yaw_ratio, pitch_ratio

    @staticmethod
    def check_pose_target(face_row: list, target_pose: str) -> Tuple[bool, str, float, float]:
        """
        Kiểm tra xem khuôn mặt hiện tại có đạt tư thế mục tiêu hay không,
        kèm thông báo hướng dẫn cụ thể và số đo yaw_ratio, pitch_ratio.

        Returns:
            (is_match, guide_message, yaw_ratio, pitch_ratio)
        """
        if len(face_row) < 14:
            return False, "Không đủ điểm mốc khuôn mặt", 0.0, 0.0

        re_x, re_y = float(face_row[4]), float(face_row[5])
        le_x, le_y = float(face_row[6]), float(face_row[7])
        nose_x, nose_y = float(face_row[8]), float(face_row[9])
        rcm_x, rcm_y = float(face_row[10]), float(face_row[11])
        lcm_x, lcm_y = float(face_row[12]), float(face_row[13])

        eye_w = le_x - re_x
        if eye_w <= 8.0:
            return False, "Khuôn mặt quá nhỏ hoặc góc nghiêng quá lớn", 0.0, 0.0

        yaw_ratio = (nose_x - re_x) / eye_w
        eye_y = (re_y + le_y) / 2.0
        mouth_y = (rcm_y + lcm_y) / 2.0
        vert_span = mouth_y - eye_y
        if vert_span <= 8.0:
            return False, "Khuôn mặt không rõ ràng", yaw_ratio, 0.0

        pitch_ratio = (nose_y - eye_y) / vert_span

        if target_pose == POSE_STRAIGHT:
            # Ngưỡng nhìn thẳng tự nhiên
            if yaw_ratio < 0.38:
                return False, "Bạn đang quay sang phải, hãy nhìn thẳng vào camera", yaw_ratio, pitch_ratio
            if yaw_ratio > 0.62:
                return False, "Bạn đang quay sang trái, hãy nhìn thẳng vào camera", yaw_ratio, pitch_ratio
            if pitch_ratio < 0.46:
                return False, "Bạn đang ngẩng mặt hơi cao, hãy nhìn thẳng vào camera", yaw_ratio, pitch_ratio
            if pitch_ratio > 0.80:
                return False, "Bạn đang cúi mặt hơi thấp, hãy nhìn thẳng vào camera", yaw_ratio, pitch_ratio
            return True, "Đúng hướng nhìn thẳng", yaw_ratio, pitch_ratio

        elif target_pose == POSE_LEFT:
            if yaw_ratio >= 0.58:
                return True, "Đúng hướng quay trái", yaw_ratio, pitch_ratio
            return False, "Vui lòng quay mặt nhẹ sang trái", yaw_ratio, pitch_ratio

        elif target_pose == POSE_RIGHT:
            if yaw_ratio <= 0.42:
                return True, "Đúng hướng quay phải", yaw_ratio, pitch_ratio
            return False, "Vui lòng quay mặt nhẹ sang phải", yaw_ratio, pitch_ratio

        elif target_pose == POSE_UP:
            if pitch_ratio <= 0.50:
                return True, "Đúng hướng ngẩng lên", yaw_ratio, pitch_ratio
            return False, "Vui lòng ngẩng mặt nhẹ lên", yaw_ratio, pitch_ratio

        elif target_pose == POSE_DOWN:
            if pitch_ratio >= 0.76:
                return True, "Đúng hướng cúi xuống", yaw_ratio, pitch_ratio
            return False, "Vui lòng cúi mặt nhẹ xuống", yaw_ratio, pitch_ratio

        return False, "Tư thế chưa xác định", yaw_ratio, pitch_ratio

    def initialize(self) -> Tuple[bool, str]:
        """
        Khởi tạo detector và recognizer.
        Gọi một lần khi app khởi động (chạy trong thread riêng).

        Returns:
            (success, message)
        """
        try:
            # Kiểm tra file model
            if not os.path.exists(YUNET_PATH):
                msg = (f"Không tìm thấy model YuNet:\n{YUNET_PATH}\n\n"
                       "Chạy: python models/download_models.py")
                self._load_error = msg
                return False, msg

            if not os.path.exists(SFACE_PATH):
                msg = (f"Không tìm thấy model SFace:\n{SFACE_PATH}\n\n"
                       "Chạy: python models/download_models.py")
                self._load_error = msg
                return False, msg

            logger.info(f"Đang tải YuNet detector từ: {YUNET_PATH}")
            self._detector = cv2.FaceDetectorYN.create(
                YUNET_PATH, "",
                self._input_size,
                score_threshold=0.6,
                nms_threshold=0.3,
                top_k=5
            )

            logger.info(f"Đang tải SFace recognizer từ: {SFACE_PATH}")
            self._recognizer = cv2.FaceRecognizerSF.create(SFACE_PATH, "")

            self._is_ready = True
            logger.info("Mô hình YuNet + SFace đã sẵn sàng hoạt động")
            return True, "Mô hình nhận diện đã sẵn sàng (YuNet + SFace)"

        except cv2.error as e:
            msg = f"Lỗi OpenCV khi tải mô hình: {str(e)}"
            self._load_error = msg
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Lỗi tải mô hình: {str(e)}"
            self._load_error = msg
            logger.error(msg)
            return False, msg

    def is_ready(self) -> bool:
        return self._is_ready

    def get_load_error(self) -> Optional[str]:
        return self._load_error

    def _resize_for_detector(self, frame: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Resize frame về kích thước phù hợp cho YuNet.
        Trả về (frame_resized, scale_factor).
        """
        h, w = frame.shape[:2]
        self._detector.setInputSize((w, h))
        return frame, 1.0

    def detect_faces(self, frame: np.ndarray) -> list:
        """
        Phát hiện khuôn mặt trong frame BGR.

        Returns:
            List các row YuNet: mỗi row là array [x, y, w, h, x_re, y_re, x_le, y_le,
                                                   x_nt, y_nt, x_rcm, y_rcm, x_lcm, y_lcm, score]
            Trả về [] nếu không phát hiện.
        """
        if not self._is_ready or self._detector is None:
            return []
        try:
            h, w = frame.shape[:2]
            self._detector.setInputSize((w, h))
            _, faces = self._detector.detect(frame)
            if faces is None:
                return []
            return faces.tolist()
        except Exception as e:
            logger.error(f"Lỗi phát hiện khuôn mặt: {e}")
            return []

    def check_face_quality(self, frame: np.ndarray, face_row: list) -> Tuple[bool, str]:
        """
        Kiểm tra chất lượng khuôn mặt để loại bỏ ảnh mờ, tối, hoặc không rõ ràng:
        - Điểm phát hiện YuNet
        - Kích thước khuôn mặt
        - Độ sáng trung bình vùng mặt
        - Độ sắc nét (Laplacian variance)
        """
        score = face_row[14] if len(face_row) > 14 else 0
        if score < 0.55:
            return False, f"Độ tin cậy phát hiện thấp ({score:.2f} < 0.55). Hãy nhìn rõ vào camera."

        x, y, w, h = int(face_row[0]), int(face_row[1]), int(face_row[2]), int(face_row[3])
        if w < 50 or h < 50:
            return False, f"Khuôn mặt quá nhỏ ({w}x{h}). Đứng gần camera hơn."

        h_frame, w_frame = frame.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(w_frame, x + w), min(h_frame, y + h)
        if x2 <= x1 or y2 <= y1:
            return False, "Vùng khuôn mặt nằm ngoài khung hình."

        face_crop = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)

        # 1. Kiểm tra độ sáng (dải rộng an toàn cho nhiều điều kiện phòng)
        brightness = float(np.mean(gray))
        if brightness < 25.0:
            return False, f"Khuôn mặt quá tối (độ sáng: {brightness:.0f}/255). Hãy tăng thêm ánh sáng."
        if brightness > 245.0:
            return False, f"Khuôn mặt quá sáng/chói (độ sáng: {brightness:.0f}/255). Tránh nguồn sáng chiếu thẳng camera."

        # 2. Kiểm tra độ sắc nét (phù hợp với webcam laptop 720p thông dụng)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if blur_score < 15.0:
            return False, f"Ảnh bị mờ hoặc rung lắc (độ nét: {blur_score:.0f}). Hãy giữ yên khuôn mặt."

        return True, "OK"

    def get_embedding(self, frame: np.ndarray, face_row: list) -> Optional[np.ndarray]:
        """
        Tính embedding từ một khuôn mặt đã phát hiện.
        Quy trình chuẩn: YuNet face_box -> SFace alignCrop -> SFace feature -> L2 Normalize.

        Args:
            frame: BGR frame gốc (không lật)
            face_row: Một row từ detect_faces() (15 phần tử)

        Returns:
            numpy float32 array 128 chiều (đã chuẩn hóa L2 norm = 1.0), hoặc None
        """
        if self._recognizer is None:
            return None
        try:
            face_arr = np.array(face_row, dtype=np.float32)
            # SFace align + feature extract
            aligned = self._recognizer.alignCrop(frame, face_arr)
            embedding = self._recognizer.feature(aligned)
            # embedding shape: (1, 128) -> flatten float32
            emb = embedding.flatten().astype(np.float32)
            # Chuẩn hóa L2 norm
            norm = np.linalg.norm(emb)
            if norm > 0:
                emb = emb / norm
            return emb
        except Exception as e:
            logger.error(f"Lỗi tính embedding: {e}")
            return None

    def get_embedding_from_frame(self, frame: np.ndarray, face_row: Optional[list] = None) -> Tuple[Optional[np.ndarray], str]:
        """
        Phát hiện khuôn mặt (nếu chưa có face_row), kiểm tra chất lượng và trích xuất embedding.

        Args:
            frame: Frame BGR gốc từ camera
            face_row: Tùy chọn. Nếu đã detect trước đó từ detect_faces, truyền vào để tránh tính toán lại.

        Returns:
            (embedding, message) - embedding=None nếu thất bại
        """
        if face_row is None:
            faces = self.detect_faces(frame)
            if len(faces) == 0:
                return None, "Không phát hiện khuôn mặt. Hãy nhìn thẳng vào camera."
            if len(faces) > 1:
                return None, "Phát hiện nhiều khuôn mặt. Chỉ để một người đứng trước camera."
            face = faces[0]
        else:
            if len(face_row) >= 14:
                face = face_row
            else:
                faces = self.detect_faces(frame)
                if not faces:
                    return None, "Không phát hiện khuôn mặt để trích xuất đặc trưng."
                face = max(faces, key=lambda f: f[2] * f[3])

        # Kiểm tra chất lượng khuôn mặt (ánh sáng, độ mờ, kích thước)
        is_quality_ok, quality_msg = self.check_face_quality(frame, face)
        if not is_quality_ok:
            return None, quality_msg

        embedding = self.get_embedding(frame, face)
        if embedding is None:
            return None, "Không thể trích xuất đặc trưng. Thử lại."

        return embedding, "OK"

    def load_known_embeddings(self, embeddings_data: List[dict]):
        """
        Nạp embedding từ DB vào bộ nhớ để nhận diện.

        Args:
            embeddings_data: Kết quả từ db_manager.get_all_face_embeddings()
        """
        self._known_embeddings = embeddings_data
        unique_accounts = set(d.get('account_id') for d in embeddings_data)
        logger.info(f"Đã nạp {len(embeddings_data)} profile embedding của {len(unique_accounts)} tài khoản vào bộ nhớ")
        if embeddings_data:
            sample_emb = embeddings_data[0]['embedding']
            logger.info(f"[Embedding Info] shape={sample_emb.shape}, dtype={sample_emb.dtype}, "
                        f"norm={np.linalg.norm(sample_emb):.4f}")

    def find_match(self, query_embedding: np.ndarray) -> Tuple[Optional[dict], float, float]:
        """
        Tìm khuôn mặt khớp nhất bằng Cosine Similarity (SFace FR_COSINE).

        Quy tắc:
          - SFace chuẩn: similarity trong khoảng [-1.0, 1.0]
          - Điểm càng lớn = càng giống nhau
          - Ngưỡng chuẩn OpenCV Model Zoo: similarity >= 0.363 là cùng người
          - Hỗ trợ so sánh với nhiều mẫu đã lưu của mỗi tài khoản (lấy max similarity)

        Returns:
            (best_match dict hoặc None, best_similarity, confidence_score)
        """
        if not self._known_embeddings:
            return None, -1.0, 0.0

        best_match = None
        best_similarity = -1.0

        for known in self._known_embeddings:
            known_emb = known['embedding']
            # Cosine similarity vì 2 vector đã chuẩn hóa L2: dot(a, b) = cos(theta)
            similarity = float(np.dot(query_embedding, known_emb))

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = known

        # So sánh với ngưỡng (similarity >= threshold => khớp)
        is_matched = (best_similarity >= self._threshold)
        confidence = calculate_confidence(best_similarity, self._threshold) if is_matched else 0.0

        if best_match:
            phone = best_match.get('phone_number')
            label = best_match.get('label')
            status_text = "KHỚP" if is_matched else "KHÔNG KHỚP (dưới ngưỡng)"
            logger.debug(f"[So khớp] {status_text} | SĐT: {phone} ({label}) | "
                         f"Cosine: {best_similarity:.4f} | Ngưỡng: {self._threshold:.4f} | "
                         f"Độ tin cậy: {confidence:.1%}")

        if is_matched:
            return best_match, best_similarity, confidence

        return None, best_similarity, 0.0

    def recognize_in_frame(self, frame: np.ndarray) -> List[dict]:
        """
        Nhận diện tất cả khuôn mặt trong frame.

        Returns:
            List dict chứa:
            - bbox: [x1, y1, x2, y2]
            - phone_number: str hoặc None
            - label: str
            - score: float (độ tin cậy 0.0 - 1.0 hiển thị trên UI)
            - similarity: float (Cosine Similarity thực tế)
            - det_score: float (điểm phát hiện YuNet)
            - identified: bool
        """
        if not self._is_ready:
            return []

        faces = self.detect_faces(frame)
        results = []

        for face in faces:
            x, y, w, h = int(face[0]), int(face[1]), int(face[2]), int(face[3])
            bbox = [x, y, x + w, y + h]
            det_score = face[14] if len(face) > 14 else 0

            embedding = self.get_embedding(frame, face)

            if embedding is not None and self._known_embeddings:
                match, similarity, confidence = self.find_match(embedding)
                if match:
                    results.append({
                        'bbox': bbox,
                        'phone_number': match['phone_number'],
                        'label': match.get('label', ''),
                        'account_id': match['account_id'],
                        'score': confidence,
                        'similarity': similarity,
                        'distance': 1.0 - similarity,   # Giữ tương thích nếu có nơi cần
                        'det_score': det_score,
                        'identified': True
                    })
                else:
                    results.append({
                        'bbox': bbox,
                        'phone_number': None,
                        'label': 'Chua xac dinh',
                        'account_id': None,
                        'score': 0.0,
                        'similarity': similarity,
                        'distance': 1.0 - similarity if similarity > -1.0 else 1.0,
                        'det_score': det_score,
                        'identified': False
                    })
            else:
                results.append({
                    'bbox': bbox,
                    'phone_number': None,
                    'label': 'Chua xac dinh',
                    'account_id': None,
                    'score': 0.0,
                    'similarity': -1.0,
                    'distance': 1.0,
                    'det_score': det_score,
                    'identified': False
                })

        return results

    def set_threshold(self, threshold: float):
        """
        Điều chỉnh ngưỡng nhận diện Cosine Similarity.
        Lớn hơn = nghiêm ngặt hơn (chuẩn OpenCV: 0.363).
        Phạm vi hợp lệ: 0.2 - 0.8
        """
        self._threshold = max(0.2, min(0.8, threshold))
        logger.info(f"Ngưỡng nhận diện (Cosine Similarity): {self._threshold:.4f}")


class RecognitionConfirmer:
    """
    Xác nhận kết quả nhận diện qua nhiều frame liên tiếp.
    Tránh kết quả nhấp nháy/bất ổn định.
    """
    def __init__(self, required_frames: int = CONFIRMATION_FRAMES):
        self.required_frames = required_frames
        self._counter: Dict[str, int] = {}

    def update(self, results: List[dict]) -> List[dict]:
        """
        Cập nhật counter và trả về kết quả đã xác nhận.
        """
        if not results:
            # Giảm dần counter khi không thấy khuôn mặt
            for k in list(self._counter.keys()):
                self._counter[k] = max(0, self._counter[k] - 2)
            return []

        confirmed = []
        current_phones = set()

        for r in results:
            if r['identified']:
                phone = r['phone_number']
                current_phones.add(phone)
                self._counter[phone] = self._counter.get(phone, 0) + 1
                if self._counter[phone] >= self.required_frames:
                    confirmed.append(r)

        # Giảm counter cho phone không xuất hiện frame này
        for phone in list(self._counter.keys()):
            if phone not in current_phones:
                self._counter[phone] = max(0, self._counter[phone] - 1)

        return confirmed if confirmed else results
