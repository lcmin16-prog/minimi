# 업비트 API 연동 가이드

## 🔐 업비트 Open API 등록 절차

### 1단계: 업비트 계정 준비

#### 계정 생성
1. **업비트 웹사이트 접속**
   - URL: https://upbit.com
   - "회원가입" 클릭

2. **본인 인증**
   - 휴대폰 인증
   - 이메일 인증
   - 실명 인증 (은행 계좌 연동)

3. **보안 설정**
   - 비밀번호 설정 (8자 이상, 영문+숫자+특수문자)
   - OTP 설정 (Google Authenticator 또는 PASS 앱)
   - 출금 비밀번호 설정

---

### 2단계: Open API 키 발급

#### API 키 생성
1. **업비트 로그인**
   - 메인 화면 우측 상단 로그인

2. **Open API 관리 페이지 이동**
   ```
   마이페이지 → 고객센터 → Open API 안내
   또는 직접 URL: https://upbit.com/mypage/open_api_management
   ```

3. **새 API 키 발급**
   - "Open API 키 발급" 버튼 클릭
   - OTP 인증 진행

4. **권한 설정** ⚠️ 중요!
   ```
   ✅ 자산 조회 (Assets)        - 필수, 잔고 확인용
   ✅ 주문 조회 (Orders)         - 필수, 거래 내역 확인
   ✅ 주문하기 (Order)           - 실전 매매용
   ❌ 출금하기 (Withdraw)        - 보안상 비활성화 권장
   
   ※ 처음에는 "주문하기" 체크 해제하고 모의 투자 먼저!
   ```

5. **IP 주소 등록** (선택사항, 보안 강화)
   ```
   고정 IP가 있는 경우:
   - 서버 IP 주소 등록
   - 해당 IP에서만 API 호출 가능
   
   없는 경우:
   - IP 등록 없이 진행 가능
   - 하지만 보안이 약해짐
   ```

6. **키 생성 완료**
   ```
   ⚠️ 화면에 표시되는 키를 반드시 복사하여 안전한 곳에 저장!
   
   Access Key: xxxxxxxxxxxxxxxxxxxxxxxx
   Secret Key: xxxxxxxxxxxxxxxxxxxxxxxx
   
   ※ Secret Key는 다시 확인 불가능!
   ※ 분실 시 삭제 후 재발급 필요
   ```

---

### 3단계: 환경 설정

#### .env 파일 생성

```bash
# 프로젝트 디렉토리에 .env 파일 생성
cd /home/user/webapp
nano .env
```

#### .env 파일 내용
```bash
# 업비트 API 키
UPBIT_ACCESS_KEY=your_access_key_here_xxxxxxxxxxxxxxxx
UPBIT_SECRET_KEY=your_secret_key_here_xxxxxxxxxxxxxxxx

# 거래 모드 (paper: 모의투자, real: 실전투자)
TRADE_MODE=paper

# 거래 설정
TICKER=KRW-BTC
RSI_PERIOD=14
TRADE_AMOUNT_KRW=10000.0

# 손절/익절 (v1.1-tight-tp 전략)
STOP_LOSS_PCT=0.02
TAKE_PROFIT_PCT=0.01

# 페이퍼 트레이딩
PAPER_INITIAL_KRW=1000000.0
PAPER_STATE_FILE=paper_account.json

# 로그
LOG_FILE=trades.log

# 캔들 간격
CANDLE_INTERVAL=minute5

# 리스크 관리
MAX_INVEST_RATIO=0.30
DAILY_LOSS_LIMIT_PCT=0.05
```

#### 보안 강화
```bash
# .env 파일 권한 설정 (본인만 읽기 가능)
chmod 600 .env

# Git에서 제외 확인
cat .gitignore | grep .env
# 만약 없다면:
echo ".env" >> .gitignore
```

---

### 4단계: API 연결 테스트

#### 테스트 스크립트 실행
```python
# test_upbit_api.py
from dotenv import load_dotenv
import os
import pyupbit

load_dotenv()

access_key = os.getenv("UPBIT_ACCESS_KEY")
secret_key = os.getenv("UPBIT_SECRET_KEY")

print("="*50)
print("업비트 API 연결 테스트")
print("="*50)

# 1. 공개 API 테스트 (인증 불필요)
print("\n[1] 현재 비트코인 가격 조회")
try:
    price = pyupbit.get_current_price("KRW-BTC")
    print(f"✅ 성공: {price:,}원")
except Exception as e:
    print(f"❌ 실패: {e}")

# 2. 인증 API 테스트 (Access Key 필요)
print("\n[2] 계정 잔고 조회")
try:
    upbit = pyupbit.Upbit(access_key, secret_key)
    balances = upbit.get_balances()
    print("✅ 성공:")
    for balance in balances:
        currency = balance['currency']
        amount = float(balance['balance'])
        if amount > 0:
            print(f"  - {currency}: {amount}")
except Exception as e:
    print(f"❌ 실패: {e}")

# 3. 주문 가능 확인 (주문하기 권한 필요)
print("\n[3] 주문 가능 화폐 조회")
try:
    upbit = pyupbit.Upbit(access_key, secret_key)
    # 실제로 주문하지 않고 권한만 확인
    print("✅ API 키 권한 확인 완료")
except Exception as e:
    print(f"⚠️ 주문하기 권한 없음 (모의 투자만 가능): {e}")

print("\n" + "="*50)
print("테스트 완료!")
print("="*50)
```

#### 실행
```bash
cd /home/user/webapp
python test_upbit_api.py
```

---

### 5단계: 모의 투자 vs 실전 투자

#### 모의 투자 (Paper Trading)
```bash
# .env 설정
TRADE_MODE=paper

# 장점
✅ 실제 돈 사용 안 함
✅ API 키 "주문하기" 권한 불필요
✅ 안전하게 알고리즘 테스트
✅ 무제한 테스트 가능

# 단점
❌ 실제 체결가와 차이 있을 수 있음
❌ 슬리피지 미반영
```

#### 실전 투자 (Real Trading)
```bash
# .env 설정
TRADE_MODE=real

# 필수 요구사항
⚠️ API 키 "주문하기" 권한 활성화
⚠️ 계정에 실제 원화 입금
⚠️ 충분한 모의 투자 검증 완료

# 주의사항
❗ 소액(1만원)부터 시작
❗ 알고리즘 검증 후 사용
❗ 손실 가능성 인지
❗ 자동 매매 지속 모니터링
```

---

## 🛡️ 보안 가이드

### DO's ✅
- ✅ API 키는 .env 파일에만 저장
- ✅ .env 파일은 Git에 업로드 금지
- ✅ 서버 접근 권한 최소화
- ✅ OTP 2FA 반드시 사용
- ✅ 정기적으로 API 키 갱신
- ✅ 출금하기 권한 비활성화
- ✅ 가능하면 IP 화이트리스트 사용

### DON'Ts ❌
- ❌ API 키를 코드에 직접 입력
- ❌ API 키를 GitHub에 업로드
- ❌ API 키를 메신저로 전송
- ❌ 타인과 API 키 공유
- ❌ 공용 서버에 키 저장
- ❌ 스크린샷에 키 노출

---

## 🚨 API 키 유출 시 대응

1. **즉시 업비트 로그인**
2. **Open API 관리 페이지 이동**
3. **해당 API 키 삭제**
4. **계정 활동 내역 확인**
5. **새 API 키 발급**
6. **비밀번호 변경**
7. **OTP 재설정**

---

## 📞 문의 및 지원

### 업비트 고객센터
- 웹사이트: https://upbit.com/service_center
- 이메일: support@upbit.com
- 카카오톡: 업비트 고객센터

### API 문서
- 공식 문서: https://docs.upbit.com
- pyupbit 문서: https://github.com/sharebook-kr/pyupbit

---

## ✅ 체크리스트

### API 등록 전
- [ ] 업비트 계정 생성
- [ ] 본인 인증 완료
- [ ] OTP 설정 완료
- [ ] 실명 인증 완료

### API 키 발급
- [ ] Open API 키 발급 완료
- [ ] Access Key 복사 저장
- [ ] Secret Key 복사 저장
- [ ] 권한 설정 확인

### 프로젝트 설정
- [ ] .env 파일 생성
- [ ] API 키 입력
- [ ] TRADE_MODE=paper 설정
- [ ] .gitignore에 .env 추가
- [ ] test_upbit_api.py 실행 성공

### 실전 투자 전
- [ ] 1주일 이상 모의 투자 완료
- [ ] 알고리즘 안정성 확인
- [ ] 리스크 관리 이해
- [ ] 소액(1만원) 테스트 계획 수립

---

생성일: 2026-01-06
