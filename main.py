import akshare as ak
import pandas as pd
import datetime
import time

def liang_61_engine():
    print("🚀 启动梁氏 6.1 猎妖扫描...")
    try:
        # 1. 强效抓取 (带 3 次重试)
        df = None
        for _ in range(3):
            try:
                df = ak.stock_zh_a_spot_em()
                if df is not None: break
            except: time.sleep(5)
        
        if df is None: raise Exception("数据接口超时")

        # 2. 字段类型强转
        df['市值_亿'] = pd.to_numeric(df['总市值'], errors='coerce') / 1e8
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce')

        # 3. 核心准则过滤 (50-150亿市值 + 3%-7.5%涨幅)
        mask = (df['市值_亿'] >= 50) & (df['市值_亿'] <= 150) & \
               (df['涨跌幅'] >= 3.0) & (df['涨跌幅'] <= 7.5)
        targets = df[mask].copy()

        # 4. 时间加权预测 (校准北京时间)
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        if now.hour < 12:
            minutes = max(1, (now.hour - 9) * 60 + now.minute - 30)
        else:
            minutes = max(120, 120 + (now.hour - 13) * 60 + now.minute)
        minutes = min(240, minutes)
        
        # 5. 梁氏猎妖线：预估全天成交 >= 5亿
        targets['预估全天成交_亿'] = (targets['成交额'] / minutes * 240 / 1e8).round(2)
        final = targets[targets['预估全天成交_亿'] >= 5.0].copy()

        # 6. 生成响应式网页报告
        time_str = now.strftime('%Y-%m-%d %H:%M')
        html_head = f"<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:sans-serif;padding:10px;}}table{{width:100%;border-collapse:collapse;margin-top:10px;}}th,td{{border:1px solid #ddd;padding:12px;text-align:center;}}th{{background:#f2f2f2;}}tr:nth-child(even){{background:#fafafa;}}</style></head><body><h2>梁氏 6.1 猎妖结果 ({time_str})</h2>"
        
        if final.empty:
            content = "<h3>今日暂未发现符合准则标的 (50-150亿 & 3%-7.5% & 5亿量)</h3>"
        else:
            # 增加展示字段：量比
            final_out = final[['代码','名称','最新价','涨跌幅','市值_亿','预估全天成交_亿','量比']]
            content = final_out.to_html(index=False)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_head + content + "</body></html>")
        print("✅ 扫描完成。")
            
    except Exception as e:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(f"系统运行异常: {str(e)}")

if __name__ == "__main__":
    liang_61_engine()
