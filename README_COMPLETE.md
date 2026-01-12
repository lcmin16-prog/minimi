# Minimi Trading Bot - Complete Guide

## 📚 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [설치 및 설정](#설치-및-설정)
3. [업비트 API 등록](#업비트-api-등록)
4. [실행 방법](#실행-방법)
5. [대시보드 사용법](#대시보드-사용법)
6. [모의 투자 → 실전 투자](#모의-투자--실전-투자)
7. [FAQ](#faq)

---

## 🎯 프로젝트 개요

**Minimi**는 업비트 암호화폐 거래소에서 RSI 지표를 활용한 자동 매매 봇입니다.

### 주요 기능
- ✅ RSI 기반 자동 매매
- ✅ 페이퍼 트레이딩 (모의 투자)
- ✅ 실시간 웹 대시보드
- ✅ 자동 스케줄러 (5분마다 실행)
- ✅ 손절/익절 자동 관리
- ✅ 일일 손실 제한
- ✅ 거래 내역 로깅

### 최적화된 전략
```
전략: v1.1-tight-tp
- 손절: -2%
- 익절: +1%
- RSI 매수: ≤ 30
- RSI 매도: ≥ 70
- 예상 승률: 86.6%
```

---

## 🔧 설치 및 설정

### 1. 필수 요구사항
- Python 3.8 이상
- pip
- 업비트 계정

### 2. 프로젝트 설치
```bash
# 저장소 클론
git clone https://github.com/lcmin16-prog/minimi.git
cd minimi

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

`.env` 파일 내용:
```env
UPBIT_ACCESS_KEY=your_access_key_here
UPBIT_SECRET_KEY=your_secret_key_here
TRADE_MODE=paper
# ... 나머지 설정
```

---

## 🔐 업비트 API 등록

상세 가이드: [UPBIT_API_GUIDE.md](UPBIT_API_GUIDE.md)

### 빠른 가이드
1. **업비트 로그인** → 마이페이지 → Open API 관리
2. **새 API 키 발급**
3. **권한 설정**:
   - ✅ 자산 조회
   - ✅ 주문 조회
   - ❌ 주문하기 (모의 투자 시 불필요)
   - ❌ 출금하기 (보안상 비활성화)
4. **키 복사** → .env 파일에 입력
5. **테스트 실행**:
   ```bash
   python test_upbit_api.py
   ```

---

## 🚀 실행 방법

### 방법 1: 통합 실행 (추천)
```bash
./start_bot.sh
```
- 대시보드 + 자동 스케줄러 동시 실행
- 브라우저에서 `http://localhost:5000` 접속

### 방법 2: 개별 실행

#### 대시보드만 실행
```bash
python dashboard.py
```

#### 1회 매매 실행
```bash
python main.py
```

#### 자동 스케줄러 실행
```bash
python scheduler.py
```

---

## 📊 대시보드 사용법

### 접속
```
http://localhost:5000
```

### 화면 구성

#### 1. 헤더
- 모드 표시 (Paper/Real)
- 티커 정보 (KRW-BTC)
- 전략 설정 (SL/TP/RSI)

#### 2. 성과 카드
- 💰 Total Equity: 총 자산
- 📈 Profit/Loss: 수익/손실
- 🎯 Win Rate: 승률
- 💵 KRW Balance: 원화 잔고

#### 3. 실시간 차트
- 📊 가격 차트 (파란색)
- 📉 RSI 지표 (빨간색)
- 과매수/과매도 구간 표시

#### 4. 거래 내역
- 최근 20개 거래
- 시간, 신호, 상태, 상세 정보

### 자동 갱신
- 상태: 5초마다
- 차트: 30초마다
- 거래: 10초마다

---

## 🎓 모의 투자 → 실전 투자

### Phase 1: 모의 투자 (1주일)

#### 설정
```bash
# .env
TRADE_MODE=paper
```

#### 실행
```bash
./start_bot.sh
```

#### 검증 항목
- [ ] 알고리즘이 정상 작동하는가?
- [ ] 승률이 70% 이상인가?
- [ ] 손절/익절이 제대로 작동하는가?
- [ ] 일일 손실 제한이 작동하는가?
- [ ] 1주일 동안 수익이 플러스인가?

---

### Phase 2: 소액 실전 테스트 (1주일)

#### 설정
```bash
# .env
TRADE_MODE=real
TRADE_AMOUNT_KRW=10000.0  # 1만원
```

#### 업비트 API 권한 변경
1. 업비트 Open API 관리
2. **"주문하기" 권한 활성화**
3. API 키 재발급

#### 실행
```bash
# API 테스트
python test_upbit_api.py

# 실전 투자 시작
./start_bot.sh
```

#### 주의사항
- ⚠️ 실제 돈 투자됨
- ⚠️ 손실 가능성 있음
- ⚠️ 지속적 모니터링 필요

---

### Phase 3: 정식 운영

#### 자금 증액
```bash
# .env
TRADE_AMOUNT_KRW=50000.0  # 5만원 (단계적 증액)
```

#### 자동화
```bash
# Crontab 등록
crontab -e

# 5분마다 실행
*/5 * * * * cd /home/user/webapp && python main.py >> logs/cron.log 2>&1
```

---

## ❓ FAQ

### Q1: "API 키가 유효하지 않습니다" 오류
**A**: 
1. .env 파일의 키가 정확한지 확인
2. 업비트에서 키가 활성화되어 있는지 확인
3. 권한 설정 확인 (자산 조회, 주문 조회)

### Q2: 대시보드가 안 열립니다
**A**:
```bash
# 포트 확인
lsof -i :5000

# 프로세스 종료 후 재실행
kill <PID>
python dashboard.py
```

### Q3: 거래가 실행되지 않습니다
**A**:
- RSI가 30 이하 또는 70 이상일 때만 거래
- 5분봉 데이터 기준으로 판단
- 일일 손실 제한 도달 시 거래 중지

### Q4: 모의 투자 데이터 초기화
**A**:
```bash
rm paper_account.json
rm trades.csv
rm trades.log
```

### Q5: 실전 투자로 전환하려면?
**A**:
1. 모의 투자 최소 1주일 검증
2. 업비트 API "주문하기" 권한 활성화
3. .env에서 `TRADE_MODE=real` 변경
4. 소액(1만원)부터 시작

### Q6: 손실이 발생하면 어떻게 하나요?
**A**:
- 자동 손절 -2% 설정됨
- 일일 손실 제한 -5% 도달 시 자동 중지
- 즉시 중지: `Ctrl+C` 또는 프로세스 종료

---

## 📞 지원

### 문서
- [배포 계획](DEPLOYMENT_PLAN.md)
- [업비트 API 가이드](UPBIT_API_GUIDE.md)
- [운영 가이드](OPERATION_GUIDE.md)
- [전략 최적화](STRATEGY_OPTIMIZATION.md)
- [유사 프로젝트](SIMILAR_PROJECTS.md)

### 이슈
- GitHub Issues: https://github.com/lcmin16-prog/minimi/issues

---

## ⚠️ 면책 조항

이 소프트웨어는 교육 및 연구 목적으로 제공됩니다.

- 실제 투자 시 손실이 발생할 수 있습니다
- 투자 결과에 대한 책임은 사용자에게 있습니다
- 충분한 테스트 없이 실전 투자하지 마세요
- 감당 가능한 금액만 투자하세요

---

## 📄 라이선스

MIT License

---

생성일: 2026-01-06
