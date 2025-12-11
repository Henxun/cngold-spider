from flask import Flask, render_template
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from currency_exchange import converter
import time
import json

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 配置应用
app.config['DEBUG'] = True

# 模拟贵金属数据（实际项目中应该从API获取）
# 这里使用模拟数据是因为没有提供实际的API密钥
mock_metal_data = {
    'gold': {
        'name': '黄金',
        'symbol': 'XAU/CNY',
        'price': 2035.45,
        'change': 12.30,
        'change_percent': 0.61,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    'silver': {
        'name': '白银',
        'symbol': 'XAG/CNY',
        'price': 24.56,
        'change': -0.12,
        'change_percent': -0.49,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    'platinum': {
        'name': '铂金',
        'symbol': 'XPT/USD',
        'price': 987.25,
        'change': 5.60,
        'change_percent': 0.57,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    'palladium': {
        'name': '钯金',
        'symbol': 'XPD/USD',
        'price': 1234.80,
        'change': -8.45,
        'change_percent': -0.68,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
}

currency_client = converter.CurrencyConverter()

def convert_currency(amount, to_currency):
    from_currency = 'USD'
    return currency_client.convert(float(amount), from_currency, to_currency)

def ounce_to_gram(ounce):
    """
    将美式盎司转换为克。
    
    参数:
    ounce (float): 盎司值
    
    返回:
    float: 转换后的克值
    """
    return ounce * 28.3495

# 获取贵金属数据的函数
def get_metal_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36",
        "Content-Type": "text/html;charset=UTF-8",
        "authority": "api.jijinhao.com",
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not=A?Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "document",
        "referer": "https://quote.cngold.org/gjs/gjhj.html",
    }
    response = requests.request("GET", f"https://api.jijinhao.com/quoteCenter/realTime.htm?codes=JO_92233,JO_92232,JO_92229,JO_92230,JO_92231,JO_38495&_={time.time_ns() // 1000000}",
            headers=headers, data={})

    data = response.text.replace("var quote_json = ", "")
    json_dict = json.loads(data)
    result = []
    
    rate = currency_client.get_exchange_rate('USD', 'CNY')
    for key, value in json_dict.items():
        if not key.startswith("JO_"):
            continue

        code = value["showCode"]
        name = value["showName"]
        price = value["q63"]
        price = price * rate
        weight = ounce_to_gram(1)
        price_per_gram = price / weight
        print(f"{name}\t{price_per_gram:.2f}")
        result.append({
            'name': name,
            'price': f"{price_per_gram:.2f}",
            'symbol': f"{code}/CNY",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    return result


# 主页路由
@app.route('/')
def index():
    metal_data = get_metal_data()
    return render_template('index.html', metals=metal_data)


if __name__ == '__main__':
    app.run(debug=True)
