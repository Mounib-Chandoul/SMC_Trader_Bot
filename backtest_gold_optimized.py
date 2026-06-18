import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, time

def backtest_optimized_smc_gold(symbol="GC=F", period="1y", interval="1h"):
    print(f"Downloading data for {symbol} (1 year, 1h interval)...")
    df = yf.download(symbol, period=period, interval=interval)
    if df.empty: return
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

    # EMA 20 for Baseline Trend
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()

    trades = []
    london_start, ny_start = time(8, 0), time(13, 0)
    
    df['date'] = df.index.date
    dates = df['date'].unique()
    
    for date in dates:
        day_data = df[df['date'] == date].copy()
        for start_time in [london_start, ny_start]:
            session_data = day_data[day_data.index.time >= start_time]
            if session_data.empty: continue
            
            # --- FULL SMC LOGIC ---
            lookback = df[df.index < session_data.index[0]].tail(24)
            if len(lookback) < 5: continue
            
            recent_high = float(lookback['High'].max())
            recent_low = float(lookback['Low'].min())
            
            fvg_bullish = any(float(lookback['Low'].iloc[i]) > float(lookback['High'].iloc[i-2]) for i in range(2, len(lookback)))
            fvg_bearish = any(float(lookback['High'].iloc[i]) < float(lookback['Low'].iloc[i-2]) for i in range(2, len(lookback)))
            
            entry_candle = session_data.iloc[0]
            price = float(entry_candle['Open'])
            ema = float(entry_candle['EMA20'])
            
            direction = None
            if price >= (recent_high * 0.999) and price > ema and fvg_bullish:
                direction = "LONG"
            elif price <= (recent_low * 1.001) and price < ema and fvg_bearish:
                direction = "SHORT"
            
            if direction:
                # OPTIMIZED RISK PARAMETERS (30% TP1 / 70% TP2)
                risk_pts = 10.0
                tp1_pts = 10.0  
                tp2_pts = 30.0  
                partial_pct = 0.30 # Only close 30% at TP1
                
                entry_p = price
                sl_p = entry_p - risk_pts if direction == "LONG" else entry_p + risk_pts
                tp1_p = entry_p + tp1_pts if direction == "LONG" else entry_p - tp1_pts
                tp2_p = entry_p + tp2_pts if direction == "LONG" else entry_p - tp2_pts
                
                tp1_hit = False
                result = None
                profit = 0.0
                
                future = df[df.index > session_data.index[0]].head(48)
                
                for _, c in future.iterrows():
                    h, l = float(c['High']), float(c['Low'])
                    
                    if direction == "LONG":
                        if not tp1_hit and h >= tp1_p:
                            tp1_hit = True
                            profit += (tp1_pts * partial_pct) 
                            sl_p = entry_p # Break Even
                        
                        if l <= sl_p:
                            if not tp1_hit:
                                result, profit = "LOSS", -risk_pts
                            else:
                                result = "TP1 + BE"
                            break
                        
                        if h >= tp2_p:
                            result = "FULL WIN"
                            profit += (tp2_pts * (1 - partial_pct)) 
                            break
                            
                    else: # SHORT
                        if not tp1_hit and l <= tp1_p:
                            tp1_hit = True
                            profit += (tp1_pts * partial_pct)
                            sl_p = entry_p
                            
                        if h >= sl_p:
                            if not tp1_hit:
                                result, profit = "LOSS", -risk_pts
                            else:
                                result = "TP1 + BE"
                            break
                            
                        if l <= tp2_p:
                            result = "FULL WIN"
                            profit += (tp2_pts * (1 - partial_pct))
                            break
                
                if result:
                    trades.append({
                        "Date": date, "Dir": direction, "Res": result, 
                        "Profit": profit
                    })

    return pd.DataFrame(trades)

if __name__ == "__main__":
    res = backtest_optimized_smc_gold()
    if res is not None and not res.empty:
        print("\n--- Optimized SMC Gold (30% TP1 / 70% TP2) ---")
        print(f"Total Trades: {len(res)}")
        print(f"Full Wins (TP2): {len(res[res['Res']=='FULL WIN'])}")
        print(f"Break-Even Trades: {len(res[res['Res']=='TP1 + BE'])}")
        print(f"Total Losses: {len(res[res['Res']=='LOSS'])}")
        print(f"Total Yearly Profit: {res['Profit'].sum():.2f} points")
    else: print("No setups found.")
