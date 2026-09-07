import pandas as pd

def clean_and_prepare_data(df):
    """
    Chuẩn hóa kiểu dữ liệu cho DataFrame đầu vào.
    """
    cleaned = df.copy()
    
    # Ép kiểu dữ liệu số
    if 'Year' in cleaned.columns:
        cleaned['Year'] = pd.to_numeric(cleaned['Year'], errors='coerce').fillna(0).astype(int)
    if 'Sales' in cleaned.columns:
        cleaned['Sales'] = pd.to_numeric(cleaned['Sales'], errors='coerce').fillna(0.0)
    if 'Profit' in cleaned.columns:
        cleaned['Profit'] = pd.to_numeric(cleaned['Profit'], errors='coerce').fillna(0.0)
    if 'Shipping Cost' in cleaned.columns:
        cleaned['Shipping Cost'] = pd.to_numeric(cleaned['Shipping Cost'], errors='coerce').fillna(0.0)
    if 'Quantity' in cleaned.columns:
        cleaned['Quantity'] = pd.to_numeric(cleaned['Quantity'], errors='coerce').fillna(0).astype(int)

    return cleaned


def filter_data(df, year=None, region=None, segment=None, country=None):
    """
    Lọc DataFrame theo các tiêu chí: Năm, Thị trường (Market), Phân khúc (Segment), Quốc gia (Country).
    """
    filtered = df.copy()

    # 1. Lọc theo Năm
    if year and str(year).lower() != 'all':
        try:
            filtered = filtered[filtered['Year'] == int(year)]
        except (ValueError, TypeError):
            pass

    # 2. Lọc theo Khu vực / Thị trường (Cột Market trong CSV)
    if region and str(region).lower() != 'all':
        filtered = filtered[filtered['Market'] == region]

    # 3. Lọc theo Phân khúc khách hàng
    if segment and str(segment).lower() != 'all':
        filtered = filtered[filtered['Segment'] == segment]

    # 4. Lọc theo Quốc gia
    if country and str(country).lower() != 'all':
        filtered = filtered[filtered['Country'].str.lower() == str(country).lower()]

    return filtered