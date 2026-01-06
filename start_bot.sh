#!/bin/bash

# Minimi Trading Bot 실행 스크립트

echo "================================================"
echo "  Minimi Trading Bot - Startup Script"
echo "================================================"
echo ""

# 1. 프로젝트 디렉토리로 이동
cd /home/user/webapp || exit 1

# 2. 가상환경 활성화 (있는 경우)
if [ -d ".venv" ]; then
    echo "✅ Activating virtual environment..."
    source .venv/bin/activate
fi

# 3. 의존성 확인
echo "✅ Checking dependencies..."
python -c "import pyupbit, loguru, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing dependencies..."
    pip install -r requirements.txt
fi

# 4. .env 파일 확인
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "Please create .env file with the following content:"
    echo "----------------------------------------"
    cat << 'EOF'
UPBIT_ACCESS_KEY=your_access_key_here
UPBIT_SECRET_KEY=your_secret_key_here
TRADE_MODE=paper
TICKER=KRW-BTC
RSI_PERIOD=14
TRADE_AMOUNT_KRW=10000.0
STOP_LOSS_PCT=0.02
TAKE_PROFIT_PCT=0.01
PAPER_INITIAL_KRW=1000000.0
PAPER_STATE_FILE=paper_account.json
LOG_FILE=trades.log
CANDLE_INTERVAL=minute5
MAX_INVEST_RATIO=0.30
DAILY_LOSS_LIMIT_PCT=0.05
EOF
    echo "----------------------------------------"
    exit 1
fi

echo "✅ .env file found"

# 5. 모드 확인
TRADE_MODE=$(grep TRADE_MODE .env | cut -d '=' -f2)
echo ""
echo "📊 Trading Mode: $TRADE_MODE"

if [ "$TRADE_MODE" == "real" ]; then
    echo "⚠️  ⚠️  ⚠️  WARNING: REAL TRADING MODE ⚠️  ⚠️  ⚠️"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

echo ""
echo "================================================"
echo "  Starting Services"
echo "================================================"
echo ""

# 6. 백그라운드에서 대시보드 실행
echo "🌐 Starting dashboard at http://localhost:5000"
nohup python dashboard.py > dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "   Dashboard PID: $DASHBOARD_PID"

# 잠시 대기
sleep 2

# 7. 스케줄러 실행
echo "⏱️  Starting scheduler (5-minute intervals)"
python scheduler.py

# 8. 종료 시 대시보드도 종료
kill $DASHBOARD_PID 2>/dev/null

echo ""
echo "================================================"
echo "  Services Stopped"
echo "================================================"
