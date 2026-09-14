import pandas as pd

def calculate_sales_by_country(filtered_df, base_df=None, year=None, region=None, segment=None):
    """
    Tính toán số liệu KPI tổng quan và gom nhóm Doanh số / Lợi nhuận theo Quốc gia
    cho Choropleth Map, kèm các chỉ số KPI động (Margin, Shipping Ratio, YoY Growth, Quốc gia).
    """
    total_sales = round(float(filtered_df['Sales'].sum()), 2) if not filtered_df.empty else 0.0
    total_profit = round(float(filtered_df['Profit'].sum()), 2) if not filtered_df.empty else 0.0
    total_shipping = round(float(filtered_df['Shipping Cost'].sum()), 2) if not filtered_df.empty else 0.0
    total_orders = int(len(filtered_df))
    total_countries = int(filtered_df['Country'].nunique()) if not filtered_df.empty else 0
    profit_margin = round((total_profit / total_sales * 100), 1) if total_sales > 0 else 0.0
    shipping_ratio = round((total_shipping / total_sales * 100), 1) if total_sales > 0 else 0.0

    # Tính toán tăng trưởng YoY hoặc tăng trưởng chu kỳ
    yoy_growth = None
    yoy_label = "N/A"

    if base_df is not None and not base_df.empty:
        ref_df = base_df.copy()
        if region and str(region).lower() != 'all':
            ref_df = ref_df[ref_df['Market'] == region]
        if segment and str(segment).lower() != 'all':
            ref_df = ref_df[ref_df['Segment'] == segment]

        if year and str(year).lower() != 'all':
            try:
                curr_year = int(year)
                prev_year = curr_year - 1
                prev_df = ref_df[ref_df['Year'] == prev_year]
                if not prev_df.empty:
                    prev_sales = prev_df['Sales'].sum()
                    if prev_sales > 0:
                        growth = round(((total_sales - prev_sales) / prev_sales) * 100, 1)
                        yoy_growth = growth
                        yoy_label = f"{growth:+.1f}% YoY"
                    else:
                        yoy_label = "N/A"
                else:
                    yoy_label = "Năm cơ sở"
            except (ValueError, TypeError):
                yoy_label = "N/A"
        else:
            all_years = sorted(ref_df['Year'].dropna().unique().astype(int).tolist())
            if len(all_years) >= 2:
                s_start = ref_df[ref_df['Year'] == all_years[0]]['Sales'].sum()
                s_end = ref_df[ref_df['Year'] == all_years[-1]]['Sales'].sum()
                if s_start > 0:
                    overall_g = round(((s_end - s_start) / s_start) * 100, 1)
                    yoy_growth = overall_g
                    yoy_label = f"{overall_g:+.1f}% ({all_years[0]}-{all_years[-1]})"
                else:
                    yoy_label = "N/A"
            else:
                yoy_label = "Toàn thời gian"

    # 1. Tính KPI tổng hợp
    summary = {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_shipping": total_shipping,
        "total_orders": total_orders,
        "total_countries": total_countries,
        "profit_margin": profit_margin,
        "shipping_ratio": shipping_ratio,
        "yoy_growth": yoy_growth,
        "yoy_label": yoy_label,
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
    Phân tích chi phí vận chuyển & Doanh thu theo Hình thức giao hàng (Ship Mode).
    """
    if filtered_df.empty:
        return []

    grouped = (
        filtered_df.groupby('Ship Mode')
        .agg(
            total_sales=('Sales', 'sum'),
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
            "total_sales": round(float(row['total_sales']), 2),
            "total_shipping_cost": round(float(row['total_shipping_cost']), 2),
            "avg_shipping_cost": round(float(row['avg_shipping_cost']), 2),
            "order_count": int(row['order_count'])
        }
        for _, row in grouped.iterrows()
    ]


def calculate_yearly_sales_by_country(base_df, countries=None, metric='sales', period='year', start_month=None, end_month=None):
    """
    Tính toán chuỗi thời gian theo từng quốc gia theo Năm hoặc Tháng,
    hỗ trợ lọc khoảng tháng bắt đầu và kết thúc, tính tốc độ tăng trưởng (Growth Rate).
    """
    if base_df.empty:
        return {
            "period_type": period,
            "years": [],
            "periods": [],
            "metric": metric,
            "countries_data": []
        }

    metric_col = 'Sales' if str(metric).lower() == 'sales' else 'Profit'
    is_monthly = str(period).lower() == 'month'

    # Tạo cột Order Month dạng YYYY-MM
    df = base_df.copy()
    if 'Order Month' not in df.columns:
        if 'Order Date' in df.columns:
            df['Order Month'] = df['Order Date'].astype(str).str.slice(0, 7)
        else:
            df['Order Month'] = df['Year'].astype(str) + '-01'

    # Lọc theo khoảng tháng nếu có
    if start_month:
        df = df[df['Order Month'] >= str(start_month)]
    if end_month:
        df = df[df['Order Month'] <= str(end_month)]

    # Xác định danh sách quốc gia
    if countries:
        if isinstance(countries, str):
            target_countries = [c.strip() for c in countries.split(',') if c.strip()]
        else:
            target_countries = list(countries)
    else:
        target_countries = (
            df.groupby('Country')['Sales']
            .sum()
            .nlargest(5)
            .index
            .tolist()
        )

    countries_data = []

    if is_monthly:
        # Chu kỳ theo Tháng (Monthly)
        all_months = sorted(df['Order Month'].dropna().unique().tolist())

        for c in target_countries:
            c_df = df[df['Country'].str.lower() == c.lower()]
            monthly_map = c_df.groupby('Order Month')[metric_col].sum().to_dict()
            monthly_values = [round(float(monthly_map.get(m, 0.0)), 2) for m in all_months]
            total_val = round(float(sum(monthly_values)), 2)

            # Tính tăng trưởng từ tháng đầu đến tháng cuối
            if len(monthly_values) >= 2 and monthly_values[0] > 0:
                growth_pct = round(((monthly_values[-1] - monthly_values[0]) / monthly_values[0]) * 100, 2)
            else:
                growth_pct = 0.0

            countries_data.append({
                "country": c,
                "values": monthly_values,
                "yearly_values": monthly_values,  # Tương thích ngược
                "total": total_val,
                "growth_percent": growth_pct,
                "yoy_growth_percent": growth_pct  # Tương thích ngược
            })

        return {
            "period_type": "month",
            "periods": all_months,
            "years": all_months,  # Tương thích ngược
            "metric": metric,
            "countries_data": countries_data
        }
    else:
        # Chu kỳ theo Năm (Yearly)
        years = sorted(df['Year'].dropna().unique().astype(int).tolist())

        for c in target_countries:
            c_df = df[df['Country'].str.lower() == c.lower()]
            yearly_map = c_df.groupby('Year')[metric_col].sum().to_dict()
            yearly_values = [round(float(yearly_map.get(y, 0.0)), 2) for y in years]
            total_val = round(float(sum(yearly_values)), 2)

            # Tính tăng trưởng từ năm đầu đến năm cuối
            if len(yearly_values) >= 2 and yearly_values[0] > 0:
                growth_pct = round(((yearly_values[-1] - yearly_values[0]) / yearly_values[0]) * 100, 2)
            else:
                growth_pct = 0.0

            countries_data.append({
                "country": c,
                "values": yearly_values,
                "yearly_values": yearly_values,
                "total": total_val,
                "growth_percent": growth_pct,
                "yoy_growth_percent": growth_pct
            })

        return {
            "period_type": "year",
            "periods": [str(y) for y in years],
            "years": years,
            "metric": metric,
            "countries_data": countries_data
        }


def calculate_monthly_growth_by_category(base_df, category='all', sub_category='all', metric='sales', start_month=None, end_month=None, region=None, segment=None):
    """
    Tính toán chuỗi thời gian doanh thu / lợi nhuận theo từng tháng (MoM)
    theo Category và Sub-Category, kèm tốc độ tăng trưởng liên tháng (% MoM Growth Rate).
    """
    if base_df.empty:
        return {
            'months': [],
            'metric': metric,
            'selected_category': category,
            'selected_subcategory': sub_category,
            'total_trend': {},
            'category_trends': [],
            'subcategory_trends': [],
            'all_subcategory_trends': [],
            'summary_kpis': {}
        }

    subcat_col = 'Sub Category' if 'Sub Category' in base_df.columns else 'Sub-Category'
    metric_col = 'Sales' if str(metric).lower() == 'sales' else ('Profit' if str(metric).lower() == 'profit' else 'Quantity')

    df = base_df.copy()
    if 'Order Month' not in df.columns:
        if 'Order Date' in df.columns:
            df['Order Month'] = df['Order Date'].astype(str).str.slice(0, 7)
        else:
            df['Order Month'] = df['Year'].astype(str) + '-01'

    # Áp dụng bộ lọc toàn cục
    if region and region != 'all':
        df = df[df['Market'].str.lower() == region.lower()]
    if segment and segment != 'all':
        df = df[df['Segment'].str.lower() == segment.lower()]
    if start_month:
        df = df[df['Order Month'] >= str(start_month)]
    if end_month:
        df = df[df['Order Month'] <= str(end_month)]

    all_months = sorted(df['Order Month'].dropna().unique().tolist())
    if not all_months:
        return {
            'months': [],
            'metric': metric,
            'selected_category': category,
            'selected_subcategory': sub_category,
            'total_trend': {},
            'category_trends': [],
            'subcategory_trends': [],
            'all_subcategory_trends': [],
            'summary_kpis': {}
        }

    # Hàm trợ giúp tính chuỗi giá trị và tốc độ tăng trưởng liên tháng (MoM)
    def compute_series(sub_df):
        m_map = sub_df.groupby('Order Month')[metric_col].sum().to_dict()
        vals = [round(float(m_map.get(m, 0.0)), 2) for m in all_months]
        growths = []
        for i in range(len(vals)):
            if i == 0 or vals[i - 1] == 0:
                growths.append(None)
            else:
                g = round(((vals[i] - vals[i - 1]) / vals[i - 1]) * 100, 2)
                growths.append(g)
        tot = round(float(sum(vals)), 2)
        ov_g = round(((vals[-1] - vals[0]) / vals[0]) * 100, 2) if len(vals) >= 2 and vals[0] > 0 else 0.0
        return vals, growths, tot, ov_g

    # Chuỗi dữ liệu của mục tiêu được chọn (Category / Sub-Category)
    target_df = df.copy()
    if category and category != 'all':
        target_df = target_df[target_df['Category'].str.lower() == category.lower()]
    if sub_category and sub_category != 'all':
        target_df = target_df[target_df[subcat_col].str.lower() == sub_category.lower()]

    tot_vals, tot_growths, tot_sum, tot_ov_g = compute_series(target_df)

    # Chuỗi dữ liệu cho 3 Category chính
    cat_trends = []
    for cat in ['Technology', 'Furniture', 'Office Supplies']:
        c_df = df[df['Category'].str.lower() == cat.lower()]
        c_vals, c_growths, c_tot, c_ov_g = compute_series(c_df)
        cat_trends.append({
            'category': cat,
            'values': c_vals,
            'growth_rates': c_growths,
            'total': c_tot,
            'overall_growth': c_ov_g
        })

    # Chuỗi dữ liệu cho các Sub-Category
    all_subcats = sorted(df[subcat_col].dropna().unique().tolist())
    subcat_trends = []
    for sc in all_subcats:
        sc_df = df[df[subcat_col].str.lower() == sc.lower()]
        sc_cat = sc_df['Category'].iloc[0] if not sc_df.empty else ''
        sc_vals, sc_growths, sc_tot, sc_ov_g = compute_series(sc_df)
        subcat_trends.append({
            'category': sc_cat,
            'sub_category': sc,
            'values': sc_vals,
            'growth_rates': sc_growths,
            'total': sc_tot,
            'overall_growth': sc_ov_g
        })

    # Lọc danh sách Sub-Category theo Category đã chọn (nếu có)
    filtered_subcat_trends = [
        s for s in subcat_trends
        if category == 'all' or s['category'].lower() == category.lower()
    ]

    # Tính toán các chỉ số KPI tóm tắt
    latest_val = tot_vals[-1] if tot_vals else 0.0
    latest_growth = tot_growths[-1] if tot_growths and tot_growths[-1] is not None else 0.0
    avg_val = round(tot_sum / len(all_months), 2) if all_months else 0.0

    max_idx = tot_vals.index(max(tot_vals)) if tot_vals else 0
    peak_month = all_months[max_idx] if all_months else 'N/A'
    peak_val = tot_vals[max_idx] if tot_vals else 0.0

    fastest_sub = max(filtered_subcat_trends or subcat_trends, key=lambda s: s['overall_growth']) if (filtered_subcat_trends or subcat_trends) else {}
    top_sub = max(filtered_subcat_trends or subcat_trends, key=lambda s: s['total']) if (filtered_subcat_trends or subcat_trends) else {}

    summary_kpis = {
        'latest_month': all_months[-1] if all_months else 'N/A',
        'latest_value': latest_val,
        'latest_growth': latest_growth,
        'avg_monthly_value': avg_val,
        'peak_month': peak_month,
        'peak_value': peak_val,
        'total_value': tot_sum,
        'overall_growth': tot_ov_g,
        'fastest_subcategory': {
            'name': fastest_sub.get('sub_category', 'N/A'),
            'category': fastest_sub.get('category', ''),
            'growth': fastest_sub.get('overall_growth', 0.0)
        },
        'top_subcategory': {
            'name': top_sub.get('sub_category', 'N/A'),
            'category': top_sub.get('category', ''),
            'total': top_sub.get('total', 0.0)
        }
    }

    return {
        'months': all_months,
        'metric': metric,
        'selected_category': category,
        'selected_subcategory': sub_category,
        'total_trend': {
            'values': tot_vals,
            'growth_rates': tot_growths,
            'total': tot_sum,
            'overall_growth': tot_ov_g
        },
        'category_trends': cat_trends,
        'subcategory_trends': filtered_subcat_trends,
        'all_subcategory_trends': subcat_trends,
        'summary_kpis': summary_kpis
    }


