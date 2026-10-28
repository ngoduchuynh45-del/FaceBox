"""
Test script kiểm tra toàn diện hệ thống nhận diện khuôn mặt FaceBox:
1. Kiểm tra đọc/ghi SQLite database và tính toàn vẹn dữ liệu
2. Kiểm tra tính toán Cosine Similarity và công thức confidence
3. Kiểm tra độ ổn định trước và sau khi khởi động lại (restart simulation)
4. Kiểm tra phân biệt giữa người thật và người khác
5. Kiểm tra hàm lọc chất lượng khuôn mặt (check_face_quality)
"""
import os
import sys
import numpy as np
import cv2

# Thêm đường dẫn FaceBox
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
from services.face_recognition_service import (
    FaceRecognitionService,
    calculate_confidence,
    DEFAULT_THRESHOLD
)

def run_tests():
    print("=" * 60)
    print("BẮT ĐẦU KIỂM THỬ HỆ THỐNG FACEBOX")
    print("=" * 60)
    
    # -------------------------------------------------------------
    # TEST 1: Database & Persistence
    # -------------------------------------------------------------
    print("\n--- TEST 1: Kiểm tra Database và Đường dẫn ---")
    db_path = db_manager.get_db_path()
    print(f"1.1 Đường dẫn DB: {db_path}")
    assert os.path.exists(db_path), f"File database không tồn tại: {db_path}"
    
    embeddings = db_manager.get_all_face_embeddings()
    print(f"1.2 Số lượng profile tải từ DB: {len(embeddings)}")
    assert len(embeddings) > 0, "Không có embedding nào trong DB!"
    
    for idx, e in enumerate(embeddings):
        emb = e['embedding']
        norm = np.linalg.norm(emb)
        print(f"    Profile {idx+1}: SĐT={e['phone_number']}, Nhãn='{e['label']}', shape={emb.shape}, dtype={emb.dtype}, norm={norm:.4f}")
        assert emb.shape == (128,), f"Shape không hợp lệ: {emb.shape}"
        assert emb.dtype == np.float32, f"Dtype không hợp lệ: {emb.dtype}"
        assert abs(norm - 1.0) < 1e-4, f"Norm không xấp xỉ 1.0: {norm}"
    print(">>> TEST 1 THÀNH CÔNG: Dữ liệu DB chuẩn hóa float32 (128,) và L2 norm = 1.0.")

    # -------------------------------------------------------------
    # TEST 2: Cosine Similarity & Confidence Formula
    # -------------------------------------------------------------
    print("\n--- TEST 2: Kiểm tra công thức Cosine Similarity & Confidence ---")
    print(f"2.1 Ngưỡng mặc định: {DEFAULT_THRESHOLD} (chuẩn OpenCV SFace)")
    
    # Kiểm tra các mốc confidence
    conf_below = calculate_confidence(0.30, DEFAULT_THRESHOLD)
    conf_at = calculate_confidence(DEFAULT_THRESHOLD, DEFAULT_THRESHOLD)
    conf_mid = calculate_confidence(0.50, DEFAULT_THRESHOLD)
    conf_good = calculate_confidence(0.65, DEFAULT_THRESHOLD)
    conf_high = calculate_confidence(0.75, DEFAULT_THRESHOLD)
    conf_max = calculate_confidence(0.85, DEFAULT_THRESHOLD)
    
    print(f"    - Sim=0.300 (< thresh): Confidence = {conf_below:.1%} (kỳ vọng: 0%)")
    print(f"    - Sim=0.363 (= thresh): Confidence = {conf_at:.1%} (kỳ vọng: 60.0%)")
    print(f"    - Sim=0.500: Confidence = {conf_mid:.1%} (kỳ vọng: ~72.4%)")
    print(f"    - Sim=0.650: Confidence = {conf_good:.1%} (kỳ vọng: ~85.9%)")
    print(f"    - Sim=0.750: Confidence = {conf_high:.1%} (kỳ vọng: 95.0%)")
    print(f"    - Sim=0.850: Confidence = {conf_max:.1%} (kỳ vọng: 97.0%)")
    
    assert conf_below == 0.0
    assert abs(conf_at - 0.60) < 1e-3
    assert 0.70 < conf_mid < 0.75
    assert 0.84 < conf_good < 0.88
    assert abs(conf_high - 0.95) < 1e-3
    assert conf_max >= 0.96
    print(">>> TEST 2 THÀNH CÔNG: Công thức confidence tách biệt đúng giữa điểm Cosine và % hiển thị.")

    # -------------------------------------------------------------
    # TEST 3: Model Initialization & SFace Match Verification
    # -------------------------------------------------------------
    print("\n--- TEST 3: Khởi tạo mô hình YuNet + SFace ---")
    service1 = FaceRecognitionService()
    ok, msg = service1.initialize()
    print(f"3.1 Khởi tạo service 1: {ok} - {msg}")
    assert ok, f"Khởi tạo service thất bại: {msg}"
    
    service1.load_known_embeddings(embeddings)
    
    # Lấy embedding của User 1
    u1_orig = embeddings[0]['embedding']
    u1_phone = embeddings[0]['phone_number']
    
    # So khớp chính nó
    match, sim, conf = service1.find_match(u1_orig)
    print(f"3.2 So khớp chính nó: phone={match['phone_number']}, sim={sim:.4f}, conf={conf:.1%}")
    assert match['phone_number'] == u1_phone
    assert abs(sim - 1.0) < 1e-4
    assert conf >= 0.99
    
    # So khớp User 1 với User 2
    u2_orig = embeddings[1]['embedding']
    u2_phone = embeddings[1]['phone_number']
    cross_sim = float(np.dot(u1_orig, u2_orig))
    print(f"3.3 Độ tương đồng giữa 2 người khác nhau ({u1_phone} vs {u2_phone}): {cross_sim:.4f}")
    assert cross_sim < DEFAULT_THRESHOLD, f"Hai người khác nhau lại có similarity >= ngưỡng: {cross_sim}"
    print(">>> TEST 3 THÀNH CÔNG: Mô hình phân biệt chính xác hai người khác nhau.")

    # -------------------------------------------------------------
    # TEST 4: Mô phỏng hành vi TRƯỚC và SAU KHI RESTART
    # -------------------------------------------------------------
    print("\n--- TEST 4: Kiểm tra tính nhất quán Trước vs Sau khi Restart ---")
    
    # Tạo một biến thể khuôn mặt thực tế của User 1 có Cosine Similarity = 0.6800
    np.random.seed(42)
    rand_v = np.random.randn(128).astype(np.float32)
    # Trực giao hóa với u1_orig
    ortho = rand_v - np.dot(rand_v, u1_orig) * u1_orig
    ortho = ortho / np.linalg.norm(ortho)
    target_sim = 0.68
    u1_variant = (target_sim * u1_orig + np.sqrt(1.0 - target_sim**2, dtype=np.float32) * ortho).astype(np.float32)
    sim_test = float(np.dot(u1_orig, u1_variant))
    print(f"4.1 Mẫu test biến thể của User 1: Cosine Similarity thực tế = {sim_test:.4f}")
    assert abs(sim_test - target_sim) < 1e-4, f"Biến thể sim ngoài khoảng kỳ vọng: {sim_test}"
    
    # Trước restart (service1):
    match_before, sim_before, conf_before = service1.find_match(u1_variant)
    print(f"4.2 TRƯỚC restart: phone={match_before['phone_number']}, sim={sim_before:.4f}, conf={conf_before:.1%}")
    assert match_before['phone_number'] == u1_phone
    assert conf_before >= 0.80, f"Confidence quá thấp trước restart: {conf_before}"
    
    # MÔ PHỎNG RESTART: giải phóng service1, tạo service2 mới hoàn toàn
    del service1
    service2 = FaceRecognitionService()
    service2.initialize()
    # Nạp lại từ database như khi khởi động app
    embeddings_reloaded = db_manager.get_all_face_embeddings()
    service2.load_known_embeddings(embeddings_reloaded)
    
    # Sau restart (service2):
    match_after, sim_after, conf_after = service2.find_match(u1_variant)
    print(f"4.3 SAU restart:   phone={match_after['phone_number']}, sim={sim_after:.4f}, conf={conf_after:.1%}")
    assert match_after['phone_number'] == u1_phone
    assert abs(sim_before - sim_after) < 1e-5, f"Similarity thay đổi sau restart: {sim_before} vs {sim_after}"
    assert abs(conf_before - conf_after) < 1e-5, f"Confidence thay đổi sau restart: {conf_before} vs {conf_after}"
    print(f">>> TEST 4 THÀNH CÔNG: Độ nhận diện trước và sau restart hoàn toàn ĐỒNG NHẤT ({conf_before:.1%} == {conf_after:.1%}), KHÔNG còn bị tụt xuống 20-30%!")

    # -------------------------------------------------------------
    # TEST 5: Kiểm tra chất lượng khuôn mặt (check_face_quality)
    # -------------------------------------------------------------
    print("\n--- TEST 5: Kiểm tra bộ lọc chất lượng khuôn mặt ---")
    # 1. Ảnh bình thường
    dummy_good = np.ones((480, 640, 3), dtype=np.uint8) * 120
    # Thêm chi tiết khuôn mặt
    cv2.circle(dummy_good, (200, 200), 40, (180, 180, 180), -1)
    for i in range(10):
        cv2.line(dummy_good, (170, 170 + i*5), (230, 170 + i*5), (40, 40, 40), 1)
    good_face_row = [160, 160, 80, 80] + [0]*10 + [0.85]
    ok_q, msg_q = service2.check_face_quality(dummy_good, good_face_row)
    print(f"5.1 Ảnh rõ nét, đủ sáng: ok={ok_q}, msg='{msg_q}'")
    assert ok_q, f"Ảnh tốt bị từ chối: {msg_q}"
    
    # 2. Ảnh quá tối
    dummy_dark = np.ones((480, 640, 3), dtype=np.uint8) * 20
    ok_dark, msg_dark = service2.check_face_quality(dummy_dark, good_face_row)
    print(f"5.2 Ảnh quá tối: ok={ok_dark}, msg='{msg_dark}'")
    assert not ok_dark and "tối" in msg_dark
    
    # 3. Ảnh bị mờ hoàn toàn (blur)
    dummy_blur = np.ones((480, 640, 3), dtype=np.uint8) * 120  # trơn hoàn toàn, không có cạnh
    ok_blur, msg_blur = service2.check_face_quality(dummy_blur, good_face_row)
    print(f"5.3 Ảnh mờ/không nét: ok={ok_blur}, msg='{msg_blur}'")
    assert not ok_blur and ("mờ" in msg_blur or "nét" in msg_blur)
    
    # 4. Khuôn mặt quá nhỏ
    small_face_row = [100, 100, 40, 40] + [0]*10 + [0.85]
    ok_small, msg_small = service2.check_face_quality(dummy_good, small_face_row)
    print(f"5.4 Khuôn mặt quá nhỏ: ok={ok_small}, msg='{msg_small}'")
    assert not ok_small and "nhỏ" in msg_small
    print(">>> TEST 5 THÀNH CÔNG: Bộ lọc đã phát hiện và loại bỏ chính xác các ảnh tối, mờ và quá nhỏ.")

    print("\n" + "=" * 60)
    print("TẤT CẢ 5 BỘ KIỂM THỬ ĐÃ VƯỢT QUA 100% THÀNH CÔNG!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
