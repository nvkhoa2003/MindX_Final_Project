import os
import pandas as pd

# Đường dẫn gốc của dự án
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'clean_superstore.csv')

def load_data(file_path=None):
    """
    Đọc dữ liệu từ file clean_superstore.csv.
    Nếu file không tồn tại, trả về ngoại lệ FileNotFoundError với thông báo rõ ràng.
    """
    path = file_path or CSV_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu tại đường dẫn: {path}")
    
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        raise RuntimeError(f"Lỗi khi đọc file dữ liệu: {str(e)}")