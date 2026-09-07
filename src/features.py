import pandas as pd

def calculate_sales_by_country(filtered_df):
    """
    Tính toán số liệu KPI tổng quan và gom nhóm Doanh số / Lợi nhuận theo Quốc gia
    cho Choropleth Map.
    """
    # 1. Tính KPI tổng hợp
    summary = {
        "total_sales": round(float(filtered_df['Sales'].sum()), 2) if not filtered_df.empty else 0.0,
        "total_profit": round(float(filtered_df['Profit'].sum()), 2) if not filtered_df.empty else 0.0,
        "total_shipping": round(float(filtered_df['Shipping Cost'].sum()), 2) if not filtered_df.empty else 0.0,
        "total_orders": int(len(filtered_df)),
    }

    if filtered_df.empty:
        return {"summary": summary, "country_data": []}

    # 2. Gom nhóm theo Quốc gia
    grouped = (
        filtered_df.groupby('Country')
        .agg(
            sales=('Sales', 'sum'),
            profit=('Profit', 'sum'),
            order_count=('Country', 'count')
        )
        .reset_index()
    )

    grouped['sales'] = grouped['sales'].round(2)
    grouped['profit'] = grouped['profit'].round(2)
    grouped = grouped.sort_values(by='sales', ascending=False)

    country_data = [
        {
            "country": row['Country'],
            "sales": float(row['sales']),
            "profit": float(row['profit']),
            "order_count": int(row['order_count'])
        }
        for _, row in grouped.iterrows()
    ]

    return {
        "summary": summary,
        "country_data": country_data
    }


def calculate_top_products(filtered_df, country='United States', top_n=5):
    """
    Tìm Top N sản phẩm có doanh số cao nhất tại một Quốc gia cụ thể.
    """
    if filtered_df.empty:
        return {
            "country": country,
            "top_n": top_n,
            "top_products": []
        }

    grouped = (
        filtered_df.groupby(['Product Name', 'Category'])
        .agg(
            sales=('Sales', 'sum'),
            quantity=('Quantity', 'sum'),
            profit=('Profit', 'sum')
        )
        .reset_index()
    )

    grouped = grouped.sort_values(by='sales', ascending=False).head(top_n)

    top_products = [
        {
            "product_name": row['Product Name'],
            "category": row['Category'],
            "sales": round(float(row['sales']), 2),
            "quantity": int(row['quantity']),
            "profit": round(float(row['profit']), 2)
        }
        for _, row in grouped.iterrows()
    ]

    return {
        "country": country,
        "top_n": top_n,
        "top_products": top_products
    }


def calculate_category_breakdown(filtered_df):
    """
    Tính toán cơ cấu Doanh số, Lợi nhuận và Số đơn theo Danh mục hàng hóa (Category).
    """
    if filtered_df.empty:
        return []

    grouped = (
        filtered_df.groupby('Category')
        .agg(
            sales=('Sales', 'sum'),
            order_count=('Category', 'count'),
            profit=('Profit', 'sum')
        )
        .reset_index()
    )

    grouped = grouped.sort_values(by='sales', ascending=False)

    return [
        {
            "category": row['Category'],
            "sales": round(float(row['sales']), 2),
            "order_count": int(row['order_count']),
            "profit": round(float(row['profit']), 2)
        }
        for _, row in grouped.iterrows()
    ]


def calculate_shipping_analysis(filtered_df):
    """
    Phân tích chi phí vận chuyển theo Hình thức giao hàng (Ship Mode).
    """
    if filtered_df.empty:
        return []

    grouped = (
        filtered_df.groupby('Ship Mode')
        .agg(
            total_shipping_cost=('Shipping Cost', 'sum'),
            avg_shipping_cost=('Shipping Cost', 'mean'),
            order_count=('Ship Mode', 'count')
        )
        .reset_index()
    )

    grouped = grouped.sort_values(by='total_shipping_cost', ascending=False)

    return [
        {
            "ship_mode": row['Ship Mode'],
            "total_shipping_cost": round(float(row['total_shipping_cost']), 2),
            "avg_shipping_cost": round(float(row['avg_shipping_cost']), 2),
            "order_count": int(row['order_count'])
        }
        for _, row in grouped.iterrows()
    ]


def calculate_yearly_sales_by_country(base_df, countries=None, metric='sales'):
    """
    Tính toán chuỗi thời gian (time-series theo năm 2011 - 2014) theo từng quốc gia
    và tính tốc độ tăng trưởng liên năm (YoY Growth Rate).
    """
    metric_col = 'Sales' if str(metric).lower() == 'sales' else 'Profit'

    # Xác định danh sách quốc gia
    if countries:
        if isinstance(countries, str):
            target_countries = [c.strip() for c in countries.split(',') if c.strip()]
        else:
            target_countries = list(countries)
    else:
        target_countries = (
            base_df.groupby('Country')['Sales']
            .sum()
            .nlargest(5)
            .index
            .tolist()
        )

    # Lấy danh sách các năm
    years = sorted(base_df['Year'].dropna().unique().astype(int).tolist())

    countries_data = []
    for c in target_countries:
        c_df = base_df[base_df['Country'].str.lower() == c.lower()]
        yearly_map = c_df.groupby('Year')[metric_col].sum().to_dict()
        yearly_values = [round(float(yearly_map.get(y, 0.0)), 2) for y in years]
        total_val = round(float(sum(yearly_values)), 2)

        # Tính tăng trưởng từ năm đầu đến năm cuối
        if yearly_values and yearly_values[0] > 0:
            growth_pct = round(((yearly_values[-1] - yearly_values[0]) / yearly_values[0]) * 100, 2)
        else:
            growth_pct = 0.0

        countries_data.append({
            "country": c,
            "yearly_values": yearly_values,
            "total": total_val,
            "yoy_growth_percent": growth_pct
        })

    return {
        "years": years,
        "metric": metric,
        "countries_data": countries_data
    }
