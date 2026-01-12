# 🚀 Minimi Trading Bot 빠른 시작 가이드

## 📋 목차
1. [환경 설정](#1-환경-설정)
2. [모의 투자 시작](#2-모의-투자-시작)
3. [대시보드 확인](#3-대시보드-확인)
4. [자동 매매 스케줄러](#4-자동-매매-스케줄러)
5. [실전 전환](#5-실전-전환)

---

## 1️⃣ 환경 설정

### Step 1: 저장소 클론 (이미 완료)
```bash
cd /home/user/webapp
pwd  # /home/user/webapp 확인
```

### Step 2: 의존성 설치 (이미 완료)
```bash
pip install -r requirements.txt
```

✅ **설치된 패키지:**
- pyupbit (업비트 API)
- python-dotenv (환경변수)
- loguru (로깅)
- schedule (스케줄링)
- flask (대시보드)
- pandas (데이터 분석)

### Step 3: 환경변수 파일 생성
```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env

# 에디터로 .env 편집
nano .env
```

**모의 투자용 .env 설정:**
```bash
# 트레이딩 모드
TRADE_MODE=paper

# 대상 코인
TICKER=KRW-BTC

# RSI 설정
RSI_PERIOD=14

# 매매 설정
TRADE_AMOUNT_KRW=10000.0
MAX_INVEST_RATIO=0.30

# 손절/익절 (최적화된 값)
STOP_LOSS_PCT=0.02      # -2%
TAKE_PROFIT_PCT=0.01    # +1%

# 일일 손실 한도
DAILY_LOSS_LIMIT_PCT=0.05

# 페이퍼 트레이딩 설정
PAPER_INITIAL_KRW=1000000.0
PAPER_STATE_FILE=paper_account.json

# 로그 파일
LOG_FILE=trades.log

# 업비트 API (모의 투자에서는 불필요)
UPBIT_ACCESS_KEY=
UPBIT_SECRET_KEY=
```

---

## 2️⃣ 모의 투자 시작

### 방법 1: 수동 실행 (테스트용)
```bash
cd /home/user/webapp
python main.py
```

**실행 결과 예시:**
```
2026-01-06 22:15:30 | INFO | Fetching KRW-BTC data...
2026-01-06 22:15:31 | INFO | RSI: 67.31
2026-01-06 22:15:31 | INFO | Signal: hold
2026-01-06 22:15:31 | INFO | No action taken
```

### 방법 2: 통합 스크립트 실행 (권장)
```bash
cd /home/user/webapp
./start_bot.sh
```

**start_bot.sh가 하는 일:**
1. 환경 검증 (.env 파일 확인)
2. 대시보드 시작 (포트 5000)
3. 자동 매매 스케줄러 시작 (5분마다)
4. 로그 실시간 모니터링

### 방법 3: 백그라운드 실행 (장기 운영)
```bash
cd /home/user/webapp
nohup ./start_bot.sh > bot.log 2>&1 &
```

---

## 3️⃣ 대시보드 확인

### 대시보드 접속
```
🌐 공개 URL: https://5000-itmmk52w3tawc17opzwxr-3844e1b6.sandbox.novita.ai
🏠 로컬 URL: http://localhost:5000
```

### 대시보드 화면
```
┌─────────────────────────────────────────────┐
│   Minimi Trading Bot Dashboard              │
│   🟢 PAPER MODE | KRW-BTC | RSI 14          │
└─────────────────────────────────────────────┘

┌───────────┬───────────┬───────────┬───────────┐
│ 💰 총자산  │ 📈 수익률  │ 🎯 승률   │ 💵 현금   │
│ 1,000,000 │   0.00%   │    -      │ 1,000,000 │
└───────────┴───────────┴───────────┴───────────┘

📊 가격 차트 (실시간)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[라인 차트: BTC/KRW 가격 추이]

📉 RSI 차트 (실시간)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[라인 차트: RSI(14) 지표]
🔴 70 (과매수)
🟡 50 (중립)
🟢 30 (과매도)

📋 거래 내역 (최근 10건)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
시간     | 신호 | 가격      | 수량   | 손익
──────────────────────────────────────────
(아직 거래 없음)
```

### 대시보드 상태 확인
```bash
# 프로세스 확인
ps aux | grep dashboard

# 로그 확인
tail -f dashboard.log

# API 테스트
curl http://localhost:5000/api/status
```

---

## 4️⃣ 자동 매매 스케줄러

### 스케줄러 시작
```bash
cd /home/user/webapp
python scheduler.py
```

**스케줄러 동작:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Minimi Trading Bot Scheduler
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mode: paper
Ticker: KRW-BTC
Schedule: Every 5 minutes

🕐 Next run: 2026-01-06 22:20:00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2026-01-06 22:15:30 | INFO | Starting trading job...
2026-01-06 22:15:31 | INFO | RSI: 67.31 | Signal: hold
2026-01-06 22:15:31 | INFO | Job completed

⏰ Waiting for next run...
```

### 스케줄 설정 변경
`scheduler.py` 파일 수정:
```python
# 5분마다 실행
schedule.every(5).minutes.do(trading_job)

# 1분마다 실행 (빈번한 거래)
schedule.every(1).minutes.do(trading_job)

# 15분마다 실행 (안정적)
schedule.every(15).minutes.do(trading_job)

# 특정 시간에 실행
schedule.every().day.at("09:00").do(trading_job)
```

---

## 5️⃣ 실전 전환

### Step 1: 모의 투자 결과 검증
**최소 1주일 이상 운영 후 확인:**
```bash
cd /home/user/webapp
python report.py
```

**검증 기준:**
- ✅ 승률 70% 이상
- ✅ 누적 수익률 플러스
- ✅ MDD(최대 낙폭) -5% 이내
- ✅ 위험/보상 비율 1.0 이상

### Step 2: 업비트 API 키 발급
1. 업비트 웹사이트 로그인
2. 고객센터 → Open API 관리
3. Open API Key 발급
   - ✅ 자산 조회
   - ✅ 주문 조회
   - ✅ 주문하기
4. API Access Key, Secret Key 복사

**자세한 가이드:** `UPBIT_API_GUIDE.md` 참고

### Step 3: API 키 테스트
```bash
cd /home/user/webapp

# .env 파일 편집
nano .env

# API 키 입력
UPBIT_ACCESS_KEY=your_access_key_here
UPBIT_SECRET_KEY=your_secret_key_here

# API 연결 테스트
python test_upbit_api.py
```

**정상 출력:**
```
✅ Upbit API 연결 성공!
계정 정보:
  KRW 잔고: 50,000원
  보유 코인: 0
```

### Step 4: 실전 모드 전환
```bash
# .env 파일 수정
nano .env
```

**실전용 .env 설정:**
```bash
# 트레이딩 모드를 real로 변경
TRADE_MODE=real

# 소액으로 시작
TRADE_AMOUNT_KRW=10000.0

# 나머지는 동일
TICKER=KRW-BTC
RSI_PERIOD=14
STOP_LOSS_PCT=0.02
TAKE_PROFIT_PCT=0.01
MAX_INVEST_RATIO=0.30
DAILY_LOSS_LIMIT_PCT=0.05

# 업비트 API (필수!)
UPBIT_ACCESS_KEY=your_access_key
UPBIT_SECRET_KEY=your_secret_key
```

### Step 5: 실전 매매 시작
```bash
# 테스트 실행 (1회만)
python main.py

# 정상 동작 확인 후 스케줄러 시작
./start_bot.sh
```

⚠️ **주의사항:**
1. 반드시 소액(1만원)으로 시작
2. 최소 1주일 실전 테스트
3. 안정성 확인 후 금액 증액
4. 일일 손실 한도 준수

---

## 📊 모니터링 체크리스트

### 매일 확인할 것
- [ ] 대시보드 접속하여 상태 확인
- [ ] 총 자산 및 수익률 확인
- [ ] 거래 내역 검토
- [ ] 로그 파일 확인 (`tail -f trades.log`)

### 매주 확인할 것
- [ ] 백테스트 리포트 실행 (`python report.py`)
- [ ] 승률 및 위험/보상 비율 확인
- [ ] 전략 파라미터 조정 필요 여부 판단
- [ ] paper_account.json 백업

### 매월 확인할 것
- [ ] 월간 수익률 계산
- [ ] 전략 성과 분석
- [ ] 시장 환경 변화 대응
- [ ] 코드 업데이트 확인

---

## 🛠️ 트러블슈팅

### 문제 1: 봇이 실행되지 않아요
```bash
# 환경 확인
python --version  # Python 3.7 이상
pip list | grep pyupbit

# 로그 확인
cat trades.log

# 에러 메시지 확인
python main.py
```

### 문제 2: API 에러가 발생해요
```bash
# API 키 확인
python test_upbit_api.py

# .env 파일 확인
cat .env | grep UPBIT

# 권한 확인 (업비트 웹사이트에서)
```

### 문제 3: 대시보드가 안 열려요
```bash
# 프로세스 확인
ps aux | grep dashboard

# 포트 확인
netstat -tuln | grep 5000

# 재시작
pkill -f dashboard.py
python dashboard.py
```

### 문제 4: 거래가 실행되지 않아요
```bash
# 신호 확인
python -c "
from strategy import get_signal
import pyupbit
df = pyupbit.get_ohlcv('KRW-BTC', 'minute5', 50)
signal, rsi = get_signal(df, 14)
print(f'RSI: {rsi:.2f}, Signal: {signal}')
"

# 계정 확인
cat paper_account.json
```

---

## 📚 추가 문서

- `README_COMPLETE.md`: 전체 프로젝트 개요
- `DASHBOARD_GUIDE.md`: 대시보드 상세 가이드
- `DEPLOYMENT_PLAN.md`: 배포 및 운영 계획
- `OPERATION_GUIDE.md`: 운영 매뉴얼
- `UPBIT_API_GUIDE.md`: 업비트 API 설정
- `STRATEGY_OPTIMIZATION.md`: 전략 최적화 분석
- `SIMILAR_PROJECTS.md`: 유사 프로젝트 참고자료

---

## ✅ 최종 체크리스트

### 모의 투자 단계
- [x] 환경 설정 완료
- [x] 의존성 설치 완료
- [x] .env 파일 생성 (TRADE_MODE=paper)
- [ ] 수동 실행 테스트 (`python main.py`)
- [ ] 대시보드 확인 (https://5000-...)
- [ ] 스케줄러 실행 (5분마다 자동 매매)
- [ ] 1주일 운영 및 모니터링
- [ ] 리포트 확인 (`python report.py`)

### 실전 전환 단계
- [ ] 모의 투자 검증 완료 (승률 70%+, 수익률 +)
- [ ] 업비트 API 키 발급
- [ ] API 연결 테스트 (`python test_upbit_api.py`)
- [ ] .env 파일 수정 (TRADE_MODE=real)
- [ ] 소액 실전 테스트 (1만원)
- [ ] 1주일 실전 운영
- [ ] 금액 증액 (5만원 → 10만원 → ...)

---

## 🎯 목표 달성 로드맵

### 1주차: 모의 투자 검증
- 목표: 시스템 안정성 확인
- 초기 자금: 1,000,000원 (가상)
- 기대 승률: 70% 이상
- 기대 수익률: +1% 이상

### 2주차: 소액 실전
- 목표: 실전 API 검증
- 초기 자금: 10,000원 (실제)
- 거래 횟수: 10~20회
- 손실 한도: -5% (-500원)

### 3주차: 정식 운영
- 목표: 안정적 수익 창출
- 초기 자금: 50,000원 → 100,000원
- 월간 목표 수익률: +5%
- 지속적 모니터링 및 최적화

---

## 🚀 지금 바로 시작하세요!

```bash
# 1. 프로젝트 디렉토리로 이동
cd /home/user/webapp

# 2. 환경변수 파일 생성
cp .env.example .env

# 3. 통합 스크립트 실행
./start_bot.sh

# 4. 대시보드 접속
open https://5000-itmmk52w3tawc17opzwxr-3844e1b6.sandbox.novita.ai
```

**축하합니다! 🎉**  
Minimi Trading Bot이 자동으로 매매를 시작합니다!

---

**문의:** GitHub Issues - https://github.com/lcmin16-prog/minimi/issues  
**프로젝트:** https://github.com/lcmin16-prog/minimi  
**작성일:** 2026-01-06
