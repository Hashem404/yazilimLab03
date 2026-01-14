"""
Validators - Doğrulama yardımcı fonksiyonları
"""

import os
import re
from typing import Optional


def validate_file_path(path: str, extension: str) -> bool:
    if not path:
        return False
    
    if not path.lower().endswith(f'.{extension.lower()}'):
        return False
    
    if '..' in path or path.startswith('/') or ':' in path[1:]:
        filename = os.path.basename(path)
        if filename != path:
            return False
    
    invalid_chars = r'[<>:"|?*\x00-\x1f]'
    if re.search(invalid_chars, path):
        return False
    
    return True


def validate_email(email: str) -> bool:
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    if not phone:
        return True 
    
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    return re.match(r'^\+?[0-9]{10,15}$', cleaned) is not None


def validate_date_format(date_str: str, format: str = '%Y-%m-%d') -> bool:
    if not date_str:
        return False
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_password_strength(password: str) -> tuple:
    if not password:
        return False, "Şifre gereklidir"
    
    if len(password) < 8:
        return False, "Şifre en az 8 karakter olmalıdır"
    
    if not re.search(r'[A-Z]', password):
        return False, "Şifrede en az bir büyük harf olmalıdır"
    
    if not re.search(r'[a-z]', password):
        return False, "Şifrede en az bir küçük harf olmalıdır"
    
    if not re.search(r'[0-9]', password):
        return False, "Şifrede en az bir rakam olmalıdır"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Şifrede en az bir özel karakter olmalıdır"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    invalid_chars = r'[<>:"|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    sanitized = re.sub(r'_+', '_', sanitized)
    
    sanitized = sanitized.strip('_')
    
    if not sanitized:
        sanitized = "dosya"
    
    return sanitized


def validate_required_fields(data: dict, required_fields: list) -> tuple:
    missing = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing.append(field)
    
    return (len(missing) == 0, missing)


def validate_range(value: any, min_val: Optional[any] = None, 
                   max_val: Optional[any] = None) -> bool:
    try:
        value = float(value)
        
        if min_val is not None and value < float(min_val):
            return False
        
        if max_val is not None and value > float(max_val):
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def validate_turkish_identity_number(tckn: str) -> bool:
    if not tckn or len(tckn) != 11:
        return False
    
    if not tckn.isdigit():
        return False
    
    if tckn[0] == '0':
        return False
    
    try:
        digits = [int(d) for d in tckn]
        
        sum1 = sum(digits[i] for i in range(9)) % 10
        if sum1 != digits[9]:
            return False
        
        sum2 = sum(digits[i] for i in range(10)) % 10
        if sum2 != digits[10]:
            return False
        
        return True
    except:
        return False


def is_positive_integer(value: any) -> bool:
    try:
        num = int(value)
        return num > 0
    except (ValueError, TypeError):
        return False


def is_valid_url(url: str) -> bool:
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// veya https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None
