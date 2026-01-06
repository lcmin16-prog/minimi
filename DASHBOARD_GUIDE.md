# 📊 Minimi Trading Dashboard 사용 가이드

## 🌐 접속 정보

### 공개 URL (인터넷에서 접속 가능)
```
https://5000-itmmk52w3tawc17opzwxr-3844e1b6.sandbox.novita.ai
```

### 로컬 URL (서버에서만 접속 가능)
```
http://localhost:5000
```

---

## 📱 대시보드 화면 구성

### 1️⃣ 헤더 섹션
- **봇 이름**: Minimi Trading Bot
- **운영 모드**: 
  - 🟢 PAPER MODE (모의 투자)
  - 🔴 REAL MODE (실전 투자)
- **대상 코인**: KRW-BTC (비트코인)
- **전략 정보**: RSI 14 (손절 -2.5%, 익절 +1.5%)

### 2️⃣ 성과 카드 (4개)

#### 💰 총 자산
- 현재 보유 총 자산 (KRW + 코인 가치)
- 초기 자금: 1,000,000원

#### 📈 수익률
- 누적 수익률 (%)
- 실시간 업데이트

#### 🎯 승률
- 수익 거래 / 전체 거래
- 백분율로 표시

#### 💵 현금 잔고
- 현재 KRW 잔액
- 거래 가능 금액

### 3️⃣ 실시간 차트 (2개)

#### 📊 가격 차트 (상단)
- BTC/KRW 가격 추이
- 시간별 가격 변화
- 자동 갱신 (30초)

#### 📉 RSI 차트 (하단)
- RSI(14) 지표 추이
- 과매수/과매도 구간 표시
  - 🔴 RSI ≥ 70: 과매수 (매도 신호)
  - 🟡 30 < RSI < 70: 중립
  - 🟢 RSI ≤ 30: 과매도 (매수 신호)

### 4️⃣ 거래 내역 테이블
- **최근 10건** 거래 내역 표시
- 표시 정보:
  - 시간: 거래 발생 시각
  - 신호: buy (매수) / sell (매도)
  - 가격: 거래 가격
  - 수량: 거래한 BTC 수량
  - 수수료: 거래 수수료
  - 잔고: 거래 후 KRW 잔액
  - 포지션: 보유 BTC 수량
  - 손익: 거래로 인한 손익 (원)

---

## 🔄 자동 갱신 주기

| 항목 | 갱신 주기 |
|------|----------|
| 성과 카드 | 5초 |
| 가격 차트 | 30초 |
| RSI 차트 | 30초 |
| 거래 내역 | 10초 |

---

## 🎮 대시보드 실행 방법

### 방법 1: 통합 스크립트로 실행
```bash
cd /home/user/webapp
./start_bot.sh
```

### 방법 2: 개별 실행
```bash
cd /home/user/webapp
python dashboard.py
```

### 방법 3: 백그라운드 실행
```bash
cd /home/user/webapp
nohup python dashboard.py > dashboard.log 2>&1 &
```

---

## 🛑 대시보드 중지 방법

### 방법 1: 프로세스 찾아서 종료
```bash
ps aux | grep dashboard.py
kill <프로세스_ID>
```

### 방법 2: pkill 사용
```bash
pkill -f dashboard.py
```

---

## 📡 API 엔드포인트

### 1. 상태 조회
```
GET /api/status
```
**응답 예시:**
```json
{
  "success": true,
  "mode": "paper",
  "ticker": "KRW-BTC",
  "account": {
    "krw_balance": 1000000,
    "coin_amount": 0,
    "avg_buy_price": 0
  },
  "performance": {
    "total_equity": 1000000,
    "profit": 0,
    "profit_pct": 0
  },
  "config": {
    "rsi_period": 14,
    "stop_loss_pct": 2.5,
    "take_profit_pct": 1.5
  }
}
```

### 2. 현재 가격 조회
```
GET /api/price
```
**응답 예시:**
```json
{
  "success": true,
  "ticker": "KRW-BTC",
  "price": 135578000,
  "timestamp": "2026-01-06T22:09:56"
}
```

### 3. RSI 지표 조회
```
GET /api/rsi
```
**응답 예시:**
```json
{
  "success": true,
  "ticker": "KRW-BTC",
  "rsi": 67.31,
  "signal": "hold",
  "timestamp": "2026-01-06T22:09:56"
}
```

### 4. 거래 내역 조회
```
GET /api/trades?limit=10
```
**응답 예시:**
```json
{
  "success": true,
  "count": 5,
  "trades": [
    {
      "time": "2026-01-06 22:00:00",
      "signal": "buy",
      "price": 135000000,
      "qty": 0.00007407,
      "fee": 5.0,
      "balance": 990000,
      "position": 0.00007407,
      "pnl": 0
    }
  ]
}
```

### 5. 차트 데이터 조회
```
GET /api/chart_data?period=1h
```
- period: 1h, 6h, 24h
**응답 예시:**
```json
{
  "success": true,
  "ticker": "KRW-BTC",
  "period": "1h",
  "data": {
    "timestamps": ["10:00", "10:05", "10:10"],
    "prices": [135000000, 135100000, 135200000],
    "rsi": [65.2, 66.5, 67.3]
  }
}
```

---

## 🔧 현재 설정 확인

### 현재 적용된 전략 설정
```
전략: RSI(14) 기반 자동매매
손절: -2.5%
익절: +1.5%
매수 신호: RSI ≤ 30
매도 신호: RSI ≥ 70
거래 금액: 10,000원/회
최대 투자 비율: 30%
일일 손실 한도: -5%
```

### 현재 시장 상태 (2026-01-06 22:09 기준)
```
BTC 현재가: 135,578,000원
RSI(14): 67.31
현재 신호: hold (관망)
```

---

## 📊 대시보드 활용 팁

### 1️⃣ 실시간 모니터링
- 대시보드를 열어두고 실시간으로 봇 상태 확인
- RSI 차트를 통해 매매 신호 예측

### 2️⃣ 성과 분석
- 수익률 카드로 전략 효과 확인
- 승률로 전략 안정성 평가
- 거래 내역으로 개별 거래 분석

### 3️⃣ 알고리즘 검증
- 모의 투자 모드에서 충분히 테스트
- 최소 1주일 이상 데이터 수집
- 승률 70% 이상, 수익률 플러스 확인 후 실전 전환

### 4️⃣ 리스크 관리
- 일일 손실 한도 확인
- 보유 포지션 비율 확인
- 손절/익절 자동 발동 확인

---

## ⚠️ 주의사항

### 1. 대시보드는 정보 표시 목적
- 대시보드는 **조회 전용** 도구입니다
- 실제 매매는 `main.py` 또는 `scheduler.py`가 수행
- 대시보드를 닫아도 매매는 계속됩니다

### 2. 자동 갱신 특성
- 대시보드는 자동으로 최신 데이터를 갱신합니다
- 새로고침(F5) 없이도 업데이트됩니다
- 인터넷 연결이 끊기면 갱신이 중단될 수 있습니다

### 3. 포트 충돌 주의
- 포트 5000이 이미 사용 중이면 실행 실패
- 다른 Flask 앱과 포트 충돌 가능
- 필요시 `dashboard.py`에서 포트 변경 가능

### 4. 모바일 접속
- 공개 URL은 모바일에서도 접속 가능
- 반응형 디자인으로 모바일 최적화
- Wi-Fi 또는 데이터 연결 필요

---

## 🚀 다음 단계

### 1주차: 모의 투자 검증
- ✅ 대시보드로 실시간 모니터링
- ✅ 매일 거래 내역 확인
- ✅ 성과 지표 기록

### 2주차: 전략 최적화
- 백테스트 결과와 실시간 결과 비교
- 필요시 손절/익절 구간 조정
- RSI 임계값 튜닝

### 3주차: 실전 전환 준비
- 승률 70% 이상 확인
- 수익률 플러스 확인
- 업비트 API 키 발급 및 등록

---

## 📞 문제 해결

### Q1: 대시보드가 안 열려요
```bash
# 프로세스 확인
ps aux | grep dashboard

# 로그 확인
tail -f dashboard.log

# 재시작
pkill -f dashboard.py
python dashboard.py
```

### Q2: 데이터가 안 보여요
```bash
# API 테스트
curl http://localhost:5000/api/status

# paper_account.json 확인
cat paper_account.json

# 계정 초기화
python -c "from paper_broker import PaperBroker; PaperBroker()"
```

### Q3: 차트가 안 그려져요
- 브라우저 개발자 도구(F12) 열기
- Console 탭에서 에러 확인
- 네트워크 탭에서 API 응답 확인

---

## 📝 결론

Minimi Trading Dashboard는 **실시간 모니터링**과 **성과 분석**을 위한 강력한 도구입니다.

✅ **모의 투자 단계**에서 충분히 검증하고  
✅ **안정적인 수익률**을 확인한 후  
✅ **실전 투자**로 전환하세요!

---

**접속 URL:** https://5000-itmmk52w3tawc17opzwxr-3844e1b6.sandbox.novita.ai

**프로젝트 저장소:** https://github.com/lcmin16-prog/minimi

**작성일:** 2026-01-06
