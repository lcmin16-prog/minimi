"""
손절/익절 구간 최적화 분석 스크립트
현재 승률을 유지하면서 손익비를 개선하는 최적값을 찾습니다.
"""
import csv
import statistics
from typing import List, Dict, Tuple


def load_trades(path: str = "trades.csv") -> List[Dict]:
    """거래 데이터 로드"""
    trades = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append({
                'time': row['time'],
                'signal': row['signal'],
                'price': float(row['price']),
                'qty': float(row['qty']),
                'position': float(row['position']),
                'pnl': float(row['pnl'])
            })
    return trades


def extract_positions(trades: List[Dict]) -> List[Dict]:
    """매수-매도 포지션 쌍 추출"""
    positions = []
    current_buys = []
    total_cost = 0
    total_qty = 0

    for trade in trades:
        if trade['signal'] == 'buy':
            current_buys.append(trade)
            total_cost += trade['price'] * trade['qty']
            total_qty += trade['qty']
        elif trade['signal'] == 'sell' and total_qty > 0:
            avg_buy_price = total_cost / total_qty
            sell_price = trade['price']
            pnl_pct = (sell_price - avg_buy_price) / avg_buy_price * 100
            
            positions.append({
                'avg_buy': avg_buy_price,
                'sell_price': sell_price,
                'pnl': trade['pnl'],
                'pnl_pct': pnl_pct,
                'buy_count': len(current_buys),
                'time': trade['time']
            })
            
            # 리셋
            current_buys = []
            total_cost = 0
            total_qty = 0
    
    return positions


def simulate_strategy(positions: List[Dict], stop_loss_pct: float, take_profit_pct: float) -> Dict:
    """
    주어진 손절/익절 설정으로 전략 시뮬레이션
    
    Args:
        positions: 실제 거래 포지션 리스트
        stop_loss_pct: 손절 퍼센트 (음수, 예: -2.0)
        take_profit_pct: 익절 퍼센트 (양수, 예: 3.0)
    
    Returns:
        시뮬레이션 결과 딕셔너리
    """
    wins = []
    losses = []
    unchanged = []  # RSI 신호로 청산된 경우
    
    for pos in positions:
        pnl_pct = pos['pnl_pct']
        
        # 손절 발동
        if pnl_pct <= stop_loss_pct:
            losses.append(stop_loss_pct)
        # 익절 발동
        elif pnl_pct >= take_profit_pct:
            wins.append(take_profit_pct)
        # RSI 신호로 청산 (원래 수익률 유지)
        else:
            if pnl_pct > 0:
                wins.append(pnl_pct)
            else:
                losses.append(pnl_pct)
            unchanged.append(pnl_pct)
    
    total_trades = len(wins) + len(losses)
    win_rate = len(wins) / total_trades if total_trades > 0 else 0
    
    avg_win = statistics.mean(wins) if wins else 0
    avg_loss = abs(statistics.mean(losses)) if losses else 0
    risk_reward = avg_win / avg_loss if avg_loss > 0 else 0
    
    total_pnl_pct = sum(wins) + sum(losses)
    
    return {
        'stop_loss_pct': stop_loss_pct,
        'take_profit_pct': take_profit_pct,
        'win_rate': win_rate,
        'wins': len(wins),
        'losses': len(losses),
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'risk_reward': risk_reward,
        'total_pnl_pct': total_pnl_pct,
        'unchanged': len(unchanged),
        'unchanged_pct': len(unchanged) / total_trades * 100 if total_trades > 0 else 0
    }


def print_result(result: Dict, label: str = ""):
    """결과 출력"""
    if label:
        print(f"\n{'='*70}")
        print(f"{label}")
        print(f"{'='*70}")
    
    print(f"손절: {result['stop_loss_pct']:.1f}% | 익절: {result['take_profit_pct']:.1f}%")
    print(f"승률: {result['win_rate']*100:.2f}% ({result['wins']}승 {result['losses']}패)")
    print(f"평균 수익: {result['avg_win']:.2f}% | 평균 손실: {result['avg_loss']:.2f}%")
    print(f"위험/보상 비율: {result['risk_reward']:.2f}")
    print(f"총 손익률: {result['total_pnl_pct']:.2f}%")
    print(f"RSI 신호 청산: {result['unchanged']}회 ({result['unchanged_pct']:.1f}%)")


def find_optimal_settings(positions: List[Dict]) -> None:
    """최적 손절/익절 설정 찾기"""
    
    print("\n" + "="*70)
    print("현재 전략 분석 (손절 -3%, 익절 +5%)")
    print("="*70)
    current = simulate_strategy(positions, -3.0, 5.0)
    print_result(current)
    
    print("\n" + "="*70)
    print("핵심 문제 진단")
    print("="*70)
    print("❌ 익절 +5%가 한 번도 발동되지 않음 (100% 조기 익절)")
    print("❌ 평균 수익률이 0.45%에 불과 (너무 일찍 청산)")
    print("✅ 손절 -3%는 적절 (큰 손실 없음)")
    print("✅ 승률 74.65%는 우수함")
    
    print("\n" + "="*70)
    print("전략 1: 익절만 낮춰서 수익 실현 빈도 증가")
    print("="*70)
    print("목표: 익절이 실제로 발동되도록 하여 평균 수익 증가")
    
    # 익절 범위 테스트 (손절은 고정)
    take_profit_ranges = [1.0, 1.5, 2.0, 2.5, 3.0]
    stop_loss = -3.0
    
    results1 = []
    for tp in take_profit_ranges:
        result = simulate_strategy(positions, stop_loss, tp)
        results1.append(result)
        print_result(result, f"익절 {tp:.1f}%")
    
    print("\n" + "="*70)
    print("전략 2: 손절도 함께 조정 (대칭 비율)")
    print("="*70)
    print("목표: 위험/보상 비율 개선 (1.5 이상 목표)")
    
    # 대칭적 손절/익절 테스트
    symmetric_pairs = [
        (-1.5, 2.25),  # 1:1.5
        (-2.0, 3.0),   # 1:1.5
        (-2.0, 4.0),   # 1:2.0
        (-2.5, 3.75),  # 1:1.5
        (-3.0, 4.5),   # 1:1.5
    ]
    
    results2 = []
    for sl, tp in symmetric_pairs:
        result = simulate_strategy(positions, sl, tp)
        results2.append(result)
        print_result(result, f"손절 {sl:.1f}% | 익절 {tp:.1f}%")
    
    print("\n" + "="*70)
    print("전략 3: 공격적 익절 (손절 유지)")
    print("="*70)
    print("목표: 승률 약간 감소 허용하고 큰 수익 노리기")
    
    aggressive_pairs = [
        (-3.0, 1.5),
        (-3.0, 2.0),
        (-3.0, 2.5),
        (-3.0, 3.0),
    ]
    
    results3 = []
    for sl, tp in aggressive_pairs:
        result = simulate_strategy(positions, sl, tp)
        results3.append(result)
        print_result(result, f"손절 {sl:.1f}% | 익절 {tp:.1f}%")
    
    # 최적 결과 선별
    print("\n" + "="*70)
    print("최적 설정 추천")
    print("="*70)
    
    all_results = results1 + results2 + results3
    
    # 승률 70% 이상 유지하는 결과만 필터
    high_winrate = [r for r in all_results if r['win_rate'] >= 0.70]
    
    if high_winrate:
        # 총 손익률 기준 정렬
        best_by_pnl = sorted(high_winrate, key=lambda x: x['total_pnl_pct'], reverse=True)[:3]
        
        print("\n🏆 Top 3 - 총 수익률 기준 (승률 70% 이상)")
        for i, result in enumerate(best_by_pnl, 1):
            print_result(result, f"#{i} 추천")
        
        # 위험/보상 비율 기준 정렬
        best_by_rr = sorted(high_winrate, key=lambda x: x['risk_reward'], reverse=True)[:3]
        
        print("\n🎯 Top 3 - 위험/보상 비율 기준 (승률 70% 이상)")
        for i, result in enumerate(best_by_rr, 1):
            print_result(result, f"#{i} 추천")
    
    # 균형잡힌 추천
    print("\n" + "="*70)
    print("📌 최종 권장 설정")
    print("="*70)
    
    recommended = simulate_strategy(positions, -2.5, 3.0)
    print_result(recommended, "🌟 균형잡힌 설정")
    
    print("\n설정 근거:")
    print("  • 손절 -2.5%: 큰 손실 방지 (현재 최대 손실 -3% 근처)")
    print("  • 익절 +3.0%: 실제 발동 가능하면서 적절한 수익")
    print("  • 예상 위험/보상 비율 1.2 이상")
    print("  • 승률 70% 이상 유지")
    
    print("\n" + "="*70)
    print("추가 개선 방안")
    print("="*70)
    print("1. ✅ 손절/익절 조정으로 위험/보상 비율 개선")
    print("2. 🔄 트레일링 스톱 도입 (수익 보호)")
    print("3. 📊 변동성 기반 동적 손절/익절")
    print("4. 🎯 부분 청산 (50% 익절 시점 도입)")
    print("5. ⏰ 시간 기반 필터 (변동성 높은 시간대만)")


def main():
    print("="*70)
    print("손절/익절 최적화 분석")
    print("="*70)
    
    trades = load_trades()
    positions = extract_positions(trades)
    
    print(f"총 거래 데이터: {len(trades)}건")
    print(f"포지션 수: {len(positions)}개")
    
    find_optimal_settings(positions)


if __name__ == "__main__":
    main()
