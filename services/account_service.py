"""
FaceBox - Account Service
Xử lý logic nghiệp vụ cho tài khoản và số điện thoại.
"""
import re
import logging
from typing import Tuple, Optional
from database import db_manager

logger = logging.getLogger(__name__)

# Regex kiểm tra số điện thoại Việt Nam
PHONE_REGEX = re.compile(r'^(0|\+84)(3[2-9]|5[25689]|7[06-9]|8[0-9]|9[0-9])[0-9]{7}$')


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Kiểm tra định dạng số điện thoại Việt Nam.
    
    Hỗ trợ: 0xxxxxxxxx, +84xxxxxxxxx
    
    Returns:
        Tuple (is_valid, message)
    """
    phone = phone.strip().replace(' ', '').replace('-', '')
    
    if not phone:
        return False, "Số điện thoại không được để trống"
    
    if not PHONE_REGEX.match(phone):
        return False, ("Số điện thoại không hợp lệ.\n"
                      "Ví dụ hợp lệ: 0912345678, +84912345678\n"
                      "Hỗ trợ các đầu số: 03x, 05x, 07x, 08x, 09x")
    
    return True, phone  # Trả về số đã chuẩn hóa


def get_or_create_account(phone_number: str) -> Tuple[bool, str, Optional[int], bool]:
    """
    Lấy tài khoản hiện có hoặc tạo mới.
    
    Returns:
        Tuple (success, message, account_id, is_new)
    """
    # Validate số điện thoại
    is_valid, result = validate_phone(phone_number)
    if not is_valid:
        return False, result, None, False
    
    normalized_phone = result
    
    # Kiểm tra tài khoản đã tồn tại
    existing = db_manager.get_account_by_phone(normalized_phone)
    if existing:
        return True, f"Tài khoản {normalized_phone} đã tồn tại", existing['id'], False
    
    # Tạo tài khoản mới
    success, msg, account_id = db_manager.create_account(normalized_phone)
    return success, msg, account_id, True
