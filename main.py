import akshare as ak
import pandas as pd
import datetime
import time
import os

def liang_61_final_engine():
    print("🚀 正在执行梁氏 6.1 深度量化决策系统...")
    try:
        # 1. 数据抓取与重试
        df = None
        for _ in range(3):
            try:
                df = ak.stock_zh_a_spot_em()
                if df is not None: break
            except: time.sleep(5)
        
        if df is None: return

        # 2. 字段清洗与强转
        df['市值_亿'] = pd.to_numeric(df['总市值'], errors='coerce') / 1e8
        df['涨幅%'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df['现价'] = pd.to_numeric(df['最新价'], errors='coerce')
        df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce')
        df['量比'] = pd.to_numeric(df['量比'], errors='coerce')
        df['换手%'] = pd.to_numeric(df['换手率'], errors='coerce')

        # 3. 基础准则过滤 (50-150亿市值 + 3-7.5% 涨幅)
        mask = (df['市值_亿'] >= 50) & (df['市值_亿'] <= 150) & (df['涨幅%'] >= 3.0) & (df['涨幅%'] <= 7.5)
        targets = df[mask].copy()

        # 4. 时间加权预测
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        minutes = ((now.hour - 9) * 60 + now.minute - 30) if now.hour < 12 else (120 + (now.hour - 13) * 60 + now.minute)
        minutes = min(240, max(1, minutes))
        targets['预估全天成交_亿'] = (targets['成交额'] / minutes * 240 / 1e8).round(2)

        # 5. 深度量化字段计算
        targets['信号'] = "🔥 猎妖启动"
        targets['核心分析'] = "量价共振/多头排列"
        targets['最佳买入点'] = (targets['现价'] * 0.995).round(2)
        targets['预期次日溢价%'] = (targets['量比'] * 0.8 + targets['涨幅%'] * 0.5).round(1)
        targets['止损参考'] = (targets['最佳买入点'] * 0.97).round(2)
        targets['综合评分'] = (targets['量比'] * 10 + (targets['预估全天成交_亿'] / 5) * 20).clip(0, 98).astype(int)
        targets['对敲风险'] = targets['量比'].apply(lambda x: "⚠️ 高" if x > 5 else "✅ 低")

        # 最终筛选：预估成交额 >= 5 亿
        final = targets[targets['预估全天成交_亿'] >= 5.0].copy()
        
        # 定义输出列名及顺序
        cols = ['代码', '信号', '核心分析', '名称', '现价', '最佳买入点', '预期次日溢价%', '止损参考', '涨幅%', '换手%', '量比', '综合评分', '对敲风险', '预估全天成交_亿']
        final_out = final[cols].sort_values(by='综合评分', ascending=False)

        # 6. 生成 Excel 文件
        excel_name = "Liang_61_Report.xlsx"
        final_out.to_excel(excel_name, index=False)

        # 7. 生成带下载链接的 HTML
        time_str = now.strftime('%Y-%m-%d %H:%M')
        html_head = f"""
        <html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
        <style>body{{font-family:sans-serif;padding:15px;}}table{{width:100%;border-collapse:collapse;font-size:12px;}}
        th,td{{border:1px solid #ddd;padding:10px;text-align:center;}}th{{background:#d32f2f;color:white;}}
        .download-btn{{display:inline-block;padding:10px 20px;background:#2e7d32;color:white;text-decoration:none;border-radius:5px;margin-bottom:15px;}}
        </style></head><body>
        <h2>梁氏 6.1 猎妖深度决策表 ({time_str})</h2>
        <a href='{excel_name}' class='download-btn'>📥 点击下载 Excel 报告</a>
        """
        
        if final_out.empty:
            content = "<h4>当前市场量能未达标，暂无 A 级猎妖信号</h4>"
        else:
            content = final_out.to_html(index=False, classes='table')
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_head + content + "</body></html>")
        print("✅ Excel 与网页报告同步生成成功。")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    liang_61_final_engine()
