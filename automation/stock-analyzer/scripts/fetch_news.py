#!/usr/bin/env python3
"""
股票资讯采集脚本（增强版）
采集公司公告、相关新闻、研报摘要、行业动态、散户情绪
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import akshare as ak
import pandas as pd


def retry_request(func, max_retries=3, delay=2, *args, **kwargs):
    """带重试机制的请求函数"""
    last_error = None
    for i in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            if i < max_retries - 1:
                print(f"请求失败({i+1}/{max_retries}): {e}，{delay}秒后重试...", file=sys.stderr)
                time.sleep(delay)
    raise last_error


def get_market_overview_sina() -> dict:
    """从新浪财经获取大盘指数（备用数据源）"""
    import requests
    try:
        # 主要指数代码
        indices_codes = {
            'sh000001': '上证指数',
            'sz399001': '深证成指',
            'sz399006': '创业板指',
            'sh000688': '科创50'
        }

        codes = ','.join(indices_codes.keys())
        url = f"https://hq.sinajs.cn/list={codes}"
        headers = {'Referer': 'https://finance.sina.com.cn/'}
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return {"error": f"新浪财经请求失败: {r.status_code}"}

        indices_data = []
        for line in r.text.strip().split('\n'):
            if not line.strip():
                continue
            # 解析 var hq_str_sh000001="...";
            import re
            match = re.search(r'var hq_str_([^=]+)="(.*)"', line)
            if not match:
                continue

            code = match.group(1)
            data = match.group(2).split(',')

            if len(data) < 32 or code not in indices_codes:
                continue

            name = data[0]
            open_price = float(data[1]) if data[1] else 0
            pre_close = float(data[2]) if data[2] else 0
            price = float(data[3]) if data[3] else 0
            change_amount = price - pre_close if pre_close > 0 else 0
            change_pct = (change_amount / pre_close * 100) if pre_close > 0 else 0

            indices_data.append({
                "name": indices_codes[code],
                "price": round(price, 2),
                "change_pct": round(change_pct, 2),
                "change_amount": round(change_amount, 2),
            })

        return {
            "indices": indices_data,
            "market_breadth": {"note": "新浪财经不提供涨跌家数"},
            "market_sentiment": "数据来源：新浪财经"
        }
    except Exception as e:
        return {"error": str(e), "indices": [], "market_breadth": {}, "market_sentiment": "数据获取失败"}


def get_stock_news(stock_code: str, limit: int = 15) -> dict:
    """获取股票相关新闻"""
    try:
        df = ak.stock_news_em(symbol=stock_code)

        if df.empty:
            return {"error": "未获取到新闻数据", "news": []}

        recent = df.head(limit)

        news_list = []
        for _, row in recent.iterrows():
            news_list.append({
                "title": str(row.get('新闻标题', '')),
                "content": str(row.get('新闻内容', ''))[:500] if '新闻内容' in row else '',
                "source": str(row.get('来源', '')) if '来源' in row else '',
                "time": str(row.get('发布时间', '')) if '发布时间' in row else '',
            })

        # 简单的情绪分析（基于关键词）
        positive_keywords = ['利好', '增长', '盈利', '突破', '上涨', '增持', '回购', '中标', '合作', '创新高']
        negative_keywords = ['利空', '亏损', '下降', '下跌', '减持', '诉讼', '处罚', '风险', '质疑', '暴跌']

        positive_count = 0
        negative_count = 0

        for news in news_list:
            title = news.get('title', '')
            for kw in positive_keywords:
                if kw in title:
                    positive_count += 1
                    break
            for kw in negative_keywords:
                if kw in title:
                    negative_count += 1
                    break

        return {
            "count": len(news_list),
            "news": news_list,
            "sentiment": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": len(news_list) - positive_count - negative_count,
                "overall": "偏多" if positive_count > negative_count else "偏空" if negative_count > positive_count else "中性"
            }
        }
    except Exception as e:
        return {"error": str(e), "news": []}


def get_company_announcements(stock_code: str, limit: int = 10) -> dict:
    """获取公司公告"""
    try:
        # 尝试使用 stock_notice_report API
        try:
            df = ak.stock_notice_report(symbol=stock_code)
            if df.empty:
                raise Exception("数据为空")
        except Exception as e:
            # 如果失败，从新闻中筛选公告类型的新闻
            print(f"公告API失败: {e}，从新闻中筛选公告...", file=sys.stderr)
            df = ak.stock_news_em(symbol=stock_code)
            if df.empty:
                return {"error": "未获取到公告数据", "announcements": []}
            # 筛选包含"公告"或"龙虎榜"的新闻（龙虎榜也是重要信息）
            mask = df['新闻标题'].str.contains('公告|报告|披露|龙虎榜|异动', na=False)
            df_filtered = df[mask]
            # 如果筛选后为空，直接使用原始新闻
            if df_filtered.empty:
                df_filtered = df
            df = df_filtered

        recent = df.head(limit)

        announcements = []
        important_types = ['业绩', '利润', '亏损', '增持', '减持', '重组', '分红', '回购', '龙虎榜', '涨停', '跌停']

        for _, row in recent.iterrows():
            title = str(row.get('公告标题', '')) if '公告标题' in row else str(row.get('新闻标题', ''))
            ann_type = str(row.get('公告类型', '')) if '公告类型' in row else ''

            is_important = any(t in title or t in ann_type for t in important_types)

            announcements.append({
                "title": title,
                "type": ann_type,
                "date": str(row.get('公告日期', '')) if '公告日期' in row else str(row.get('发布时间', '')),
                "important": is_important
            })

        # 筛选重要公告
        important_announcements = [a for a in announcements if a.get('important')]

        return {
            "count": len(announcements),
            "important_count": len(important_announcements),
            "announcements": announcements,
            "important_announcements": important_announcements[:5]  # 只返回前5条重要公告
        }
    except Exception as e:
        return {"error": str(e), "announcements": []}


def get_research_reports(stock_code: str, limit: int = 10) -> dict:
    """获取研报数据"""
    try:
        df = ak.stock_research_report_em(symbol=stock_code)

        if df.empty:
            return {"error": "未获取到研报数据", "reports": []}

        recent = df.head(limit)

        reports = []
        rating_stats = {"买入": 0, "增持": 0, "中性": 0, "减持": 0, "卖出": 0, "其他": 0}

        for _, row in recent.iterrows():
            rating = str(row.get('评级', '')) if '评级' in row else ''
            if '买入' in rating:
                rating_stats["买入"] += 1
            elif '增持' in rating:
                rating_stats["增持"] += 1
            elif '中性' in rating:
                rating_stats["中性"] += 1
            elif '减持' in rating:
                rating_stats["减持"] += 1
            elif '卖出' in rating:
                rating_stats["卖出"] += 1
            else:
                rating_stats["其他"] += 1

            reports.append({
                "title": str(row.get('标题', '')) if '标题' in row else '',
                "rating": rating,
                "institution": str(row.get('机构', '')) if '机构' in row else '',
                "researcher": str(row.get('研究员', '')) if '研究员' in row else '',
                "date": str(row.get('日期', '')) if '日期' in row else '',
            })

        # 计算综合评级
        positive_ratings = rating_stats["买入"] + rating_stats["增持"]
        negative_ratings = rating_stats["减持"] + rating_stats["卖出"]
        total = sum(rating_stats.values())

        if total > 0:
            positive_ratio = positive_ratings / total
            if positive_ratio > 0.6:
                overall_rating = "看多"
            elif positive_ratio > 0.4:
                overall_rating = "中性偏多"
            elif negative_ratings / total > 0.3:
                overall_rating = "看空"
            else:
                overall_rating = "中性"
        else:
            overall_rating = "无评级"

        return {
            "count": len(reports),
            "reports": reports,
            "rating_stats": rating_stats,
            "overall_rating": overall_rating
        }
    except Exception as e:
        return {"error": str(e), "reports": []}


def get_industry_info(stock_code: str) -> dict:
    """获取行业信息（带重试和备用数据源）"""
    try:
        df = retry_request(ak.stock_individual_info_em, max_retries=2, delay=2, symbol=stock_code)

        if df.empty:
            raise Exception("数据为空")

        info_dict = dict(zip(df['item'], df['value']))

        return {
            "industry": info_dict.get('行业', ''),
            "sector": info_dict.get('板块', ''),
            "concept": info_dict.get('概念', ''),
            "region": info_dict.get('地区', ''),
            "list_date": info_dict.get('上市时间', ''),
            "total_share": info_dict.get('总股本', ''),
            "data_source": "东方财富"
        }
    except Exception as e:
        print(f"东方财富行业信息失败: {e}，尝试备用数据源...", file=sys.stderr)
        # 备用：从腾讯财经获取基本信息
        try:
            import requests
            market = "sh" if stock_code.startswith('6') else "sz"
            url = f'https://web.sqt.gtimg.cn/q={market}{stock_code}'
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                parts = r.text.split('="')
                if len(parts) >= 2:
                    data = parts[1].strip('";').split('~')
                    if len(data) > 60:
                        return {
                            "industry": "未知",
                            "sector": str(data[1]) if len(data) > 1 else "",  # 股票名称
                            "concept": "",
                            "region": "",
                            "list_date": "",
                            "total_share": "",
                            "data_source": "腾讯财经（备用）",
                            "note": "仅获取基本信息"
                        }
        except Exception as e2:
            print(f"腾讯财经备用也失败: {e2}", file=sys.stderr)
        return {"error": str(e)}


def get_retail_sentiment(stock_code: str) -> dict:
    """
    获取散户情绪数据（使用股票评论接口）
    """
    result = {
        "source": "东方财富股票评论",
        "note": "散户情绪数据仅供参考，可能存在较大噪音，需结合其他指标综合判断"
    }

    try:
        # 使用股票评论接口获取情绪数据
        df = ak.stock_comment_em()

        if df.empty:
            return {**result, "error": "未获取到评论数据"}

        # 查找对应股票
        stock_data = df[df['代码'] == stock_code]
        if stock_data.empty:
            return {**result, "error": f"未找到股票 {stock_code} 的评论数据"}

        row = stock_data.iloc[0]

        # 解析情绪数据
        score = float(row.get('综合得分', 0)) if pd.notna(row.get('综合得分')) else 0
        focus_index = float(row.get('关注指数', 0)) if pd.notna(row.get('关注指数')) else 0
        current_state = int(row.get('目前状态', 0)) if pd.notna(row.get('目前状态')) else 0

        # 综合得分范围通常是0-100
        if score >= 70:
            sentiment = "看多情绪浓厚"
            sentiment_signal = "bullish"
        elif score >= 55:
            sentiment = "偏乐观"
            sentiment_signal = "slightly_bullish"
        elif score >= 45:
            sentiment = "分歧较大"
            sentiment_signal = "neutral"
        elif score >= 30:
            sentiment = "偏悲观"
            sentiment_signal = "slightly_bearish"
        else:
            sentiment = "看空情绪浓厚"
            sentiment_signal = "bearish"

        # 关注指数判断热度
        if focus_index >= 90:
            heat_level = "极高"
        elif focus_index >= 70:
            heat_level = "高"
        elif focus_index >= 50:
            heat_level = "中等"
        else:
            heat_level = "低"

        return {
            **result,
            "stock_name": str(row.get('名称', '')),
            "sentiment_analysis": {
                "score": round(score, 2),
                "sentiment": sentiment,
                "sentiment_signal": sentiment_signal,
                "current_state": current_state,
                "state_note": "状态值>0偏多，<0偏空" if current_state != 0 else "中性"
            },
            "heat_analysis": {
                "focus_index": round(focus_index, 2),
                "heat_level": heat_level
            },
            "vote_data": {
                "bullish_ratio": float(row.get('多头比例', 0)) if '多头比例' in row and pd.notna(row.get('多头比例')) else None,
                "bearish_ratio": float(row.get('空头比例', 0)) if '空头比例' in row and pd.notna(row.get('空头比例')) else None,
            },
            "warning": "注意：当散户情绪过于一致时（如综合得分>80或<20），往往与实际走势相反，需谨慎参考" if score > 80 or score < 20 else None
        }
    except Exception as e:
        return {**result, "error": str(e)}


def get_investor_vote(stock_code: str) -> dict:
    """获取投资者投票数据（看涨看跌投票）"""
    try:
        # 获取投资者互动数据
        df = ak.stock_comment_em()

        if df.empty:
            return {"error": "未获取到投票数据"}

        # 查找对应股票
        stock_data = df[df['代码'] == stock_code]
        if stock_data.empty:
            return {"error": f"未找到股票 {stock_code} 的投票数据"}

        row = stock_data.iloc[0]

        return {
            "code": stock_code,
            "name": str(row.get('名称', '')),
            "bullish_ratio": float(row.get('看涨比例', 0)) if '看涨比例' in row and pd.notna(row.get('看涨比例')) else None,
            "bearish_ratio": float(row.get('看跌比例', 0)) if '看跌比例' in row and pd.notna(row.get('看跌比例')) else None,
            "vote_count": int(row.get('投票数', 0)) if '投票数' in row and pd.notna(row.get('投票数')) else None,
        }
    except Exception as e:
        return {"error": str(e)}


def get_hot_concepts() -> dict:
    """获取热门概念板块（带重试和备用数据源）"""
    try:
        df = retry_request(ak.stock_board_concept_name_em, max_retries=2, delay=2)

        if df.empty:
            raise Exception("数据为空")

        top_concepts = df.head(20)

        concepts = []
        for _, row in top_concepts.iterrows():
            concepts.append({
                "name": str(row.get('板块名称', '')),
                "change_pct": float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else 0,
                "leading_stock": str(row.get('领涨股票', '')) if '领涨股票' in row else '',
            })

        return {
            "count": len(concepts),
            "concepts": concepts,
            "data_source": "东方财富"
        }
    except Exception as e:
        print(f"东方财富概念板块失败: {e}，尝试备用数据源...", file=sys.stderr)
        # 备用：返回空数据，标记为不可用
        return {
            "error": f"概念板块数据暂时不可用: {e}",
            "concepts": [],
            "note": "东方财富API连接失败，可稍后重试"
        }


def get_market_overview() -> dict:
    """获取市场概况（带重试和备用数据源）"""
    try:
        # 使用重试机制获取指数数据
        df = retry_request(ak.stock_zh_index_spot_em, max_retries=2, delay=2)

        main_indices = ['上证指数', '深证成指', '创业板指', '科创50']
        indices_data = []

        for idx_name in main_indices:
            idx_df = df[df['名称'] == idx_name]
            if not idx_df.empty:
                row = idx_df.iloc[0]
                indices_data.append({
                    "name": idx_name,
                    "price": float(row.get('最新价', 0)),
                    "change_pct": float(row.get('涨跌幅', 0)),
                    "change_amount": float(row.get('涨跌额', 0)),
                })

        # 获取涨跌家数（带重试）
        try:
            up_down_df = retry_request(ak.stock_zh_a_spot_em, max_retries=2, delay=2)
            total = len(up_down_df)
            up = len(up_down_df[up_down_df['涨跌幅'] > 0])
            down = len(up_down_df[up_down_df['涨跌幅'] < 0])
            flat = total - up - down

            # 涨停跌停统计
            limit_up = len(up_down_df[up_down_df['涨跌幅'] >= 9.9])
            limit_down = len(up_down_df[up_down_df['涨跌幅'] <= -9.9])
        except Exception as e:
            print(f"获取涨跌家数失败: {e}", file=sys.stderr)
            up = down = flat = limit_up = limit_down = 0
            total = 0

        return {
            "indices": indices_data,
            "market_breadth": {
                "up": up,
                "down": down,
                "flat": flat,
                "total": total,
                "limit_up": limit_up,
                "limit_down": limit_down
            },
            "market_sentiment": "偏多" if up > down * 1.5 else "偏空" if down > up * 1.5 else "均衡",
            "data_source": "东方财富"
        }
    except Exception as e:
        print(f"东方财富市场数据失败: {e}，切换到新浪财经...", file=sys.stderr)
        # 切换到新浪备用数据源
        result = get_market_overview_sina()
        if 'error' not in result or not result.get('error'):
            result["data_source"] = "新浪财经（备用）"
        return result


def get_industry_performance() -> dict:
    """获取行业板块表现（带重试和备用数据源）"""
    try:
        df = retry_request(ak.stock_board_industry_name_em, max_retries=2, delay=2)

        if df.empty:
            raise Exception("数据为空")

        # 涨幅前5和跌幅前5
        top_gainers = df.head(5)
        top_losers = df.tail(5)

        gainers = []
        for _, row in top_gainers.iterrows():
            gainers.append({
                "name": str(row.get('板块名称', '')),
                "change_pct": float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else 0,
            })

        losers = []
        for _, row in top_losers.iterrows():
            losers.append({
                "name": str(row.get('板块名称', '')),
                "change_pct": float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else 0,
            })

        return {
            "top_gainers": gainers,
            "top_losers": losers,
            "data_source": "东方财富"
        }
    except Exception as e:
        print(f"东方财富行业板块失败: {e}", file=sys.stderr)
        return {
            "error": f"行业板块数据暂时不可用: {e}",
            "note": "东方财富API连接失败，可稍后重试"
        }


def fetch_news_data(stock_codes: list[str]) -> dict:
    """获取所有资讯数据"""
    result = {
        "fetch_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "market": get_market_overview(),
        "hot_concepts": get_hot_concepts(),
        "industry_performance": get_industry_performance(),
        "stocks": {}
    }

    for code in stock_codes:
        print(f"正在获取 {code} 的资讯和情绪数据...", file=sys.stderr)

        stock_news = {
            "code": code,
            "news": get_stock_news(code),
            "announcements": get_company_announcements(code),
            "research_reports": get_research_reports(code),
            "industry_info": get_industry_info(code),
            "retail_sentiment": get_retail_sentiment(code),
            "investor_vote": get_investor_vote(code)
        }

        result["stocks"][code] = stock_news

    return result


def main():
    parser = argparse.ArgumentParser(description='获取股票资讯（增强版）')
    parser.add_argument('codes', nargs='+', help='股票代码列表，如: 600519 000858')
    parser.add_argument('--output', '-o', help='输出文件路径', default=None)

    args = parser.parse_args()

    data = fetch_news_data(args.codes)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {args.output}", file=sys.stderr)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
