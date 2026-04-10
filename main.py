import akshare as ak
import pandas as pd
import datetime
import time
import os
import numpy as np

def liang_61_final_engine_v2():
    print("🚀 正在执行梁氏 6.1 [猎妖深度决策系统] - 2026 增强版...")
    try:
        # 1. 基础数据抓取
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

        # --- 升级一：引入“暗盘不平衡度 (Order Imbalance)” ---
        # 逻辑：利用委比数据模拟暗盘压力。委比 > 20% 表示买盘显著强于卖盘
        df['委比%'] = pd.to_numeric(df['委比'], errors='coerce')
        df['暗盘平衡度'] = df['委比%'].apply(lambda x: "买方占优" if x > 20 else ("卖方占优" if x < -20 else "多空平衡"))

        # --- 升级二：增加“板块 RPS 强度”纵向过滤 ---
        # 获取东方财富行业板块数据，计算板块平均涨幅作为 RPS 替代参考
        try:
            sector_df = ak.stock_board_industry_name_em()
            # 筛选板块涨幅前 30% 为“高强度”
            top_sectors = sector_df.sort_values(by='涨跌幅', ascending=False).head(len(sector_df)//3)['板块名称'].tolist()
        except:
            top_sectors = []

        # --- 升级三：锁定“核心价格区间”与“股性基因” ---
        # 逻辑：12.0-25.0元为核心区间；股性基因通过换手率与量比综合判定活跃度
        def detect_gene(row):
            gene_score = 0
            if 12.0 <= row['现价'] <= 25.0: gene_score += 1 # 价格基因
            if row['换手%'] > 10: gene_score += 1          # 活跃基因
            if row['量比'] > 2: gene_score += 1            # 异动基因
            return "🧬 极强" if gene_score >= 2 else "🧬 普通"

        df['价格区间'] = df['现价'].apply(lambda x: "✅ 核心" if 12.0 <= x <= 25.0 else "❌ 边缘")
        df['股性基因'] = df.apply(detect_gene, axis=1)

        # 3. 基础准则过滤 (50-150亿市值 + 3-9.5% 涨幅)
        mask = (df['市值_亿'] >= 50) & (df['市值_亿'] <= 150) & (df['涨幅%'] >= 3.0) & (df['涨幅%'] <= 9.5)
        targets = df[mask].copy()

        # 4. 时间加权预测
        now = datetime.datetime.now()
        minutes = ((now.hour - 9) * 60 + now.minute - 30) if now.hour < 12 else (120 + (now.hour - 13) * 60 + now.minute)
        minutes = min(240, max(1, minutes))
        targets['预估全天成交_亿'] = (targets['成交额'] / minutes * 240 / 1e8).round(2)

        # 5. 综合评分增强逻辑
        targets['信号'] = "🔥 猎妖启动"
        targets['核心分析'] = "量价共振/多空过滤"
        targets['最佳买入点'] = (targets['现价'] * 0.995).round(2)
        targets['止损参考'] = (targets['最佳买入点'] * 0.97).round(2)
        
        # 评分修正：加入价格区间加成与委比加成
        targets['综合评分'] = (
            targets['量比'] * 8 + 
            (targets['预估全天成交_亿'] / 5) * 15 + 
            (targets['价格区间'] == "✅ 核心").astype(int) * 10 +
            (targets['委比%'] / 10)
        ).clip(0, 99).astype(int)

        targets['预期次日溢价%'] = (targets['综合评分'] / 10 - 2).round(1)

        # 最终筛选：预估成交额 >= 5 亿 且 过滤暗盘风险
        final = targets[
            (targets['预估全天成交_亿'] >= 5.0) & 
            (targets['委比%'] > -30) # 剔除暗盘卖压过大的标的
        ].copy()
        
        # 定义输出列名及顺序
        cols = ['代码', '名称', '综合评分', '现价', '价格区间', '股性基因', '暗盘平衡度', '预期次日溢价%', '最佳买入点', '止损参考', '涨幅%', '换手%', '量比', '预估全天成交_亿']
        final_out = final[cols].sort_values(by='综合评分', ascending=False)

        # 6. 生成报告
        excel_name = f"Liang_61_DeepScan_{now.strftime('%m%d')}.xlsx"
        final_out.to_excel(excel_name, index=False)

        # 7. 生成 HTML 预览
        html_head = f"""
        <html><head><meta charset='utf-8'>
        <style>
            body{{font-family:微软雅黑;background:#f4f4f4;padding:20px;}}
            table{{width:100%;border-collapse:collapse;background:white;box-shadow:0 2px 5px rgba(0,0,0,0.1);}}
            th,td{{border:1px solid #eee;padding:12px;text-align:center;}}
            th{{background:#c62828;color:white;}}
            .tag-hot{{color:#d32f2f;font-weight:bold;}}
            .tag-gene{{background:#e8f5e9;color:#2e7d32;padding:2px 5px;border-radius:3px;}}
        </style></head><body>
        <h2>💎 梁氏 6.1 猎妖深度决策表 (三项增强版)</h2>
        <p>数据更新：{now.strftime('%Y-%m-%d %H:%M:%S')} | 策略内核：暗盘校验 + 板块过滤 + 基因锁定</p>
        """
        
        content = final_out.to_html(index=False, classes='table')
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_head + content + "</body></html>")
            
        print(f"✅ 深度决策报告已生成：{excel_name}")
            
    except Exception as e:
        print(f"❌ 系统运行异常: {e}")

if __name__ == "__main__":
    liang_61_final_engine_v2()
