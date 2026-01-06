# 유사 프로젝트 조사 및 알고리즘 분석

## 🔍 GitHub 유사 프로젝트 조사 결과

### 1. Freqtrade (★ 28k+ stars)
**URL**: https://github.com/freqtrade/freqtrade

#### 특징
- **가장 인기 있는 오픈소스 암호화폐 트레이딩 봇**
- 모든 주요 거래소 지원 (Binance, Kraken, Coinbase 등)
- 텔레그램/WebUI 제어
- 강력한 백테스트 엔진

#### RSI 전략 예시
```python
from freqtrade.strategy import IStrategy
import talib.abstract as ta

class RSIStrategy(IStrategy):
    # 손절/익절
    stoploss = -0.02  # -2%
    minimal_roi = {
        "0": 0.01,    # 1% 익절
        "40": 0.005,  # 40분 후 0.5%
        "90": 0        # 90분 후 손익분기점
    }
    
    # 트레일링 스톱
    trailing_stop = True
    trailing_stop_positive = 0.005  # 0.5% 수익 시 활성화
    trailing_stop_positive_offset = 0.01  # 1% 수익부터
    trailing_only_offset_is_reached = True
    
    def populate_indicators(self, dataframe, metadata):
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe, metadata):
        dataframe.loc[
            (dataframe['rsi'] < 30),  # RSI < 30
            'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe, metadata):
        dataframe.loc[
            (dataframe['rsi'] > 70),  # RSI > 70
            'exit_long'] = 1
        return dataframe
```

#### 우리 프로젝트 적용 가능 요소
✅ **트레일링 스톱**: 수익 보호하며 확장  
✅ **다단계 ROI**: 시간 기반 익절  
✅ **상세한 백테스트**: 메트릭 분석  
✅ **WebUI/텔레그램**: 모니터링  

---

### 2. 업비트 자동매매 봇 (한국어)
**URL**: https://github.com/haguri-peng/UPbitAutoTrading

#### 특징
- **업비트 전용** 자동매매
- 변동성 돌파 전략
- RSI, 볼린저 밴드 조합

#### 핵심 로직
```python
# 변동성 돌파 + RSI 조합
def get_target_price(ticker):
    """목표가 계산 (변동성 돌파)"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + \
                   (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.5
    return target_price

def check_buy_signal(ticker):
    """매수 신호"""
    current_price = pyupbit.get_current_price(ticker)
    target_price = get_target_price(ticker)
    
    # RSI
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=30)
    rsi = calculate_rsi(df)
    
    if current_price > target_price and rsi < 30:
        return True
    return False
```

#### 우리 프로젝트 적용 가능 요소
✅ **변동성 필터**: 변동성 높은 구간만 거래  
✅ **다중 조건**: RSI + 추가 지표  
✅ **목표가 설정**: 동적 익절  

---

### 3. Blankly Finance - RSI Crypto Trading Bot
**URL**: https://github.com/blankly-finance/rsi-crypto-trading-bot

#### 특징
- **25줄로 구현된 간단한 RSI 봇**
- Binance 지원
- 백테스트 내장

#### 핵심 로직
```python
def price_event(price, symbol, state):
    # RSI 계산
    rsi = blankly.indicators.rsi(state.interface.history(
        symbol, 40, resolution='15m'
    )['close'])
    
    # 매수 신호
    if rsi[-1] < 30 and not state.variables['owns_position']:
        buy = int(state.interface.cash / price)
        state.interface.market_order(symbol, 'buy', buy)
        state.variables['owns_position'] = True
    
    # 매도 신호
    elif rsi[-1] > 70 and state.variables['owns_position']:
        curr_value = int(state.interface.account[symbol].available)
        state.interface.market_order(symbol, 'sell', curr_value)
        state.variables['owns_position'] = False
```

#### 우리 프로젝트와 비교
- ✅ 우리: 더 정교한 손절/익절
- ✅ 우리: 페이퍼 트레이딩 시스템
- ❌ 우리: 실시간 모니터링 부족

---

## 🎓 알고리즘 패턴 분석

### Pattern 1: 기본 RSI 전략 (우리 현재)
```
매수: RSI ≤ 30
매도: RSI ≥ 70
손절: -3%
익절: +5%
```
**문제**: 익절이 너무 높아 도달 못함

---

### Pattern 2: RSI + 볼린저 밴드 조합
```python
# 매수 조건
if rsi < 30 and price < bollinger_lower:
    buy()

# 매도 조건
if rsi > 70 or price > bollinger_upper:
    sell()
```
**장점**: 더 강한 신호, 승률 향상  
**단점**: 거래 빈도 감소

---

### Pattern 3: RSI + 이동평균선
```python
# 상승 추세에서만 매수
if rsi < 30 and price > ma_20:
    buy()

# 하락 추세 빠른 청산
if rsi > 70 or price < ma_20:
    sell()
```
**장점**: 추세 확인, 잘못된 신호 필터링  
**단점**: 추세 전환 놓칠 수 있음

---

### Pattern 4: 다단계 RSI (레벨 트레이딩)
```python
# 레벨별 분할 매수
if rsi <= 20:
    buy(50%)  # 50% 매수
elif rsi <= 30:
    buy(30%)  # 30% 매수

# 레벨별 분할 매도
if rsi >= 80:
    sell(50%)  # 50% 매도
elif rsi >= 70:
    sell(30%)  # 30% 매도
```
**장점**: 리스크 분산, 평균 단가 개선  
**단점**: 복잡한 포지션 관리

---

### Pattern 5: RSI + 트레일링 스톱 (Freqtrade 방식)
```python
# 진입
if rsi < 30:
    buy()

# 트레일링 스톱
if profit > 0.005:  # 0.5% 수익
    trailing_stop_price = max(
        trailing_stop_price,
        current_price * 0.997  # 고점 -0.3%
    )
    
    if current_price <= trailing_stop_price:
        sell()  # 트레일링 발동

# 손절
if profit < -0.02:
    sell()
```
**장점**: 수익 보호하며 확장, 큰 상승 놓치지 않음  
**단점**: 구현 복잡

---

### Pattern 6: 시간 기반 ROI (Freqtrade)
```python
minimal_roi = {
    "0": 0.02,    # 즉시 2% 익절
    "30": 0.01,   # 30분 후 1%
    "60": 0.005,  # 1시간 후 0.5%
    "120": 0      # 2시간 후 손익분기점
}
```
**장점**: 보유시간 최적화, 수수료 효율  
**단점**: 시장 상황 무시

---

## 🎯 우리 프로젝트 개선 방향

### 1단계: 간단 조정 (즉시 적용)
```python
# config.py
STOP_LOSS_PCT = 0.02      # -2%
TAKE_PROFIT_PCT = 0.01    # +1%
```

### 2단계: RSI 임계값 강화
```python
# strategy.py
RSI_BUY = 25   # 30 → 25
RSI_SELL = 75  # 70 → 75
```

### 3단계: 볼린저 밴드 추가
```python
def get_signal(df, period):
    rsi = calculate_rsi(df['close'], period)
    
    # 볼린저 밴드
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(df['close'], 20, 2)
    
    latest_rsi = rsi.iloc[-1]
    latest_price = df['close'].iloc[-1]
    
    # 매수: RSI < 25 AND 가격 < 볼린저 하단
    if latest_rsi <= 25 and latest_price < bb_lower.iloc[-1]:
        return "buy", float(latest_rsi)
    
    # 매도: RSI > 75 OR 가격 > 볼린저 상단
    if latest_rsi >= 75 or latest_price > bb_upper.iloc[-1]:
        return "sell", float(latest_rsi)
    
    return "hold", float(latest_rsi)
```

### 4단계: 트레일링 스톱 구현
```python
# paper_broker.py에 추가
class PaperBroker:
    def __init__(self, ...):
        # ...
        self.trailing_stop_price = 0.0
        self.trailing_active = False
    
    def update_trailing_stop(self, current_price):
        """트레일링 스톱 업데이트"""
        if self.coin_amount <= 0:
            return False
        
        profit_pct = (current_price - self.avg_buy_price) / self.avg_buy_price
        
        # 0.5% 수익 시 트레일링 활성화
        if profit_pct >= 0.005:
            self.trailing_active = True
            # 고점 -0.3%
            new_stop = current_price * 0.997
            self.trailing_stop_price = max(self.trailing_stop_price, new_stop)
        
        # 트레일링 발동 체크
        if self.trailing_active and current_price <= self.trailing_stop_price:
            return True  # 매도 신호
        
        return False
```

---

## 📚 참고할 만한 리소스

### 백테스트 라이브러리
1. **Backtrader**: https://github.com/mementum/backtrader
2. **Backtesting.py**: https://github.com/kernc/backtesting.py
3. **VectorBT**: https://github.com/polakowo/vectorbt

### 기술적 지표
1. **TA-Lib**: 모든 기술적 지표 제공
2. **pandas-ta**: pandas 기반 지표
3. **finta**: 경량 지표 라이브러리

### 트레이딩 전략
1. **Freqtrade Strategies**: https://github.com/freqtrade/freqtrade-strategies
2. **QuantConnect**: 알고리즘 트레이딩 플랫폼

---

## 🎁 프로젝트 적용 체크리스트

### 즉시 적용 가능
- [x] 손절/익절 조정 (-2%/+1%)
- [x] RSI 임계값 강화 (25/75)
- [ ] 백테스트 비교 시스템 구축 ✅ (완료)

### 단기 적용 (1~2주)
- [ ] 트레일링 스톱 구현
- [ ] 볼린저 밴드 추가
- [ ] 변동성 필터
- [ ] 텔레그램 알림

### 장기 적용 (1개월+)
- [ ] 다중 지표 조합
- [ ] 머신러닝 신호 생성
- [ ] 멀티 코인 포트폴리오
- [ ] WebUI 대시보드

---

생성일: 2026-01-06
