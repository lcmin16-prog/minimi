"""
승률 유지 전략 - 손익 구간 조정 상세 분석
"""
import csv
from typing import List, Dict
import statistics


def analyze_actual_trades():
    """실제 거래 데이터 분석"""
    
    print("="*80)
    print("🔍 실제 백테스트 데이터 분석")
    print("="*80)
    
    # 데이터 로드
    trades = []
    with open('trades.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append({
                'time': row['time'],
                'signal': row['signal'],
                'price': float(row['price']),
                'qty': float(row['qty']),
                'fee': float(row['fee']),
                'balance': float(row['balance']),
                'position': float(row['position']),
                'pnl': float(row['pnl'])
            })
    
    # 포지션 추적
    positions = []
    entry_price = 0
    entry_qty = 0
    
    for trade in trades:
        if trade['signal'] == 'buy':
            if entry_qty == 0:
                entry_price = trade['price']
            else:
                # 평균 매수가 계산
                total_value = entry_price * entry_qty + trade['price'] * trade['qty']
                entry_qty += trade['qty']
                entry_price = total_value / entry_qty
            entry_qty = trade['position']
        
        elif trade['signal'] == 'sell' and trade['pnl'] != 0:
            exit_price = trade['price']
            pnl_pct = (exit_price - entry_price) / entry_price * 100
            
            positions.append({
                'entry': entry_price,
                'exit': exit_price,
                'pnl': trade['pnl'],
                'pnl_pct': pnl_pct,
                'fee': trade['fee'],
                'time': trade['time']
            })
            
            entry_price = 0
            entry_qty = 0
    
    print(f"\n총 완결 포지션: {len(positions)}개")
    
    # 승률 분석
    wins = [p for p in positions if p['pnl'] > 0]
    losses = [p for p in positions if p['pnl'] < 0]
    
    win_rate = len(wins) / len(positions) * 100
    
    print(f"\n{'='*80}")
    print(f"📊 승률 분석")
    print(f"{'='*80}")
    print(f"승리: {len(wins)}회")
    print(f"패배: {len(losses)}회")
    print(f"승률: {win_rate:.2f}%")
    
    # 손익 분포
    print(f"\n{'='*80}")
    print(f"💰 손익 분포 (퍼센트)")
    print(f"{'='*80}")
    
    print("\n[수익 거래]")
    if wins:
        win_pcts = [p['pnl_pct'] for p in wins]
        print(f"  평균: {statistics.mean(win_pcts):.3f}%")
        print(f"  중간값: {statistics.median(win_pcts):.3f}%")
        print(f"  최소: {min(win_pcts):.3f}%")
        print(f"  최대: {max(win_pcts):.3f}%")
        print(f"  표준편차: {statistics.stdev(win_pcts):.3f}%")
        
        # 구간별 분포
        print("\n  구간별 분포:")
        ranges = [
            (0, 0.5, "0.0% ~ 0.5%"),
            (0.5, 1.0, "0.5% ~ 1.0%"),
            (1.0, 1.5, "1.0% ~ 1.5%"),
            (1.5, 2.0, "1.5% ~ 2.0%"),
            (2.0, 100, "2.0% 이상")
        ]
        for min_v, max_v, label in ranges:
            count = len([p for p in wins if min_v <= p['pnl_pct'] < max_v])
            pct = count / len(wins) * 100
            print(f"    {label:15s}: {count:3d}회 ({pct:5.1f}%)")
    
    print("\n[손실 거래]")
    if losses:
        loss_pcts = [p['pnl_pct'] for p in losses]
        print(f"  평균: {statistics.mean(loss_pcts):.3f}%")
        print(f"  중간값: {statistics.median(loss_pcts):.3f}%")
        print(f"  최소 (최대손실): {min(loss_pcts):.3f}%")
        print(f"  최대 (최소손실): {max(loss_pcts):.3f}%")
        print(f"  표준편차: {statistics.stdev(loss_pcts):.3f}%")
        
        # 구간별 분포
        print("\n  구간별 분포:")
        ranges = [
            (-0.5, 0, " 0.0% ~ -0.5%"),
            (-1.0, -0.5, "-0.5% ~ -1.0%"),
            (-1.5, -1.0, "-1.0% ~ -1.5%"),
            (-2.0, -1.5, "-1.5% ~ -2.0%"),
            (-100, -2.0, "-2.0% 이하")
        ]
        for min_v, max_v, label in ranges:
            count = len([p for p in losses if min_v <= p['pnl_pct'] < max_v])
            pct = count / len(losses) * 100
            print(f"    {label:15s}: {count:3d}회 ({pct:5.1f}%)")
    
    # 핵심 발견
    print(f"\n{'='*80}")
    print(f"🎯 핵심 발견")
    print(f"{'='*80}")
    
    avg_win_pct = statistics.mean([p['pnl_pct'] for p in wins]) if wins else 0
    avg_loss_pct = statistics.mean([p['pnl_pct'] for p in losses]) if losses else 0
    risk_reward = abs(avg_win_pct / avg_loss_pct) if avg_loss_pct != 0 else 0
    
    print(f"평균 수익: {avg_win_pct:.3f}%")
    print(f"평균 손실: {avg_loss_pct:.3f}%")
    print(f"위험/보상 비율: {risk_reward:.2f}")
    
    # 문제점 진단
    print(f"\n{'='*80}")
    print(f"⚠️  문제점 진단")
    print(f"{'='*80}")
    
    print("\n1. 평균 수익이 매우 낮음 (< 0.5%)")
    print("   → RSI 신호로 너무 빨리 청산됨")
    print("   → 익절 지점이 도달하기 전에 매도")
    
    max_win = max([p['pnl_pct'] for p in wins]) if wins else 0
    print(f"\n2. 최대 수익도 {max_win:.2f}%에 불과")
    print("   → 큰 상승을 놓치고 있음")
    print("   → 현재 익절 5%는 한 번도 발동 안 됨")
    
    max_loss = min([p['pnl_pct'] for p in losses]) if losses else 0
    print(f"\n3. 최대 손실은 {max_loss:.2f}%")
    print("   → 손절 -3%도 거의 발동 안 됨")
    print("   → 손실도 RSI 신호로 조기 청산")
    
    # 개선 방안
    print(f"\n{'='*80}")
    print(f"💡 개선 전략 (승률 유지)")
    print(f"{'='*80}")
    
    # 백분위수 분석
    win_pcts_sorted = sorted([p['pnl_pct'] for p in wins])
    loss_pcts_sorted = sorted([p['pnl_pct'] for p in losses])
    
    # 75th percentile
    win_75th = win_pcts_sorted[int(len(win_pcts_sorted) * 0.75)] if wins else 0
    win_90th = win_pcts_sorted[int(len(win_pcts_sorted) * 0.90)] if wins else 0
    loss_25th = loss_pcts_sorted[int(len(loss_pcts_sorted) * 0.25)] if losses else 0
    
    print(f"\n[데이터 기반 임계값]")
    print(f"  수익 75th percentile: {win_75th:.3f}%")
    print(f"  수익 90th percentile: {win_90th:.3f}%")
    print(f"  손실 25th percentile: {loss_25th:.3f}%")
    
    print(f"\n{'='*80}")
    print(f"📌 전략 제안")
    print(f"{'='*80}")
    
    print("\n전략 A: 익절 낮추기 (승률 유지 가능)")
    print(f"  • 손절: -2.0% (현재 최대 손실 {max_loss:.2f}% 근처)")
    print(f"  • 익절: +1.0% (75th percentile {win_75th:.2f}% 근처)")
    print("  • 예상 효과: 익절 실제 발동, 수익 확정 증가")
    print("  • 승률 영향: 거의 없음 (대부분 1% 이하 청산)")
    
    print("\n전략 B: RSI 임계값 완화 (거래 빈도 감소)")
    print("  • RSI 매수: 30 → 25 (더 강한 과매도)")
    print("  • RSI 매도: 70 → 75 (더 강한 과매수)")
    print("  • 손절/익절: -2.5% / +1.5%")
    print("  • 예상 효과: 더 확실한 신호에만 진입, 승률 유지")
    
    print("\n전략 C: 트레일링 스톱 (수익 보호)")
    print("  • 0.5% 수익 발생 시 트레일링 시작")
    print("  • 고점 대비 -0.3% 하락 시 청산")
    print("  • 손절: -2.0%")
    print("  • 예상 효과: 수익 구간 확장, 승률 유지")
    
    print("\n전략 D: 부분 청산 (리스크 감소)")
    print("  • 1차 익절 +0.8%에서 50% 청산")
    print("  • 2차 익절 +1.5%에서 나머지 청산")
    print("  • 손절: -2.0%")
    print("  • 예상 효과: 수익 확정 + 추가 수익 기회")
    
    # 최종 추천
    print(f"\n{'='*80}")
    print(f"🌟 최종 추천 (우선순위)")
    print(f"{'='*80}")
    
    print("\n1순위: 익절 1.0% + 손절 -2.0%")
    print("   이유: 가장 빠른 개선, 승률 유지 확실")
    print(f"   근거: 수익 거래의 {len([p for p in wins if p['pnl_pct'] < 1.0])/len(wins)*100:.0f}%가 1% 미만")
    
    print("\n2순위: RSI 임계값 25/75 + 익절 1.5% + 손절 -2.5%")
    print("   이유: 거래 품질 향상, 수수료 감소")
    print("   근거: 더 강한 신호로 승률 유지하며 수익폭 증가")
    
    print("\n3순위: 트레일링 스톱 도입")
    print("   이유: 구현 복잡하지만 효과적")
    print("   근거: 수익 구간 자동 확장")
    
    # 수치 시뮬레이션
    print(f"\n{'='*80}")
    print(f"📊 시뮬레이션 (간단 계산)")
    print(f"{'='*80}")
    
    print("\n현재 (손절 -3%, 익절 +5%):")
    print(f"  승률: {win_rate:.1f}%")
    print(f"  평균 수익: {avg_win_pct:.3f}%")
    print(f"  평균 손실: {avg_loss_pct:.3f}%")
    print(f"  기대값: {win_rate/100 * avg_win_pct + (1-win_rate/100) * avg_loss_pct:.3f}%")
    
    # 제안 A
    new_wins = [min(p['pnl_pct'], 1.0) if p['pnl_pct'] > 0 else p['pnl_pct'] for p in positions]
    new_losses = [max(p['pnl_pct'], -2.0) if p['pnl_pct'] < 0 else p['pnl_pct'] for p in positions]
    
    new_win_positions = [x for x in new_wins if x > 0]
    new_loss_positions = [x for x in new_losses if x < 0]
    
    new_win_rate = len(new_win_positions) / len(positions) * 100
    new_avg_win = statistics.mean(new_win_positions) if new_win_positions else 0
    new_avg_loss = statistics.mean(new_loss_positions) if new_loss_positions else 0
    
    print("\n제안 A (손절 -2%, 익절 +1%):")
    print(f"  승률: {new_win_rate:.1f}% (변화: {new_win_rate - win_rate:+.1f}%p)")
    print(f"  평균 수익: {new_avg_win:.3f}%")
    print(f"  평균 손실: {new_avg_loss:.3f}%")
    print(f"  기대값: {new_win_rate/100 * new_avg_win + (1-new_win_rate/100) * new_avg_loss:.3f}%")
    print(f"  위험/보상: {abs(new_avg_win/new_avg_loss):.2f}")


if __name__ == "__main__":
    analyze_actual_trades()
