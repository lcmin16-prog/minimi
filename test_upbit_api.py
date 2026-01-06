"""
업비트 API 연결 테스트 스크립트
"""
from dotenv import load_dotenv
import os
import sys

# 환경 변수 로드
load_dotenv()

def test_api_connection():
    """API 연결 테스트"""
    
    print("=" * 60)
    print("업비트 API 연결 테스트")
    print("=" * 60)
    
    # API 키 확인
    access_key = os.getenv("UPBIT_ACCESS_KEY")
    secret_key = os.getenv("UPBIT_SECRET_KEY")
    
    print("\n[1단계] 환경 변수 확인")
    print("-" * 60)
    
    if not access_key or access_key == "your_access_key_here":
        print("❌ UPBIT_ACCESS_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 실제 Access Key를 입력해주세요.")
        return False
    else:
        print(f"✅ Access Key: {access_key[:8]}...{access_key[-8:]}")
    
    if not secret_key or secret_key == "your_secret_key_here":
        print("❌ UPBIT_SECRET_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 실제 Secret Key를 입력해주세요.")
        return False
    else:
        print(f"✅ Secret Key: {secret_key[:8]}...{secret_key[-8:]}")
    
    # pyupbit 임포트 시도
    print("\n[2단계] pyupbit 라이브러리 확인")
    print("-" * 60)
    
    try:
        import pyupbit
        print("✅ pyupbit 설치 확인")
    except ImportError:
        print("❌ pyupbit가 설치되지 않았습니다.")
        print("   다음 명령어로 설치하세요: pip install pyupbit")
        return False
    
    # 공개 API 테스트
    print("\n[3단계] 공개 API 테스트 (인증 불필요)")
    print("-" * 60)
    
    try:
        # 현재 비트코인 가격 조회
        price = pyupbit.get_current_price("KRW-BTC")
        print(f"✅ 현재 비트코인 가격: {price:,}원")
        
        # 최근 24시간 OHLCV
        df = pyupbit.get_ohlcv("KRW-BTC", interval="minute5", count=1)
        if df is not None and not df.empty:
            print(f"✅ OHLCV 데이터 조회 성공 (최근 5분봉)")
        else:
            print("⚠️  OHLCV 데이터 조회 실패")
            
    except Exception as e:
        print(f"❌ 공개 API 테스트 실패: {e}")
        return False
    
    # 인증 API 테스트
    print("\n[4단계] 인증 API 테스트 (Access Key 필요)")
    print("-" * 60)
    
    try:
        upbit = pyupbit.Upbit(access_key, secret_key)
        
        # 계정 잔고 조회
        balances = upbit.get_balances()
        
        if balances is None:
            print("⚠️  잔고 조회 실패 - API 키를 확인해주세요")
            print("   1. Access Key가 올바른지 확인")
            print("   2. Secret Key가 올바른지 확인")
            print("   3. 업비트에서 API 키가 활성화되어 있는지 확인")
            return False
        
        print("✅ 계정 잔고 조회 성공:")
        
        has_balance = False
        for balance in balances:
            currency = balance['currency']
            amount = float(balance['balance'])
            locked = float(balance['locked'])
            
            if amount > 0 or locked > 0:
                has_balance = True
                total = amount + locked
                print(f"   - {currency}: {total:,.8f} (사용가능: {amount:,.8f}, 대기: {locked:,.8f})")
        
        if not has_balance:
            print("   ⚠️  보유 자산이 없습니다 (정상)")
            
    except Exception as e:
        print(f"❌ 인증 API 테스트 실패: {e}")
        print("   가능한 원인:")
        print("   1. API 키가 올바르지 않음")
        print("   2. '자산 조회' 권한이 비활성화됨")
        print("   3. IP 화이트리스트에 등록되지 않음 (설정한 경우)")
        return False
    
    # 주문 가능 화폐 조회
    print("\n[5단계] 주문 가능 확인")
    print("-" * 60)
    
    try:
        # 주문 가능 화폐 조회 (실제 주문은 하지 않음)
        tickers = pyupbit.get_tickers(fiat="KRW")
        print(f"✅ 주문 가능 화폐 {len(tickers)}개 조회 성공")
        print(f"   예시: {', '.join(tickers[:5])}, ...")
        
        # 주문하기 권한 확인 (에러 발생 시 권한 없음)
        # 실제로 주문하지 않고 함수 호출 가능 여부만 확인
        print("\n   주문하기 권한 확인 중...")
        
        # 매우 작은 금액으로 주문 시도 (실제로는 최소 주문 금액 미달로 실패)
        # 권한이 있으면 "최소 주문 금액 미달" 에러, 없으면 "권한 없음" 에러
        try:
            # 실제로 체결되지 않을 소액 주문
            result = upbit.buy_limit_order("KRW-BTC", 100, 1)
            print("   ⚠️  주문하기 권한 있음 (주의: TRADE_MODE=paper로 설정하세요!)")
        except Exception as order_error:
            error_message = str(order_error)
            if "권한" in error_message or "permission" in error_message.lower():
                print("   ℹ️  주문하기 권한 없음 (모의 투자만 가능)")
                print("   → 실전 투자 시 업비트에서 '주문하기' 권한 활성화 필요")
            else:
                print("   ✅ 주문하기 권한 있음")
                print("   ⚠️  주의: TRADE_MODE=paper로 먼저 모의 투자 테스트 필수!")
                
    except Exception as e:
        print(f"⚠️  주문 가능 확인 실패: {e}")
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("✅ API 연결 테스트 완료!")
    print("=" * 60)
    print("\n다음 단계:")
    print("1. TRADE_MODE=paper로 설정되어 있는지 확인")
    print("2. python main.py로 모의 투자 시작")
    print("3. python dashboard.py로 대시보드 실행")
    print("\n⚠️  실전 투자 전 반드시 충분한 모의 투자 테스트 필요!")
    
    return True


if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)
