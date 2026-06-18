import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, time

def backtest_optimized_smc_forex(symbol="EURUSD=X", period="1y", interval="1h"):
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
            # Standard Forex sensitivity (0.0001 = 1 pip)
            if price >= (recent_high * 0.9998) and price > ema and fvg_bullish:
                direction = "LONG"
            elif price <= (recent_low * 1.0002) and price < ema and fvg_bearish:
                direction = "SHORT"
            
            if direction:
                # FOREX RISK PARAMETERS (Scaled for EURUSD)
                # Let's use 15 pips SL / 45 pips TP2 (standard for 1h chart)
                risk_pips = 0.0015
                tp1_pips = 0.0015  
                tp2_pips = 0.0045  
                partial_pct = 0.30 
                
                entry_p = price
                sl_p = entry_p - risk_pips if direction == "LONG" else entry_p + risk_pips
                tp1_p = entry_p + tp1_pips if direction == "LONG" else entry_p - tp1_pips
                tp2_p = entry_p + tp2_pips if direction == "LONG" else entry_p - tp2_pips
                
                tp1_hit = False
                result = None
                profit_pips = 0.0
                
                future = df[df.index > session_data.index[0]].head(48)
                
                for _, c in future.iterrows():
                    h, l = float(c['High']), float(c['Low'])
                    
                    if direction == "LONG":
                        if not tp1_hit and h >= tp1_p:
                            tp1_hit = True
                            profit_pips += (tp1_pips * partial_pct) 
                            sl_p = entry_p # BE
                        
                        if l <= sl_p:
                            if not tp1_hit:
                                result, profit_pips = "LOSS", -risk_pips
                            else:
                                result = "TP1 + BE"
                            break
                        
                        if h >= tp2_p:
                            result = "FULL WIN"
                            profit_pips += (tp2_pips * (1 - partial_pct)) 
                            break
                            
                    else: # SHORT
                        if not tp1_hit and l <= tp1_p:
                            tp1_hit = True
                            profit_pips += (tp1_pips * partial_pct)
                            sl_p = entry_p
                            
                        if h >= sl_p:
                            if not tp1_hit:
                                result, profit_pips = "LOSS", -risk_pips
                            else:
                                result = "TP1 + BE"
                            break
                            
                        if l <= tp2_p:
                            result = "FULL WIN"
                            profit_pips += (tp2_pips * (1 - partial_pct))
                            break
                
                if result:
                    trades.append({
                        "Date": date, "Dir": direction, "Res": result, 
                        "Profit_Pips": profit_pips * 10000 # Convert to Pips
                    })

    return pd.DataFrame(trades)

if __name__ == "__main__":
    res = backtest_optimized_smc_forex()
    if res is not None and not res.empty:
        print("\n--- Optimized SMC EUR/USD Results ---")
        print(f"Total Trades: {len(res)}")
        print(f"Full Wins (TP2): {len(res[res['Res']=='FULL WIN'])}")
        print(f"Break-Even Trades: {len(res[res['Res']=='TP1 + BE'])}")
        print(f"Total Losses: {len(res[res['Res']=='LOSS'])}")
        print(f"Total Yearly Profit: {res['Profit_Pips'].sum():.1f} pips")
    else: print("No setups found for EUR/USD.")
