import os
import sys
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# Đảm bảo đường dẫn import hoạt động chuẩn xác dù chạy từ bất kỳ thư mục nào
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from data_loader import load_data
from preprocessing import clean_and_prepare_data, filter_data
from features import (
    calculate_sales_by_country,
    calculate_top_products,
    calculate_category_breakdown,
    calculate_shipping_analysis,
    calculate_yearly_sales_by_country,
    calculate_monthly_growth_by_category
)

app = Flask(__name__, template_folder='../templates')
CORS(app)

# Nạp và chuẩn hóa dữ liệu khi server khởi động
raw_df = load_data()
df = clean_and_prepare_data(raw_df)


@app.route('/')
def index():
    return render_template('index.html')


# API 1: Phân bố Doanh thu & Lợi nhuận theo Quốc gia (Choropleth Map & KPI)
@app.route('/api/v1/sales-by-country', methods=['GET'])
def sales_by_country():
    year = request.args.get('year')
    region = request.args.get('region')
    segment = request.args.get('segment')

    filtered_df = filter_data(df, year=year, region=region, segment=segment)
    result = calculate_sales_by_country(filtered_df)
    return jsonify(result)


# API 2: Top Sản phẩm bán chạy nhất theo từng Quốc gia
@app.route('/api/v1/top-products-by-country', methods=['GET'])
def top_products_by_country():
    country = request.args.get('country', default='United States')
    top_n = int(request.args.get('top_n', default=5))
    year = request.args.get('year')
    segment = request.args.get('segment')

    filtered_df = filter_data(df, year=year, segment=segment, country=country)
    result = calculate_top_products(filtered_df, country=country, top_n=top_n)
    return jsonify(result)


# API 3: Phân tích Đơn hàng & Doanh số theo Danh mục hàng hóa
@app.route('/api/v1/orders-by-category', methods=['GET'])
def orders_by_category():
    year = request.args.get('year')
    region = request.args.get('region')
    segment = request.args.get('segment')

    filtered_df = filter_data(df, year=year, region=region, segment=segment)
    result = calculate_category_breakdown(filtered_df)
    return jsonify(result)


# API 4: Phân tích Chi phí Vận chuyển & Hình thức giao hàng
@app.route('/api/v1/shipping-analysis', methods=['GET'])
def shipping_analysis():
    year = request.args.get('year')
    region = request.args.get('region')
    segment = request.args.get('segment')

    filtered_df = filter_data(df, year=year, region=region, segment=segment)
    result = calculate_shipping_analysis(filtered_df)
    return jsonify(result)


# API 5: Phân tích Xu hướng Doanh thu (Theo Tháng) của các Quốc gia
@app.route('/api/v1/yearly-sales-by-country', methods=['GET'])
def yearly_sales_by_country():
    countries = request.args.get('countries')
    metric = request.args.get('metric', default='sales')
    segment = request.args.get('segment')
    period = request.args.get('period', default='year')
    start_month = request.args.get('start_month')
    end_month = request.args.get('end_month')

    filtered_df = filter_data(df, segment=segment)
    result = calculate_yearly_sales_by_country(
        filtered_df,
        countries=countries,
        metric=metric,
        period=period,
        start_month=start_month,
        end_month=end_month
    )
    return jsonify(result)


# API 6: Phân tích Xu hướng Doanh thu theo Tháng của Category & Sub-Category
@app.route('/api/v1/monthly-growth-by-category', methods=['GET'])
def monthly_growth_by_category():
    category = request.args.get('category', default='all')
    sub_category = request.args.get('sub_category', default='all')
    metric = request.args.get('metric', default='sales')
    start_month = request.args.get('start_month')
    end_month = request.args.get('end_month')
    region = request.args.get('region')
    segment = request.args.get('segment')

    result = calculate_monthly_growth_by_category(
        df,
        category=category,
        sub_category=sub_category,
        metric=metric,
        start_month=start_month,
        end_month=end_month,
        region=region,
        segment=segment
    )
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=8386)
