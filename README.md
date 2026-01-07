# 🤖 Minimi Trading Bot

**업비트 RSI 기반 자동매매 봇** - 최적화된 알고리즘 + 실시간 대시보드

[![GitHub](https://img.shields.io/badge/GitHub-minimi-blue)](https://github.com/lcmin16-prog/minimi)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## ✨ 주요 기능

- 🎯 **최적화된 RSI 전략**: 승률 86.6% (백테스트)
- 📊 **실시간 웹 대시보드**: 성과 카드, 차트, 거래 내역
- 🔄 **자동 매매**: 5분마다 자동 실행
- 🛡️ **안전장치**: 손절/익절/일일 손실 한도
- 📈 **백테스트 엔진**: 90일 과거 데이터 분석
- 📱 **모바일 지원**: 반응형 웹 디자인

---

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/lcmin16-prog/minimi.git
cd minimi
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 설정
```bash
cp .env.example .env
# .env 파일 편집 (TRADE_MODE=paper로 시작)
```

### 4. 실행
```bash
# 단일 실행 (테스트)
python main.py

# 통합 실행 (봇 + 대시보드)
./start_bot.sh

# 대시보드만 실행
python dashboard.py
```

### 5. 대시보드 접속
```
http://localhost:5000
```

---

## 📚 상세 문서

| 문서 | 설명 |
|------|------|
| **[QUICKSTART.md](QUICKSTART.md)** | 빠른 시작 가이드 ⭐ |
| **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** | 대시보드 사용법 ⭐ |
| **[DEPLOYMENT_SETUP.md](DEPLOYMENT_SETUP.md)** | 서버 배포 방법 ⭐ |
| [UPBIT_API_GUIDE.md](UPBIT_API_GUIDE.md) | 업비트 API 설정 |
| [OPERATION_GUIDE.md](OPERATION_GUIDE.md) | 운영 매뉴얼 |
| [STRATEGY_OPTIMIZATION.md](STRATEGY_OPTIMIZATION.md) | 전략 최적화 분석 |
| [FINAL_REPORT.md](FINAL_REPORT.md) | 프로젝트 완성 보고서 |

---

## 📊 성과

### 백테스트 결과 (90일)
- **승률**: 74.65% → **86.6%** (최적화 후)
- **수익률**: -1.11% → 플러스 전환 (예상)
- **MDD**: -1.66%
- **거래 횟수**: 142건

### 최적화 전략
- 손절: -2% (기존 -3%)
- 익절: +1% (기존 +5%)
- RSI(14): 매수 ≤30, 매도 ≥70

---

## 🖥️ 실행 환경

### ⚠️ 중요: GitHub에서는 실행되지 않습니다!

이 봇을 실행하려면 **서버 환경**이 필요합니다:

1. **로컬 PC** (테스트용)
   - Windows, Mac, Linux
   - 무료, 간단

2. **클라우드 서버** (실전용)
   - AWS EC2 (1년 무료)
   - Google Cloud
   - DigitalOcean, Vultr

3. **라즈베리파이** (저전력 24시간)
   - 초기 비용: ~5만원
   - 월 전기세: ~500원

👉 **자세한 배포 방법**: [DEPLOYMENT_SETUP.md](DEPLOYMENT_SETUP.md)

---

## 🔧 기술 스택

- **Backend**: Python 3.8+, Flask
- **Trading**: pyupbit (업비트 API)
- **Analysis**: pandas, numpy
- **Scheduling**: schedule
- **Frontend**: HTML5, CSS3, Chart.js
- **Logging**: loguru

---

## 📁 프로젝트 구조

```
minimi/
├── 📄 Core
│   ├── main.py              # 매매 실행
│   ├── strategy.py          # RSI 전략
│   ├── paper_broker.py      # 페이퍼 트레이딩
│   └── config.py            # 설정
├── 📊 Analysis
│   ├── backtest.py          # 백테스트
│   └── report.py            # 리포트
├── 🌐 Dashboard
│   ├── dashboard.py         # 웹 서버
│   └── templates/           # UI
├── 🔄 Automation
│   ├── scheduler.py         # 스케줄러
│   └── start_bot.sh         # 통합 실행
└── 📚 Docs
    └── *.md                 # 문서들
```

---

## ⚙️ 설정 (.env)

```env
# 모의 투자용
TRADE_MODE=paper
TICKER=KRW-BTC
STOP_LOSS_PCT=0.02
TAKE_PROFIT_PCT=0.01
PAPER_INITIAL_KRW=1000000.0

# 실전 투자용 (API 키 필수)
TRADE_MODE=real
UPBIT_ACCESS_KEY=your_key
UPBIT_SECRET_KEY=your_secret
```

---

## 🛣️ 로드맵

### Phase 1: 모의 투자 (1주)
- [x] 시스템 구축 완료
- [ ] 1주일 운영 및 검증

### Phase 2: 소액 실전 (2주)
- [ ] 업비트 API 연동
- [ ] 1만원으로 실전 테스트

### Phase 3: 정식 운영 (3주~)
- [ ] 자금 증액
- [ ] 지속 모니터링
- [ ] 전략 최적화

---

## 🤝 기여

이슈 및 PR 환영합니다!

---

## 📄 라이선스

MIT License

---

## 📞 문의

- **GitHub Issues**: https://github.com/lcmin16-prog/minimi/issues
- **Pull Request**: https://github.com/lcmin16-prog/minimi/pull/1

---

**⚠️ 투자 유의사항**  
이 봇은 교육 및 연구 목적으로 제공됩니다.  
실제 투자 시 발생하는 손실에 대한 책임은 사용자에게 있습니다.

**작성**: 2026-01-06
