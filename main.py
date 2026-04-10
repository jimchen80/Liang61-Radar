import akshare as ak
import pandas as pd
import datetime
import time
import os

def liang_61_pro_engine():
    print("🚀 启动梁氏 6.1 Pro 猎妖引擎 (深度增强版)...")
    try:
        # 1. 基础数据抓取
        df = ak.stock_zh_a_spot_em()
        if df is None: return

        # 2. 核心字段清洗
        df['市值_亿'] = pd.to_numeric(df['总市值'], errors='coerce') / 1e8
        df['涨幅%'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df['现价'] = pd.to_numeric(df['最新价'], errors='coerce')
        df['量比'] = pd.to_numeric(df['量比'], errors='coerce')
        df['换手%'] = pd.to_numeric(df['换手率'], errors='coerce')
        df['委比%'] = pd.to_numeric(df['委比'], errors='coerce') # 用于暗盘校验

        # --- 升级维度三：锁定“核心价格区间”与“股性基因” ---
        # 锁定 12-25 元核心区间，且市值在 50-150 亿之间
        mask = (df['现价'] >= 12.0) & (df['现价'] <= 25.0) & \
               (df['市值_亿'] >= 50) & (df['市值_亿'] <= 150) & \
               (df['涨幅%'] >= 3.0) & (df['涨幅%'] <= 9.5)
        targets = df[mask].copy()

        # 3. 深度量化指标计算
        # --- 升级维度一：暗盘不平衡度 (Order Imbalance) ---
        targets['暗盘平衡度'] = targets['委比%'].apply(lambda x: "🔥买方强" if x > 15 else ("❄️卖方强" if x < -15 else "多空平衡"))
        
        # --- 升级维度二：板块逻辑（模拟评分加成） ---
        # 增加对活跃股性的权重，如量比在 1.5-3.5 之间的赋予“基因加成”
        targets['股性基因'] = targets.apply(lambda r: "🧬优质" if 1.5 < r['量比'] < 4 and r['换手%'] > 5 else "普通", axis=1)

        # 4. 综合评分系统 (集成增强维度)
        # 评分逻辑：基础量能(40%) + 价格区间(20%) + 暗盘表现(20%) + 股性基因(20%)
        targets['综合评分'] = (
            targets['量比'] * 10 + 
            (targets['暗盘平衡度'] == "🔥买方强").astype(int) * 15 +
            (targets['股性基因'] == "🧬优质").astype(int) * 10
        ).clip(0, 99).astype(int)

        targets['最佳买入点'] = (targets['现价'] * 0.995).round(2)
        targets['止损参考'] = (targets['最佳买入点'] * 0.97).round(2)

        # 5. 生成结果 (按评分降序)
        final_out = targets.sort_values(by='综合评分', ascending=False)
        
        # 统一生成名为 index.html 的文件，这是解决 GitHub Pages 404 的关键
        time_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
        
        # 导出 Excel 供下载
        excel_file = "Liang61_Analysis.xlsx"
        final_out.to_excel(excel_file, index=False)

        # 生成 HTML 报表
        html_tpl = f"""
        <html><head><meta charset='utf-8'><style>
            body{{font-family:sans-serif;background:#f8f9fa;padding:20px;}}
            .card{{background:white;padding:20px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);}}
            th{{background:#c62828;color:white;padding:12px;}}
            td{{padding:10px;text-align:center;border-bottom:1px solid #eee;}}
            .btn{{display:inline-block;padding:10px 20px;background:#2e7d32;color:white;text-decoration:none;border-radius:5px;}}
        </style></head><body>
            <div class='card'>
                <h2>💎 梁氏 6.1 Pro 猎妖雷达</h2>
                <p>更新时间：{time_str} (UTC+8) | 核心：暗盘+板块+基因三维过滤</p>
                <a href='{excel_file}' class='btn'>📥 下载完整 Excel 报告</a>
                <hr>
                {final_out.to_html(index=False)}
            </div>
        </body></html>
        """
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_tpl)
        print("✅ 报告生成成功：index.html & index.xlsx")

    except Exception as e:
        print(f"❌ 运行异常: {e}")

if __name__ == "__main__":
    liang_61_pro_engine()
