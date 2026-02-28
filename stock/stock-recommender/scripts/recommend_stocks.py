#!/usr/bin/env python3
"""
股票智能推荐脚本
基于多维度评分筛选优质股票
"""

import argparse
import json
import sys
from datetime import datetime
from typing import List, Dict, Optional

import akshare as ak
import numpy as np
import pandas as pd
import requests


class StockRecommender:
    """股票推荐引擎"""

    # 评分权重配置
    WEIGHTS = {
        "technical": 0.30,    # 技术面30%
        "fundamental": 0.25,  # 基本面25%
        "capital": 0.25,      # 资金面25%
        "market": 0.20        # 市场面20%
    }

    def __init__(self, min_cap=None, max_cap=None, industries=None,
                 exclude_st=True, min_score=60):
        """
        初始化推荐引擎

        Args:
            min_cap: 最小市值（亿）
            max_cap: 最大市值（亿）
            industries: 行业列表
            exclude_st: 是否排除ST股票
            min_score: 最低综合评分
        """
        self.min_cap = min_cap
        self.max_cap = max_cap
        self.industries = industries or []
        self.exclude_st = exclude_st
        self.min_score = min_score

    def get_stock_pool(self) -> pd.DataFrame:
        """获取候选股票池"""
        try:
            print("正在获取A股市场数据...", file=sys.stderr)
            df = ak.stock_zh_a_spot_em()

            if df.empty:
                raise Exception("未获取到市场数据")

            print(f"获取到 {len(df)} 只股票", file=sys.stderr)

            # 基础筛选
            if self.exclude_st:
                # 排除ST、*ST股票
                df = df[~df['名称'].str.contains('ST|退', na=False)]
                print(f"排除ST后剩余 {len(df)} 只", file=sys.stderr)

            # 市值筛选
            if self.min_cap or self.max_cap:
                # 总市值单位是亿
                if self.min_cap:
                    df = df[df['总市值'] >= self.min_cap * 100000000]
                if self.max_cap:
                    df = df[df['总市值'] <= self.max_cap * 100000000]
                print(f"市值筛选后剩余 {len(df)} 只", file=sys.stderr)

            return df

        except Exception as e:
            print(f"获取股票池失败: {e}", file=sys.stderr)
            return pd.DataFrame()

    def score_technical(self, stock_code: str) -> Dict:
        """技术面评分（30分）"""
        score = 0
        details = {}

        try:
            # 获取K线数据
            kline = self._get_kline_data(stock_code)
            if not kline:
                return {"score": 0, "details": {"error": "数据不足"}}

            df = pd.DataFrame(kline)
            if len(df) < 60:
                return {"score": 0, "details": {"error": "数据不足"}}

            latest = df.iloc[-1]

            # 1. 均线系统（10分）
            ma5 = latest.get('MA5', 0)
            ma10 = latest.get('MA10', 0)
            ma20 = latest.get('MA20', 0)
            ma60 = latest.get('MA60', 0)
            close = latest.get('close', 0)

            if pd.notna(ma5) and pd.notna(ma10) and pd.notna(ma20):
                if ma5 > ma10 > ma20 > ma60:
                    score += 10
                    details['ma_system'] = "强多头排列"
                elif ma5 > ma10 > ma20:
                    score += 7
                    details['ma_system'] = "多头排列"
                elif ma5 > ma10:
                    score += 4
                    details['ma_system'] = "短期向好"
                else:
                    score += 0
                    details['ma_system'] = "空头排列"

            # 2. MACD信号（5分）
            macd = latest.get('MACDh_12_26_9', 0)
            prev_macd = df.iloc[-2].get('MACDh_12_26_9', 0)

            if pd.notna(macd) and pd.notna(prev_macd):
                if macd > 0 and prev_macd <= 0:
                    score += 5
                    details['macd'] = "金叉信号"
                elif macd > 0:
                    score += 3
                    details['macd'] = "红柱持续"
                elif macd < 0:
                    score += 0
                    details['macd'] = "绿柱"

            # 3. KDJ/RSI（5分）
            k_value = latest.get('K_9_3', 50)
            rsi = latest.get('RSI_14', 50)

            kdj_score = 0
            if pd.notna(k_value):
                if 20 < k_value < 50:  # 超卖区域加分
                    kdj_score += 3
                    details['kdj'] = f"K值{k_value:.1f}（超卖反弹）"
                elif 50 < k_value < 80:  # 正常区域
                    kdj_score += 2
                    details['kdj'] = f"K值{k_value:.1f}（正常）"
                elif k_value > 80:  # 超买减分
                    kdj_score += 0
                    details['kdj'] = f"K值{k_value:.1f}（超买）"

            if pd.notna(rsi):
                if 30 < rsi < 50:
                    kdj_score += 2
                elif 50 < rsi < 70:
                    kdj_score += 1

            score += min(kdj_score, 5)

            # 4. 趋势强度（5分）
            recent_5 = df.tail(5)
            up_days = sum(1 for _, row in recent_5.iterrows() if row['close'] > row['open'])

            if up_days >= 4:
                score += 5
                details['trend'] = "强势上涨"
            elif up_days >= 3:
                score += 3
                details['trend'] = "震荡向上"
            else:
                score += 0
                details['trend'] = "偏弱"

            # 5. K线形态（5分）
            pattern_score = self._score_patterns(df)
            score += pattern_score
            details['pattern'] = f"形态得分{pattern_score}"

        except Exception as e:
            details['error'] = str(e)

        return {
            "score": min(score, 30),
            "details": details
        }

    def score_fundamental(self, stock_code: str, market_cap: float) -> Dict:
        """基本面评分（25分）"""
        score = 0
        details = {}

        try:
            # 获取财务数据
            df = ak.stock_financial_analysis_indicator(symbol=stock_code)
            if df.empty:
                return {"score": 0, "details": {"error": "无财务数据"}}

            latest = df.iloc[0]

            # 1. 估值水平（8分）
            pe = float(latest.get('市盈率', 0)) if pd.notna(latest.get('市盈率')) else None
            pb = float(latest.get('市净率', 0)) if pd.notna(latest.get('市净率')) else None

            pe_score = 0
            if pe and 0 < pe < 15:
                pe_score += 5  # 低估值
                details['pe'] = f"{pe:.2f}（低估）"
            elif pe and 15 <= pe < 30:
                pe_score += 3  # 合理估值
                details['pe'] = f"{pe:.2f}（合理）"
            elif pe and 30 <= pe < 50:
                pe_score += 1  # 偏高
                details['pe'] = f"{pe:.2f}（偏高）"
            else:
                details['pe'] = "过高或亏损"

            if pb and 0 < pb < 2:
                pe_score += 3
                details['pb'] = f"{pb:.2f}（合理）"
            elif pb and pb >= 2:
                pe_score += 1

            score += min(pe_score, 8)

            # 2. 盈利能力（8分）
            roe = float(latest.get('净资产收益率', 0)) if pd.notna(latest.get('净资产收益率')) else 0
            gross_margin = float(latest.get('销售毛利率', 0)) if pd.notna(latest.get('销售毛利率')) else 0

            if roe > 15:
                score += 5
                details['roe'] = f"{roe:.2f}%（优秀）"
            elif roe > 10:
                score += 3
                details['roe'] = f"{roe:.2f}%（良好）"
            elif roe > 5:
                score += 1
                details['roe'] = f"{roe:.2f}%（一般）"

            if gross_margin > 30:
                score += 3
                details['margin'] = f"{gross_margin:.2f}%（高毛利）"
            elif gross_margin > 20:
                score += 2

            # 3. 财务健康（5分）
            debt_ratio = float(latest.get('资产负债率', 0)) if pd.notna(latest.get('资产负债率')) else 0
            current_ratio = float(latest.get('流动比率', 0)) if pd.notna(latest.get('流动比率')) else 0

            if 0 < debt_ratio < 40:
                score += 3
                details['debt'] = f"{debt_ratio:.1f}%（低负债）"
            elif debt_ratio < 60:
                score += 2

            if current_ratio > 2:
                score += 2
                details['liquidity'] = "流动性好"
            elif current_ratio > 1:
                score += 1

            # 4. 业绩增长（4分）
            # 尝试获取业绩预告
            try:
                current_year = datetime.now().year
                df_forecast = ak.stock_yjyg_em(date=f"{current_year}1231")
                stock_forecast = df_forecast[df_forecast['股票代码'] == stock_code]

                if not stock_forecast.empty:
                    forecast = stock_forecast.iloc[0]
                    forecast_type = str(forecast.get('业绩变动', ''))

                    if '预增' in forecast_type or '扭亏' in forecast_type:
                        score += 4
                        details['forecast'] = "业绩预增"
                    elif '略增' in forecast_type:
                        score += 2
                        details['forecast'] = "业绩略增"
            except:
                pass

        except Exception as e:
            details['error'] = str(e)

        return {
            "score": min(score, 25),
            "details": details
        }

    def score_capital(self, stock_code: str) -> Dict:
        """资金面评分（25分）"""
        score = 0
        details = {}

        try:
            market = "sh" if stock_code.startswith('6') else "sz"
            df = ak.stock_individual_fund_flow(stock=stock_code, market=market)

            if df.empty:
                return {"score": 0, "details": {"error": "无资金数据"}}

            recent = df.head(10)
            latest = recent.iloc[0]

            # 1. 主力净流入（15分）
            main_inflow = float(latest.get('主力净流入-净额', 0))
            main_pct = float(latest.get('主力净流入-净占比', 0))

            if main_inflow > 0 and main_pct > 10:
                score += 15
                details['main_flow'] = f"大幅流入{main_inflow/10000:.2f}万"
            elif main_inflow > 0 and main_pct > 5:
                score += 10
                details['main_flow'] = f"流入{main_inflow/10000:.2f}万"
            elif main_inflow > 0:
                score += 5
                details['main_flow'] = "小幅流入"
            else:
                score += 0
                details['main_flow'] = "流出"

            # 2. 资金流入趋势（5分）
            main_inflows = [float(x) for x in recent['主力净流入-净额'].head(5) if pd.notna(x)]
            positive_days = sum(1 for x in main_inflows if x > 0)

            if positive_days >= 4:
                score += 5
                details['trend'] = "持续流入"
            elif positive_days >= 3:
                score += 3
                details['trend'] = "多数流入"

            # 3. 换手率（5分）
            # 需要从行情数据获取
            try:
                quote = self._get_realtime_quote(stock_code)
                turnover = quote.get('turnover_rate', 0)

                if 3 < turnover < 10:
                    score += 5
                    details['turnover'] = f"{turnover:.2f}%（活跃）"
                elif 1 < turnover < 15:
                    score += 3
                    details['turnover'] = f"{turnover:.2f}%（正常）"
            except:
                pass

        except Exception as e:
            details['error'] = str(e)

        return {
            "score": min(score, 25),
            "details": details
        }

    def score_market(self, stock_code: str, industry: str) -> Dict:
        """市场面评分（20分）"""
        score = 0
        details = {}

        try:
            # 1. 行业表现（8分）
            try:
                df_industry = ak.stock_board_industry_name_em()
                if not df_industry.empty and industry:
                    industry_data = df_industry[df_industry['板块名称'].str.contains(industry, na=False)]
                    if not industry_data.empty:
                        ind = industry_data.iloc[0]
                        ind_change = float(ind.get('涨跌幅', 0))

                        if ind_change > 3:
                            score += 8
                            details['industry'] = f"{industry}涨{ind_change:.2f}%（强势）"
                        elif ind_change > 1:
                            score += 5
                            details['industry'] = f"{industry}涨{ind_change:.2f}%"
                        elif ind_change > 0:
                            score += 3
                            details['industry'] = f"{industry}涨{ind_change:.2f}%"
            except:
                pass

            # 2. 概念热度（7分）
            try:
                # 获取个股信息
                df_info = ak.stock_individual_info_em(symbol=stock_code)
                if not df_info.empty:
                    info_dict = dict(zip(df_info['item'], df_info['value']))
                    concepts = info_dict.get('概念', '')

                    # 检查是否属于热门概念
                    df_concept = ak.stock_board_concept_name_em()
                    hot_concepts = df_concept.head(10)['板块名称'].tolist()

                    hot_count = sum(1 for c in hot_concepts if c in concepts)
                    if hot_count >= 2:
                        score += 7
                        details['concept'] = "多个热门概念"
                    elif hot_count >= 1:
                        score += 4
                        details['concept'] = "有热门概念"
            except:
                pass

            # 3. 散户情绪（5分）
            try:
                df_comment = ak.stock_comment_em()
                stock_comment = df_comment[df_comment['代码'] == stock_code]

                if not stock_comment.empty:
                    row = stock_comment.iloc[0]
                    sentiment_score = float(row.get('综合得分', 50))

                    # 适中情绪最好（50-70），极端情绪反向扣分
                    if 50 <= sentiment_score <= 70:
                        score += 5
                        details['sentiment'] = f"情绪适中{sentiment_score:.0f}"
                    elif 40 <= sentiment_score <= 80:
                        score += 3
                        details['sentiment'] = f"情绪{sentiment_score:.0f}"
                    elif sentiment_score > 85:
                        score += 0
                        details['sentiment'] = f"情绪过热{sentiment_score:.0f}（警惕）"
                    elif sentiment_score < 30:
                        score += 2
                        details['sentiment'] = f"情绪低迷{sentiment_score:.0f}（可能反转）"
            except:
                pass

        except Exception as e:
            details['error'] = str(e)

        return {
            "score": min(score, 20),
            "details": details
        }

    def calculate_risk_level(self, market_cap: float, volatility: float) -> Dict:
        """计算风险等级"""
        cap_yi = market_cap / 100000000

        if cap_yi > 500:
            base_risk = "低风险"
        elif cap_yi > 200:
            base_risk = "中低风险"
        elif cap_yi > 50:
            base_risk = "中等风险"
        elif cap_yi > 20:
            base_risk = "中高风险"
        else:
            base_risk = "高风险"

        # 根据波动率调整
        if volatility > 12:
            risk_note = f"{base_risk}，高波动"
        elif volatility > 8:
            risk_note = f"{base_risk}，中波动"
        else:
            risk_note = f"{base_risk}，低波动"

        return {
            "level": base_risk,
            "volatility": round(volatility, 2),
            "note": risk_note
        }

    def recommend(self, limit: int = 10) -> List[Dict]:
        """执行推荐"""
        stock_pool = self.get_stock_pool()

        if stock_pool.empty:
            print("股票池为空", file=sys.stderr)
            return []

        recommendations = []

        # 限制处理数量，避免API限流
        max_process = min(len(stock_pool), 200)
        print(f"将处理 {max_process} 只股票...", file=sys.stderr)

        for idx, (_, row) in enumerate(stock_pool.head(max_process).iterrows()):
            try:
                code = str(row['代码'])
                name = str(row['名称'])
                price = float(row['最新价'])
                change_pct = float(row['涨跌幅'])
                market_cap = float(row['总市值'])

                print(f"[{idx+1}/{max_process}] 评估 {name}({code})...", file=sys.stderr)

                # 计算各维度评分
                tech_score = self.score_technical(code)
                fund_score = self.score_fundamental(code, market_cap)
                cap_score = self.score_capital(code)

                # 获取行业信息
                industry = ""
                try:
                    df_info = ak.stock_individual_info_em(symbol=code)
                    if not df_info.empty:
                        info_dict = dict(zip(df_info['item'], df_info['value']))
                        industry = info_dict.get('行业', '')
                except:
                    pass

                market_score = self.score_market(code, industry)

                # 计算综合评分
                total_score = (
                    tech_score['score'] +
                    fund_score['score'] +
                    cap_score['score'] +
                    market_score['score']
                )

                # 过滤低分股票
                if total_score < self.min_score:
                    continue

                # 计算波动率（从K线数据）
                volatility = 5.0  # 默认值
                try:
                    kline = self._get_kline_data(code)
                    if kline:
                        df = pd.DataFrame(kline)
                        if len(df) >= 30:
                            df['change_pct'] = df['close'].pct_change() * 100
                            volatility = df['change_pct'].std()
                except:
                    pass

                risk = self.calculate_risk_level(market_cap, volatility)

                recommendations.append({
                    "code": code,
                    "name": name,
                    "price": price,
                    "change_pct": change_pct,
                    "market_cap": market_cap,
                    "industry": industry,
                    "scores": {
                        "technical": tech_score,
                        "fundamental": fund_score,
                        "capital": cap_score,
                        "market": market_score,
                        "total": round(total_score, 2)
                    },
                    "risk": risk
                })

            except Exception as e:
                print(f"评估 {row['名称']} 失败: {e}", file=sys.stderr)
                continue

        # 按综合评分排序
        recommendations.sort(key=lambda x: x['scores']['total'], reverse=True)

        return recommendations[:limit]

    def _get_kline_data(self, stock_code: str) -> List:
        """获取K线数据（简化版）"""
        try:
            prefix = 'sh' if stock_code.startswith('6') else 'sz'
            full_code = f"{prefix}{stock_code}"

            url = f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var_kline=kline&param={full_code},day,,,60,qfq"
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'http://gu.qq.com/'
            }

            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

            kline_raw = data.get('data', {}).get(full_code, {}).get('qfqday', [])
            if not kline_raw:
                return []

            clean_data = [row[:6] for row in kline_raw]
            df = pd.DataFrame(clean_data, columns=['date', 'open', 'close', 'high', 'low', 'volume'])

            for col in ['open', 'close', 'high', 'low', 'volume']:
                df[col] = pd.to_numeric(df[col])

            # 计算简化的技术指标
            close = df['close']
            high = df['high']
            low = df['low']

            df['MA5'] = close.rolling(window=5).mean()
            df['MA10'] = close.rolling(window=10).mean()
            df['MA20'] = close.rolling(window=20).mean()
            df['MA60'] = close.rolling(window=60).mean()

            # MACD
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            df['MACD_12_26_9'] = ema12 - ema26
            df['MACDs_12_26_9'] = df['MACD_12_26_9'].ewm(span=9, adjust=False).mean()
            df['MACDh_12_26_9'] = (df['MACD_12_26_9'] - df['MACDs_12_26_9']) * 2

            # KDJ
            low_9 = low.rolling(window=9).min()
            high_9 = high.rolling(window=9).max()
            rsv = (close - low_9) / (high_9 - low_9) * 100
            rsv = rsv.fillna(50)
            df['K_9_3'] = rsv.ewm(com=2, adjust=False).mean()
            df['D_9_3'] = df['K_9_3'].ewm(com=2, adjust=False).mean()
            df['J_9_3'] = 3 * df['K_9_3'] - 2 * df['D_9_3']

            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI_14'] = 100 - (100 / (1 + rs))

            return df.to_dict('records')

        except Exception as e:
            return []

    def _get_realtime_quote(self, stock_code: str) -> Dict:
        """获取实时行情（简化版）"""
        try:
            full_code = f"sh{stock_code}" if stock_code.startswith('6') else f"sz{stock_code}"
            url = f'https://web.sqt.gtimg.cn/q={full_code}'
            r = requests.get(url, timeout=10)

            parts = r.text.split('="')
            if len(parts) < 2:
                return {}

            data = parts[1].strip('";').split('~')

            return {
                "turnover_rate": float(data[38]) if len(data) > 38 and data[38] else 0
            }
        except:
            return {}

    def _score_patterns(self, df: pd.DataFrame) -> int:
        """K线形态评分（简化版）"""
        if len(df) < 5:
            return 0

        score = 0
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        close = latest['close']
        open_price = latest['open']
        prev_close = prev['close']

        # 大阳线
        change_pct = (close - prev_close) / prev_close * 100 if prev_close > 0 else 0
        if change_pct > 5:
            score += 3
        elif change_pct > 3:
            score += 2

        # 连续上涨
        recent_5 = df.tail(5)
        up_days = sum(1 for _, row in recent_5.iterrows() if row['close'] > row['open'])
        if up_days >= 4:
            score += 2

        return min(score, 5)


def main():
    parser = argparse.ArgumentParser(description='股票智能推荐')
    parser.add_argument('--limit', '-l', type=int, default=10, help='推荐数量')
    parser.add_argument('--min-cap', type=float, help='最小市值（亿）')
    parser.add_argument('--max-cap', type=float, help='最大市值（亿）')
    parser.add_argument('--industry', nargs='+', help='行业列表')
    parser.add_argument('--min-score', type=int, default=60, help='最低评分')
    parser.add_argument('--output', '-o', help='输出文件路径')

    args = parser.parse_args()

    recommender = StockRecommender(
        min_cap=args.min_cap,
        max_cap=args.max_cap,
        industries=args.industry,
        min_score=args.min_score
    )

    print("开始推荐股票...", file=sys.stderr)
    recommendations = recommender.recommend(limit=args.limit)

    result = {
        "generate_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "filters": {
            "limit": args.limit,
            "min_cap": args.min_cap,
            "max_cap": args.max_cap,
            "industries": args.industry,
            "min_score": args.min_score
        },
        "count": len(recommendations),
        "recommendations": recommendations
    }

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"推荐结果已保存到 {args.output}", file=sys.stderr)
        print(f"共推荐 {len(recommendations)} 只股票", file=sys.stderr)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
