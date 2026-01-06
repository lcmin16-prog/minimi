"""
실시간 트레이딩 대시보드
Flask 기반 웹 인터페이스
"""
from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from config import (
    PAPER_STATE_FILE,
    LOG_FILE,
    TICKER,
    STOP_LOSS_PCT,
    TAKE_PROFIT_PCT,
    RSI_PERIOD,
    TRADE_MODE
)

app = Flask(__name__)


def load_paper_account():
    """페이퍼 계좌 상태 로드"""
    if not os.path.exists(PAPER_STATE_FILE):
        return {
            'krw_balance': 0,
            'coin_amount': 0,
            'avg_buy_price': 0
        }
    
    try:
        with open(PAPER_STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {
            'krw_balance': 0,
            'coin_amount': 0,
            'avg_buy_price': 0
        }


def load_recent_trades(limit=20):
    """최근 거래 내역 로드"""
    if not os.path.exists(LOG_FILE):
        return []
    
    trades = []
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            
        # 최근 거래만 추출
        for line in reversed(lines[-limit*5:]):  # 충분히 많이 읽기
            if 'Order response:' in line or 'Paper result:' in line:
                try:
                    # 타임스탬프 추출
                    timestamp = line.split('|')[0].strip()
                    
                    # JSON 파싱
                    if '{' in line:
                        json_str = line[line.index('{'):line.rindex('}')+1]
                        trade_data = json.loads(json_str)
                        trade_data['timestamp'] = timestamp
                        trades.append(trade_data)
                        
                        if len(trades) >= limit:
                            break
                except Exception:
                    continue
                    
    except Exception as e:
        print(f"Error loading trades: {e}")
    
    return list(reversed(trades[-limit:]))


def calculate_performance():
    """성과 계산"""
    account = load_paper_account()
    initial_krw = 1000000.0  # 초기 자금
    
    current_krw = account.get('krw_balance', 0)
    coin_amount = account.get('coin_amount', 0)
    
    # 현재 가격 가져오기
    try:
        import pyupbit
        current_price = pyupbit.get_current_price(TICKER)
        coin_value = coin_amount * current_price if current_price else 0
    except Exception:
        coin_value = 0
        current_price = 0
    
    total_equity = current_krw + coin_value
    profit = total_equity - initial_krw
    profit_pct = (profit / initial_krw * 100) if initial_krw > 0 else 0
    
    return {
        'total_equity': total_equity,
        'profit': profit,
        'profit_pct': profit_pct,
        'krw_balance': current_krw,
        'coin_value': coin_value,
        'coin_amount': coin_amount,
        'current_price': current_price
    }


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """현재 상태 API"""
    try:
        performance = calculate_performance()
        account = load_paper_account()
        
        return jsonify({
            'success': True,
            'mode': TRADE_MODE,
            'ticker': TICKER,
            'performance': performance,
            'account': account,
            'config': {
                'stop_loss_pct': STOP_LOSS_PCT * 100,
                'take_profit_pct': TAKE_PROFIT_PCT * 100,
                'rsi_period': RSI_PERIOD
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/trades')
def get_trades():
    """거래 내역 API"""
    try:
        limit = request.args.get('limit', 20, type=int)
        trades = load_recent_trades(limit)
        
        return jsonify({
            'success': True,
            'trades': trades,
            'count': len(trades)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chart')
def get_chart_data():
    """차트 데이터 API"""
    try:
        import pyupbit
        
        # OHLCV 데이터
        df = pyupbit.get_ohlcv(TICKER, interval="minute5", count=100)
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': 'No data available'
            }), 500
        
        # RSI 계산
        from strategy import calculate_rsi
        rsi = calculate_rsi(df['close'], RSI_PERIOD)
        
        # 데이터 변환
        chart_data = []
        for idx in range(len(df)):
            timestamp = df.index[idx]
            if hasattr(timestamp, 'to_pydatetime'):
                timestamp = timestamp.to_pydatetime()
            
            chart_data.append({
                'time': timestamp.isoformat(),
                'open': float(df['open'].iloc[idx]),
                'high': float(df['high'].iloc[idx]),
                'low': float(df['low'].iloc[idx]),
                'close': float(df['close'].iloc[idx]),
                'volume': float(df['volume'].iloc[idx]),
                'rsi': float(rsi.iloc[idx]) if idx < len(rsi) and not pd.isna(rsi.iloc[idx]) else None
            })
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/report')
def get_report():
    """리포트 데이터 API"""
    try:
        # trades.csv에서 통계 계산
        if not os.path.exists('trades.csv'):
            return jsonify({
                'success': False,
                'error': 'No trade history'
            }), 404
        
        df = pd.read_csv('trades.csv')
        
        # 매도 거래만 추출
        sell_trades = df[df['signal'] == 'sell']
        
        if len(sell_trades) == 0:
            return jsonify({
                'success': False,
                'error': 'No sell trades yet'
            }), 404
        
        # 통계 계산
        wins = sell_trades[sell_trades['pnl'] > 0]
        losses = sell_trades[sell_trades['pnl'] < 0]
        
        stats = {
            'total_trades': len(sell_trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(sell_trades) * 100 if len(sell_trades) > 0 else 0,
            'total_pnl': float(sell_trades['pnl'].sum()),
            'avg_win': float(wins['pnl'].mean()) if len(wins) > 0 else 0,
            'avg_loss': float(losses['pnl'].mean()) if len(losses) > 0 else 0,
            'max_win': float(wins['pnl'].max()) if len(wins) > 0 else 0,
            'max_loss': float(losses['pnl'].min()) if len(losses) > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # templates 디렉토리 생성
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("="*60)
    print("Minimi Trading Bot Dashboard")
    print("="*60)
    print(f"Mode: {TRADE_MODE}")
    print(f"Ticker: {TICKER}")
    print(f"Strategy: RSI {RSI_PERIOD} (SL: {STOP_LOSS_PCT*100}%, TP: {TAKE_PROFIT_PCT*100}%)")
    print("="*60)
    print("\n🌐 Dashboard URL: http://localhost:5000")
    print("\n⚠️  Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
