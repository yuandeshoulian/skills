#!/usr/bin/env python3
"""
股票数据采集脚本（增强版）
采集基础行情、历史K线、技术指标、财务数据、资金流向、业绩数据
支持市值分析、长期趋势分析、历史规律挖掘
支持多数据源（腾讯财经为主，同花顺备用）
"""

import argparse
import json
import sys
from datetime import datetime, date

import akshare as ak
import numpy as np
import pandas as pd
import requests


def get_realtime_quote_ths(stock_code: str) -> dict:
    """从同花顺获取实时行情（备用数据源）"""
    try:
        # 同花顺实时行情接口
        url = f"https://qt.10jqka.com.cn/api/public/index.php"
        params = {
            "module": "stock",
            "controller": "quote",
            "method": "realtime",
            "code": stock_code
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://stockpage.10jqka.com.cn/'
        }
        r = requests.get(url, params=params, headers=headers, timeout=10)

        if r.status_code != 200:
            return {"error": f"同花顺请求失败: {r.status_code}"}

        data = r.json()
        if data.get('status') != 0 or 'data' not in data:
            return {"error": "无法解析同花顺数据"}

        quote = data['data']

        # 解析字段
        name = quote.get('name', '')
        price = float(quote.get('current', 0))
        pre_close = float(quote.get('close_yest', 0))
        open_price = float(quote.get('open', 0))
        high = float(quote.get('high', 0))
        low = float(quote.get('low', 0))
        volume = float(quote.get('volume', 0))
        amount = float(quote.get('amount', 0))
        turnover_rate = float(quote.get('turnover_rate', 0))

        change_amount = price - pre_close if pre_close > 0 else 0
        change_percent = (change_amount / pre_close * 100) if pre_close > 0 else 0

        # 市值
        market_cap = float(quote.get('total_market_value', 0))
        circulating_cap = float(quote.get('circulation_market_value', 0))

        cap_analysis = classify_market_cap(market_cap)

        return {
            "code": stock_code,
            "name": name,
            "price": price,
            "change_percent": round(change_percent, 2),
            "change_amount": round(change_amount, 2),
            "volume": volume,
            "turnover_rate": turnover_rate,
            "high": high,
            "low": low,
            "open": open_price,
            "pre_close": pre_close,
            "amount": amount,
            "market_cap": market_cap,
            "circulating_cap": circulating_cap,
            "market_cap_analysis": cap_analysis,
            "data_source": "同花顺（备用）"
        }
    except Exception as e:
        return {"error": str(e)}


def get_realtime_quote_tencent(stock_code: str) -> dict:
    """从腾讯财经获取实时行情（包含市值和财务数据）"""
    try:
        # 确定市场前缀
        if stock_code.startswith('6'):
            full_code = f"sh{stock_code}"
        else:
            full_code = f"sz{stock_code}"

        url = f'https://web.sqt.gtimg.cn/q={full_code}'
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return {"error": f"腾讯财经请求失败: {r.status_code}"}

        # 解析数据
        parts = r.text.split('="')
        if len(parts) < 2:
            return {"error": "无法解析腾讯财经数据"}

        data = parts[1].strip('";').split('~')

        if len(data) < 60:
            return {"error": "数据不完整"}

        # 解析字段
        name = data[1]
        code = data[2]
        price = float(data[3]) if data[3] else 0
        pre_close = float(data[4]) if data[4] else 0
        open_price = float(data[5]) if data[5] else 0
        volume = float(data[6]) if data[6] else 0
        high = float(data[33]) if len(data) > 33 and data[33] else 0
        low = float(data[34]) if len(data) > 34 and data[34] else 0
        change_percent = float(data[32]) if len(data) > 32 and data[32] else 0
        change_amount = float(data[31]) if len(data) > 31 and data[31] else 0
        amount = float(data[37]) * 10000 if len(data) > 37 and data[37] else 0  # 转为元
        turnover_rate = float(data[38]) if len(data) > 38 and data[38] else 0

        # 市值（亿）
        market_cap_yi = float(data[44]) if len(data) > 44 and data[44] else 0
        circulating_cap_yi = float(data[45]) if len(data) > 45 and data[45] else 0
        market_cap = market_cap_yi * 100000000  # 转为元

        # 财务指标
        pe_ttm = float(data[39]) if len(data) > 39 and data[39] else None
        # 腾讯财经PB字段位置不固定，暂不使用
        pb = None
        roe = float(data[52]) if len(data) > 52 and data[52] else None
        gross_margin = float(data[53]) if len(data) > 53 and data[53] else None

        # 市值分类
        cap_analysis = classify_market_cap(market_cap)

        return {
            "code": code,
            "name": name,
            "price": price,
            "change_percent": change_percent,
            "change_amount": change_amount,
            "volume": volume * 100,  # 手转股
            "turnover_rate": turnover_rate,
            "high": high,
            "low": low,
            "open": open_price,
            "pre_close": pre_close,
            "amount": amount,
            "market_cap": market_cap,
            "circulating_cap": circulating_cap_yi * 100000000,
            "market_cap_analysis": cap_analysis,
            "financial": {
                "pe_ttm": pe_ttm,
                "pb": pb,
                "roe": roe,
                "gross_margin": gross_margin
            },
            "data_source": "腾讯财经"
        }
    except Exception as e:
        return {"error": str(e)}


class DateTimeEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理日期和时间类型"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.strftime('%Y-%m-%d') if isinstance(obj, date) and not isinstance(obj, datetime) else obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if pd.isna(obj):
            return None
        return super().default(obj)


def classify_market_cap(market_cap: float) -> dict:
    """
    根据市值分类股票规模
    market_cap: 总市值（元）
    """
    # 转换为亿元
    cap_yi = market_cap / 100000000 if market_cap else 0

    if cap_yi < 50:
        return {
            "category": "小市值",
            "cap_yi": round(cap_yi, 2),
            "risk_level": "高",
            "risk_note": "小市值股票易受主力资金操控，技术指标可能失效，需结合资金流向和消息面综合判断，注意防范拉升出货风险"
        }
    elif cap_yi < 200:
        return {
            "category": "中小市值",
            "cap_yi": round(cap_yi, 2),
            "risk_level": "中高",
            "risk_note": "中小市值股票波动较大，需关注主力资金动向和散户情绪，技术分析结合基本面使用"
        }
    elif cap_yi < 500:
        return {
            "category": "中等市值",
            "cap_yi": round(cap_yi, 2),
            "risk_level": "中",
            "risk_note": "中等市值股票相对均衡，技术指标有效性较好"
        }
    elif cap_yi < 2000:
        return {
            "category": "大市值",
            "cap_yi": round(cap_yi, 2),
            "risk_level": "中低",
            "risk_note": "大市值股票走势相对稳定，技术指标有效性较高，更需关注基本面和行业趋势"
        }
    else:
        return {
            "category": "超大盘",
            "cap_yi": round(cap_yi, 2),
            "risk_level": "低",
            "risk_note": "超大盘股票走势稳定，主要受宏观经济和行业基本面影响，技术分析可作为辅助参考"
        }


def get_realtime_quote(stock_code: str) -> dict:
    """获取实时行情数据（腾讯为主，同花顺备用）"""
    # 先尝试腾讯财经
    tencent_result = get_realtime_quote_tencent(stock_code)
    if 'error' not in tencent_result or not tencent_result.get('error'):
        return tencent_result

    print(f"腾讯财经获取失败: {tencent_result.get('error', '未知错误')}，尝试同花顺...", file=sys.stderr)
    # 使用同花顺备用
    return get_realtime_quote_ths(stock_code)


def get_kline_data(stock_code: str, days: int = 120) -> dict:
    """获取历史K线数据并计算技术指标（腾讯为主，同花顺备用）"""
    # 先尝试腾讯财经
    try:
        result = get_kline_data_tencent(stock_code, days)
        if 'error' not in result or not result.get('error'):
            return result
        print(f"腾讯K线获取失败: {result.get('error', '未知错误')}，尝试同花顺...", file=sys.stderr)
    except Exception as e:
        print(f"腾讯K线获取失败: {e}，尝试同花顺...", file=sys.stderr)

    # 使用同花顺备用
    return get_kline_data_ths(stock_code, days)


def get_kline_data_tencent(stock_code: str, days: int = 120) -> dict:
    """从腾讯财经获取历史K线数据（主数据源）- 直接调用API"""
    try:
        # 添加股票代码前缀
        if stock_code.startswith('6'):
            prefix = 'sh'
        else:
            prefix = 'sz'
        full_code = f"{prefix}{stock_code}"

        # 直接调用腾讯财经API
        url = f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var_kline=kline&param={full_code},day,,,{days + 50},qfq"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://gu.qq.com/'
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        # 解析K线数据
        kline_raw = data.get('data', {}).get(full_code, {}).get('qfqday', [])
        if not kline_raw:
            return {"error": "未获取到K线数据"}

        # 只取前6列（日期、开、收、高、低、量），忽略第7列分红信息
        clean_data = [row[:6] for row in kline_raw]

        df = pd.DataFrame(clean_data, columns=['date', 'open', 'close', 'high', 'low', 'volume'])
        df['date'] = pd.to_datetime(df['date'])
        for col in ['open', 'close', 'high', 'low', 'volume']:
            df[col] = pd.to_numeric(df[col])

        # 取最近N天
        df = df.tail(days)

        if df.empty:
            return {"error": "未获取到K线数据"}

        # 取最近N天
        df = df.tail(days)

        # 重命名列
        df = df.rename(columns={
            'date': 'date',
            'open': 'open',
            'close': 'close',
            'high': 'high',
            'low': 'low',
            'volume': 'volume'
        })

        # 确保必要的列存在
        required_cols = ['date', 'open', 'close', 'high', 'low', 'volume']
        for col in required_cols:
            if col not in df.columns:
                return {"error": f"缺少必要列: {col}"}

        # 计算技术指标
        df = calculate_indicators(df)

        # 将日期列转换为字符串
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)

        # 获取最新指标值
        latest = df.iloc[-1] if len(df) > 0 else {}

        return {
            "kline": df.to_dict('records'),
            "kline_recent": df.tail(30).to_dict('records'),
            "indicators": {
                "MA5": float(latest.get('MA5', 0)) if pd.notna(latest.get('MA5')) else None,
                "MA10": float(latest.get('MA10', 0)) if pd.notna(latest.get('MA10')) else None,
                "MA20": float(latest.get('MA20', 0)) if pd.notna(latest.get('MA20')) else None,
                "MA60": float(latest.get('MA60', 0)) if pd.notna(latest.get('MA60')) else None,
                "MA120": float(latest.get('MA120', 0)) if pd.notna(latest.get('MA120')) else None,
                "MACD": {
                    "DIF": float(latest.get('MACD_12_26_9', 0)) if pd.notna(latest.get('MACD_12_26_9')) else None,
                    "DEA": float(latest.get('MACDs_12_26_9', 0)) if pd.notna(latest.get('MACDs_12_26_9')) else None,
                    "MACD": float(latest.get('MACDh_12_26_9', 0)) if pd.notna(latest.get('MACDh_12_26_9')) else None,
                },
                "KDJ": {
                    "K": float(latest.get('K_9_3', 0)) if pd.notna(latest.get('K_9_3')) else None,
                    "D": float(latest.get('D_9_3', 0)) if pd.notna(latest.get('D_9_3')) else None,
                    "J": float(latest.get('J_9_3', 0)) if pd.notna(latest.get('J_9_3')) else None,
                },
                "RSI": float(latest.get('RSI_14', 0)) if pd.notna(latest.get('RSI_14')) else None,
                "BOLL": {
                    "upper": float(latest.get('BBU_20_2.0', 0)) if pd.notna(latest.get('BBU_20_2.0')) else None,
                    "middle": float(latest.get('BBM_20_2.0', 0)) if pd.notna(latest.get('BBM_20_2.0')) else None,
                    "lower": float(latest.get('BBL_20_2.0', 0)) if pd.notna(latest.get('BBL_20_2.0')) else None,
                }
            },
            "trend_analysis": analyze_trend(df),
            "pattern_analysis": analyze_patterns(df),
            "history_stats": analyze_history_stats(df),
            "data_source": "腾讯财经"
        }
    except Exception as e:
        return {"error": str(e)}


def get_kline_data_ths(stock_code: str, days: int = 120) -> dict:
    """从同花顺获取历史K线数据（备用数据源）"""
    try:
        # 同花顺历史K线接口
        url = f"https://d.10jqka.com.cn/v6/line/hs_{stock_code}/01/last.js"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://stockpage.10jqka.com.cn/'
        }

        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return {"error": f"同花顺请求失败: {r.status_code}"}

        # 解析JSON数据
        data_str = r.text
        if not data_str:
            return {"error": "未获取到K线数据"}

        # 移除JSONP包装
        if data_str.startswith('load'):
            json_str = data_str[data_str.index('(') + 1:data_str.rindex(')')]
            data = json.loads(json_str)
        else:
            data = json.loads(data_str)

        # 解析K线数据
        kline_data = data.get('data', [])
        if not kline_data:
            return {"error": "数据为空"}

        # 转换为DataFrame
        records = []
        for item in kline_data[-days:]:  # 只取最近N天
            records.append({
                'date': item[0] if isinstance(item, list) else item.get('d', ''),
                'open': float(item[1]) if isinstance(item, list) else float(item.get('o', 0)),
                'close': float(item[2]) if isinstance(item, list) else float(item.get('c', 0)),
                'high': float(item[3]) if isinstance(item, list) else float(item.get('h', 0)),
                'low': float(item[4]) if isinstance(item, list) else float(item.get('l', 0)),
                'volume': float(item[5]) if isinstance(item, list) else float(item.get('v', 0)),
            })

        df = pd.DataFrame(records)

        if df.empty:
            return {"error": "数据解析失败"}

        # 计算技术指标
        df = calculate_indicators(df)

        # 获取最新指标值
        latest = df.iloc[-1] if len(df) > 0 else {}

        return {
            "kline": df.to_dict('records'),
            "kline_recent": df.tail(30).to_dict('records'),
            "indicators": {
                "MA5": float(latest.get('MA5', 0)) if pd.notna(latest.get('MA5')) else None,
                "MA10": float(latest.get('MA10', 0)) if pd.notna(latest.get('MA10')) else None,
                "MA20": float(latest.get('MA20', 0)) if pd.notna(latest.get('MA20')) else None,
                "MA60": float(latest.get('MA60', 0)) if pd.notna(latest.get('MA60')) else None,
                "MA120": None,  # 备用数据源数据较少
                "MACD": {
                    "DIF": float(latest.get('MACD_12_26_9', 0)) if pd.notna(latest.get('MACD_12_26_9')) else None,
                    "DEA": float(latest.get('MACDs_12_26_9', 0)) if pd.notna(latest.get('MACDs_12_26_9')) else None,
                    "MACD": float(latest.get('MACDh_12_26_9', 0)) if pd.notna(latest.get('MACDh_12_26_9')) else None,
                },
                "KDJ": {
                    "K": float(latest.get('K_9_3', 0)) if pd.notna(latest.get('K_9_3')) else None,
                    "D": float(latest.get('D_9_3', 0)) if pd.notna(latest.get('D_9_3')) else None,
                    "J": float(latest.get('J_9_3', 0)) if pd.notna(latest.get('J_9_3')) else None,
                },
                "RSI": float(latest.get('RSI_14', 0)) if pd.notna(latest.get('RSI_14')) else None,
                "BOLL": {
                    "upper": float(latest.get('BBU_20_2.0', 0)) if pd.notna(latest.get('BBU_20_2.0')) else None,
                    "middle": float(latest.get('BBM_20_2.0', 0)) if pd.notna(latest.get('BBM_20_2.0')) else None,
                    "lower": float(latest.get('BBL_20_2.0', 0)) if pd.notna(latest.get('BBL_20_2.0')) else None,
                }
            },
            "trend_analysis": analyze_trend(df),
            "pattern_analysis": {"patterns": [], "note": "备用数据源，形态分析不可用"},
            "history_stats": analyze_history_stats(df),
            "data_source": "同花顺（备用）"
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算技术指标（使用纯pandas/numpy实现）"""
    try:
        close = df['close']
        high = df['high']
        low = df['low']

        # 移动平均线 - 增加MA120
        df['MA5'] = close.rolling(window=5).mean()
        df['MA10'] = close.rolling(window=10).mean()
        df['MA20'] = close.rolling(window=20).mean()
        df['MA60'] = close.rolling(window=60).mean()
        df['MA120'] = close.rolling(window=120).mean()

        # MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        df['MACD_12_26_9'] = ema12 - ema26
        df['MACDs_12_26_9'] = df['MACD_12_26_9'].ewm(span=9, adjust=False).mean()
        df['MACDh_12_26_9'] = (df['MACD_12_26_9'] - df['MACDs_12_26_9']) * 2

        # KDJ指标
        low_9 = low.rolling(window=9).min()
        high_9 = high.rolling(window=9).max()
        rsv = (close - low_9) / (high_9 - low_9) * 100
        rsv = rsv.fillna(50)
        df['K_9_3'] = rsv.ewm(com=2, adjust=False).mean()
        df['D_9_3'] = df['K_9_3'].ewm(com=2, adjust=False).mean()
        df['J_9_3'] = 3 * df['K_9_3'] - 2 * df['D_9_3']

        # RSI(14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI_14'] = 100 - (100 / (1 + rs))

        # 布林带
        df['BBM_20_2.0'] = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        df['BBU_20_2.0'] = df['BBM_20_2.0'] + 2 * std_20
        df['BBL_20_2.0'] = df['BBM_20_2.0'] - 2 * std_20

        return df
    except Exception as e:
        print(f"计算技术指标时出错: {e}", file=sys.stderr)
        return df


def analyze_trend(df: pd.DataFrame) -> dict:
    """分析趋势（增强版）"""
    if len(df) < 20:
        return {"trend": "unknown", "description": "数据不足"}

    try:
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # 均线趋势判断
        ma5 = latest.get('MA5', 0)
        ma10 = latest.get('MA10', 0)
        ma20 = latest.get('MA20', 0)
        ma60 = latest.get('MA60', 0)
        ma120 = latest.get('MA120', 0)
        close = latest.get('close', 0)

        # 均线多头/空头排列
        if ma5 > ma10 > ma20 > ma60 and (pd.isna(ma120) or ma60 > ma120):
            ma_trend = "强多头排列"
        elif ma5 > ma10 > ma20:
            ma_trend = "多头排列"
        elif ma5 < ma10 < ma20 < ma60 and (pd.isna(ma120) or ma60 < ma120):
            ma_trend = "强空头排列"
        elif ma5 < ma10 < ma20:
            ma_trend = "空头排列"
        else:
            ma_trend = "均线交织"

        # MACD趋势
        macd_hist = latest.get('MACDh_12_26_9', 0)
        prev_macd_hist = prev.get('MACDh_12_26_9', 0)
        if pd.notna(macd_hist) and pd.notna(prev_macd_hist):
            if macd_hist > 0 and prev_macd_hist <= 0:
                macd_signal = "金叉"
            elif macd_hist < 0 and prev_macd_hist >= 0:
                macd_signal = "死叉"
            elif macd_hist > 0:
                macd_signal = "红柱"
            else:
                macd_signal = "绿柱"
        else:
            macd_signal = "未知"

        # KDJ位置
        k_value = latest.get('K_9_3', 50)
        if pd.notna(k_value):
            if k_value > 80:
                kdj_status = "超买"
            elif k_value < 20:
                kdj_status = "超卖"
            else:
                kdj_status = "正常"
        else:
            kdj_status = "未知"

        # RSI位置
        rsi = latest.get('RSI_14', 50)
        if pd.notna(rsi):
            if rsi > 70:
                rsi_status = "超买"
            elif rsi < 30:
                rsi_status = "超卖"
            else:
                rsi_status = "正常"
        else:
            rsi_status = "未知"

        # 综合趋势判断
        bullish_signals = 0
        bearish_signals = 0

        if "多头" in ma_trend:
            bullish_signals += 2
        elif "空头" in ma_trend:
            bearish_signals += 2

        if macd_signal in ["金叉", "红柱"]:
            bullish_signals += 1
        elif macd_signal in ["死叉", "绿柱"]:
            bearish_signals += 1

        if kdj_status == "超卖":
            bullish_signals += 1
        elif kdj_status == "超买":
            bearish_signals += 1

        if rsi_status == "超卖":
            bullish_signals += 1
        elif rsi_status == "超买":
            bearish_signals += 1

        if bullish_signals > bearish_signals + 1:
            overall_trend = "偏多"
        elif bearish_signals > bullish_signals + 1:
            overall_trend = "偏空"
        else:
            overall_trend = "震荡"

        return {
            "trend": overall_trend,
            "ma_trend": ma_trend,
            "macd_signal": macd_signal,
            "kdj_status": kdj_status,
            "rsi_status": rsi_status,
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals
        }
    except Exception as e:
        return {"trend": "unknown", "error": str(e)}


def analyze_patterns(df: pd.DataFrame) -> dict:
    """分析K线形态和历史规律"""
    if len(df) < 60:
        return {"patterns": [], "note": "数据不足"}

    patterns = []

    try:
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        close = latest['close']
        open_price = latest['open']
        high = latest['high']
        low = latest['low']
        prev_close = prev['close']

        # 今日K线形态
        body = abs(close - open_price)
        upper_shadow = high - max(close, open_price)
        lower_shadow = min(close, open_price) - low
        total_range = high - low

        # 十字星
        if body < total_range * 0.1 and total_range > 0:
            patterns.append({
                "name": "十字星",
                "signal": "变盘信号",
                "description": "开盘价与收盘价接近，市场犹豫不决，可能面临方向选择"
            })

        # 锤子线/上吊线
        if lower_shadow > body * 2 and upper_shadow < body * 0.5:
            if close > prev_close:
                patterns.append({
                    "name": "锤子线",
                    "signal": "看涨",
                    "description": "下影线较长，实体较小，可能是底部反转信号"
                })
            else:
                patterns.append({
                    "name": "上吊线",
                    "signal": "看跌",
                    "description": "出现在上涨趋势中，可能是顶部反转信号"
                })

        # 倒锤子/流星
        if upper_shadow > body * 2 and lower_shadow < body * 0.5:
            if close < prev_close:
                patterns.append({
                    "name": "流星线",
                    "signal": "看跌",
                    "description": "上影线较长，实体较小，可能是顶部反转信号"
                })

        # 大阳线/大阴线
        change_pct = (close - prev_close) / prev_close * 100 if prev_close > 0 else 0
        if change_pct > 5:
            patterns.append({
                "name": "大阳线",
                "signal": "看涨",
                "description": f"涨幅{change_pct:.2f}%，强势上涨信号"
            })
        elif change_pct < -5:
            patterns.append({
                "name": "大阴线",
                "signal": "看跌",
                "description": f"跌幅{abs(change_pct):.2f}%，强势下跌信号"
            })

        # 连续上涨/下跌
        recent_5 = df.tail(5)
        up_days = sum(1 for _, row in recent_5.iterrows() if row['close'] > row['open'])
        down_days = 5 - up_days

        if up_days >= 4:
            patterns.append({
                "name": "连续上涨",
                "signal": "注意回调",
                "description": f"近5日有{up_days}天上涨，短期可能面临回调"
            })
        elif down_days >= 4:
            patterns.append({
                "name": "连续下跌",
                "signal": "可能反弹",
                "description": f"近5日有{down_days}天下跌，短期可能出现反弹"
            })

        # 突破信号
        ma20 = latest.get('MA20', 0)
        prev_ma20 = prev.get('MA20', 0)
        if pd.notna(ma20) and pd.notna(prev_ma20):
            if close > ma20 and prev_close < prev_ma20:
                patterns.append({
                    "name": "突破20日均线",
                    "signal": "看涨",
                    "description": "股价站上20日均线，中期趋势可能转好"
                })
            elif close < ma20 and prev_close > prev_ma20:
                patterns.append({
                    "name": "跌破20日均线",
                    "signal": "看跌",
                    "description": "股价跌破20日均线，中期趋势可能转弱"
                })

        return {
            "patterns": patterns,
            "pattern_count": len(patterns),
            "bullish_patterns": len([p for p in patterns if "看涨" in p.get("signal", "")]),
            "bearish_patterns": len([p for p in patterns if "看跌" in p.get("signal", "")])
        }
    except Exception as e:
        return {"patterns": [], "error": str(e)}


def analyze_history_stats(df: pd.DataFrame) -> dict:
    """分析历史统计数据，挖掘规律"""
    if len(df) < 30:
        return {"note": "数据不足"}

    try:
        stats = {}

        # 计算涨跌幅（如果列不存在则自己计算）
        if 'change_pct' not in df.columns:
            df = df.copy()
            df['change_pct'] = df['close'].pct_change() * 100

        # 近期涨跌统计
        recent_30 = df.tail(30)
        changes_30 = recent_30['change_pct'].dropna()
        up_days = sum(1 for c in changes_30 if c > 0)
        down_days = sum(1 for c in changes_30 if c < 0)
        flat_days = len(changes_30) - up_days - down_days

        stats["recent_30_days"] = {
            "up_days": up_days,
            "down_days": down_days,
            "flat_days": flat_days,
            "up_ratio": round(up_days / len(changes_30) * 100, 1) if len(changes_30) > 0 else 0
        }

        # 涨跌幅分布
        if len(changes_30) > 0:
            stats["change_distribution"] = {
                "max_up": round(float(changes_30.max()), 2),
                "max_down": round(float(changes_30.min()), 2),
                "avg_change": round(float(changes_30.mean()), 2),
                "volatility": round(float(changes_30.std()), 2)
            }

        # 近60日统计
        if len(df) >= 60:
            recent_60 = df.tail(60)
            changes_60 = recent_60['change_pct'].dropna()
            if len(changes_60) > 0:
                stats["recent_60_days"] = {
                    "total_change": round(float(changes_60.sum()), 2),
                    "avg_change": round(float(changes_60.mean()), 2),
                    "volatility": round(float(changes_60.std()), 2),
                    "max_up": round(float(changes_60.max()), 2),
                    "max_down": round(float(changes_60.min()), 2)
                }

        # 成交量分析
        volumes = recent_30['volume'].dropna()
        if len(volumes) > 0:
            latest_vol = volumes.iloc[-1]
            avg_vol = volumes.mean()
            stats["volume_analysis"] = {
                "latest_volume": float(latest_vol),
                "avg_volume_30d": float(avg_vol),
                "volume_ratio": round(float(latest_vol / avg_vol), 2) if avg_vol > 0 else 0,
                "note": "放量" if latest_vol > avg_vol * 1.5 else "缩量" if latest_vol < avg_vol * 0.7 else "正常"
            }

        # 支撑压力位分析
        recent_high = recent_30['high'].max()
        recent_low = recent_30['low'].min()
        current_price = df.iloc[-1]['close']

        stats["support_resistance"] = {
            "recent_high": float(recent_high),
            "recent_low": float(recent_low),
            "current_price": float(current_price),
            "distance_to_high": round((current_price - recent_high) / recent_high * 100, 2) if recent_high > 0 else 0,
            "distance_to_low": round((current_price - recent_low) / recent_low * 100, 2) if recent_low > 0 else 0
        }

        return stats
    except Exception as e:
        return {"error": str(e)}


def get_financial_data(stock_code: str) -> dict:
    """获取财务数据（增强版，包含业绩预告、财报等）"""
    result = {}

    try:
        # 获取财务指标
        df = ak.stock_financial_analysis_indicator(symbol=stock_code)
        if not df.empty:
            latest = df.iloc[0]
            result["financial_indicators"] = {
                "pe_ratio": float(latest.get('市盈率', 0)) if pd.notna(latest.get('市盈率')) else None,
                "pb_ratio": float(latest.get('市净率', 0)) if pd.notna(latest.get('市净率')) else None,
                "roe": float(latest.get('净资产收益率', 0)) if pd.notna(latest.get('净资产收益率')) else None,
                "gross_margin": float(latest.get('销售毛利率', 0)) if pd.notna(latest.get('销售毛利率')) else None,
                "net_margin": float(latest.get('销售净利率', 0)) if pd.notna(latest.get('销售净利率')) else None,
                "debt_ratio": float(latest.get('资产负债率', 0)) if pd.notna(latest.get('资产负债率')) else None,
                "current_ratio": float(latest.get('流动比率', 0)) if pd.notna(latest.get('流动比率')) else None,
            }
    except Exception as e:
        result["financial_indicators"] = {"error": str(e)}

    # 获取业绩预告
    try:
        # 动态获取当前年份
        current_year = datetime.now().year
        df_forecast = ak.stock_yjyg_em(date=f"{current_year}1231")
        if not df_forecast.empty:
            stock_forecast = df_forecast[df_forecast['股票代码'] == stock_code]
            if not stock_forecast.empty:
                forecast_list = stock_forecast.head(3).to_dict('records')
                result["performance_forecast"] = forecast_list
    except:
        pass

    # 获取业绩快报
    try:
        # 动态计算最近季度末日期
        now = datetime.now()
        year = now.year
        month = now.month

        # 确定最近的报告期：0331, 0630, 0930, 1231
        if month >= 10:
            report_date = f"{year}0930"  # 三季报
        elif month >= 7:
            report_date = f"{year}0630"  # 半年报
        elif month >= 4:
            report_date = f"{year}0331"  # 一季报
        else:
            report_date = f"{year - 1}1231"  # 去年年报

        df_report = ak.stock_yjkb_em(date=report_date)
        if not df_report.empty:
            stock_report = df_report[df_report['股票代码'] == stock_code]
            if not stock_report.empty:
                report_data = stock_report.iloc[0]
                result["performance_report"] = {
                    "revenue": float(report_data.get('营业收入', 0)) if pd.notna(report_data.get('营业收入')) else None,
                    "revenue_yoy": float(report_data.get('营业收入同比', 0)) if pd.notna(report_data.get('营业收入同比')) else None,
                    "net_profit": float(report_data.get('净利润', 0)) if pd.notna(report_data.get('净利润')) else None,
                    "net_profit_yoy": float(report_data.get('净利润同比', 0)) if pd.notna(report_data.get('净利润同比')) else None,
                }
    except:
        pass

    # 获取主要财务数据（营收、利润等）
    try:
        df_main = ak.stock_financial_abstract_ths(symbol=stock_code)
        if not df_main.empty:
            # 取最近几期数据
            recent = df_main.head(4)
            result["financial_abstract"] = recent.to_dict('records')
    except:
        pass

    return result


def get_fund_flow(stock_code: str) -> dict:
    """获取资金流向数据（增强版）"""
    try:
        market = "sh" if stock_code.startswith('6') else "sz"
        df = ak.stock_individual_fund_flow(stock=stock_code, market=market)

        if df.empty:
            return {"error": "未获取到资金流向数据"}

        # 取最近10天数据分析趋势
        recent = df.head(10)

        latest = recent.iloc[0]

        # 计算主力资金趋势
        main_inflows = [float(x) for x in recent['主力净流入-净额'].head(5) if pd.notna(x)]
        main_trend = "持续流入" if sum(1 for x in main_inflows if x > 0) >= 3 else "持续流出" if sum(1 for x in main_inflows if x < 0) >= 3 else "反复震荡"

        # 注意：API返回的是"小单净流入"而不是"散户净流入"，两者含义相近
        return {
            "date": str(latest.get('日期', '')),
            "main_net_inflow": float(latest.get('主力净流入-净额', 0)) if pd.notna(latest.get('主力净流入-净额')) else 0,
            "main_net_inflow_pct": float(latest.get('主力净流入-净占比', 0)) if pd.notna(latest.get('主力净流入-净占比')) else 0,
            "small_net_inflow": float(latest.get('小单净流入-净额', 0)) if pd.notna(latest.get('小单净流入-净额')) else 0,
            "small_net_inflow_pct": float(latest.get('小单净流入-净占比', 0)) if pd.notna(latest.get('小单净流入-净占比')) else 0,
            "super_large_net_inflow": float(latest.get('超大单净流入-净额', 0)) if pd.notna(latest.get('超大单净流入-净额')) else 0,
            "large_net_inflow": float(latest.get('大单净流入-净额', 0)) if pd.notna(latest.get('大单净流入-净额')) else 0,
            "main_trend": main_trend,
            "recent_5_days": recent[['日期', '主力净流入-净额', '主力净流入-净占比', '小单净流入-净额']].head(5).to_dict('records')
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_stock_data(stock_codes: list[str]) -> dict:
    """获取所有股票数据"""
    result = {
        "fetch_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "stocks": {}
    }

    for code in stock_codes:
        print(f"正在获取 {code} 的数据...", file=sys.stderr)

        stock_data = {
            "code": code,
            "realtime": get_realtime_quote(code),
            "kline": get_kline_data(code),
            "financial": get_financial_data(code),
            "fund_flow": get_fund_flow(code)
        }

        result["stocks"][code] = stock_data

    return result


def main():
    parser = argparse.ArgumentParser(description='获取股票数据（增强版）')
    parser.add_argument('codes', nargs='+', help='股票代码列表，如: 600519 000858')
    parser.add_argument('--output', '-o', help='输出文件路径', default=None)
    parser.add_argument('--days', '-d', type=int, default=120, help='K线天数，默认120天')

    args = parser.parse_args()

    data = fetch_stock_data(args.codes)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
        print(f"数据已保存到 {args.output}", file=sys.stderr)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2, cls=DateTimeEncoder))


if __name__ == '__main__':
    main()
