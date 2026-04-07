import akshare as ak
import pandas as pd
import datetime
import time

def get_data():
    """解决网络波动，重试 5 次"""
    for _ in range(5):
        try:
            # 抓取实时快照数据
            data = ak.stock_zh_a_spot_em()
            if data is not None and not data.empty:
                return data
        except:
            time.sleep(3)
    return None

def liang_61_radar():
    print("雷达预警启动...")
    try:
        df = get_data()
        if df is None: raise Exception("接口数据抓取失败")

        # 1. 字段清洗：解决部分数据非数值报错
        df['市值_亿'] = pd.to_numeric(df['总市值'], errors='coerce') / 1e8
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce')
        
        # 2. 基础过滤：50-150亿市值 + 3-7.5% 涨幅
        mask = (df['市值_亿'] >= 50) & (df['市值_亿'] <= 150) & \
               (df['涨跌幅'] >= 3.0) & (df['涨跌幅'] <= 7.5)
        targets = df[mask].copy()

        # 3. 动态时间计算（强制同步北京时间）
        now_utc = datetime.datetime.utcnow()
        now_bj = now_utc + datetime.timedelta(hours=8)
        
        # 计算开盘总分钟数
        if now_bj.hour < 12:
            minutes = max(1, (now_bj.hour - 9) * 60 + now_bj.minute - 30)
        else:
            minutes = max(120, 120 + (now_bj.hour - 13) * 60 + now_bj.minute)
        minutes = min(240, minutes)

        # 4. 梁氏 6.1 核心：预测成交额 > 5亿
        targets['预估全天成交_亿'] = (targets['成交额'] / minutes * 240 / 1e8).round(2)
        final = targets[targets['预估全天成交_亿'] >= 5.0].copy()

        # 5. HTML 增强输出（解决乱码，增加自适应布局）
        now_str = now_bj.strftime('%Y-%m-%d %H:%M:%S')
        if final.empty:
            content = f"<h2>{now_str} 扫描：暂无符合 A 级标的</h2>"
        else:
            content = f"<h2>🚀 梁氏 6.1 猎妖结果 ({now_str})</h2>" + \
                      final[['代码','名称','最新价','涨跌幅','市值_亿','预估全天成交_亿','量比']].to_html(index=False, border=1)

        html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:sans-serif;padding:20px;}}table{{width:100%;border-collapse:collapse;}}th,td{{border:1px solid #ddd;padding:8px;text-align:center;}}th{{background:#f2f2f2;}}tr:nth-child(even){{background:#fafafa;}}</style></head><body>{content}</body></html>"
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("报告生成成功。")
        
    except Exception as e:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(f"<h2>系统异常：{str(e)}</h2>")

if __name__ == "__main__":
    liang_61_radar()
