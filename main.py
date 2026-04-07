import akshare as ak
import pandas as pd
import datetime

def liang_61_radar_v2():
    print("🚀 正在启动梁氏 6.1 增强型猎妖雷达...")
    
    # 1. 抓取全 A 股实时快照
    df = ak.stock_zh_a_spot_em()
    
    # 2. 基础财务与形态过滤 (50-150亿市值 + 3%-7.5%涨幅)
    df['市值_亿'] = df['总市值'] / 1e8
    mask = (df['市值_亿'] >= 50) & (df['市值_亿'] <= 150) & \
           (df['涨跌幅'] >= 3.0) & (df['涨跌幅'] <= 7.5)
    targets = df[mask].copy()

    if targets.empty:
        with open("index.html", "w") as f: f.write("<h1>今日暂无符合 6.1 准则标的</h1>")
        return

    # 3. 动态时间加权算法 (解决成交额预估问题)
    now = datetime.datetime.now()
    # 计算当前已交易分钟数 (简单处理：9:30-11:30, 13:00-15:00)
    if now.hour < 12:
        minutes = max(1, (now.hour - 9) * 60 + now.minute - 30)
    else:
        minutes = max(120, 120 + (now.hour - 13) * 60 + now.minute)
    minutes = min(240, minutes) # 上限 240 分钟

    # 梁氏核心：全天预估成交额必须 > 5亿
    targets['预估全天成交'] = (targets['成交额'] / minutes) * 240
    targets = targets[targets['预估全天成交'] >= 500000000].copy()

    # 4. 量能共振过滤：量比必须 > 1.8 且 < 5.0 (防止巨量对敲)
    targets = targets[(targets['量比'] >= 1.8) & (targets['量比'] <= 5.0)]

    # 5. 输出精简报告
    if not targets.empty:
        # 整理展示字段：名称、涨幅、市值、预估全天成交(亿)
        targets['预估全天成交_亿'] = (targets['预估全天成交'] / 1e8).round(2)
        final_out = targets[['代码','名称','涨跌幅','最新价','市值_亿','预估全天成交_亿','量比']]
        final_out.to_html('index.html', index=False, border=1, justify='center')
        print(f"✅ 扫描完毕，发现 {len(final_out)} 只潜力标的。")
    else:
        with open("index.html", "w") as f: f.write("<h1>量能未达标，暂无 A 级标的。</h1>")

if __name__ == "__main__":
    liang_61_radar_v2()
