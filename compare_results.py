"""
전략 버전별 백테스트 결과 비교
"""
import os
import json
import csv
from typing import List, Dict
import statistics


def parse_report(report_path: str) -> Dict:
    """리포트 파일에서 메트릭 추출"""
    if not os.path.exists(report_path):
        return {}
    
    with open(report_path, "r") as f:
        content = f.read()
    
    metrics = {}
    
    # 패턴 매칭
    import re
    
    patterns = {
        "cumulative_return": r"Cumulative Return: ([-\d.]+)%",
        "mdd": r"MDD: ([-\d.]+)%",
        "win_rate": r"Win Rate: ([\d.]+)%",
        "risk_reward": r"Risk/Reward: ([\d.]+)",
        "trade_count": r"Trade Count: (\d+)",
        "avg_holding": r"Average Holding Time: (.+)",
        "total_fees": r"Total Fees: ([\d.]+)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            value = match.group(1)
            # 숫자 변환
            if key in ["avg_holding"]:
                metrics[key] = value
            elif key == "trade_count":
                metrics[key] = int(value)
            else:
                metrics[key] = float(value)
    
    return metrics


def analyze_trades_csv(trades_path: str) -> Dict:
    """trades.csv 상세 분석"""
    if not os.path.exists(trades_path):
        return {}
    
    trades = []
    with open(trades_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append({
                "signal": row["signal"],
                "pnl": float(row["pnl"])
            })
    
    # 매도 거래만 추출
    sell_trades = [t for t in trades if t["signal"] == "sell" and t["pnl"] != 0]
    
    if not sell_trades:
        return {}
    
    wins = [t["pnl"] for t in sell_trades if t["pnl"] > 0]
    losses = [t["pnl"] for t in sell_trades if t["pnl"] < 0]
    
    return {
        "total_trades": len(sell_trades),
        "wins": len(wins),
        "losses": len(losses),
        "avg_win": statistics.mean(wins) if wins else 0,
        "avg_loss": statistics.mean(losses) if losses else 0,
        "max_win": max(wins) if wins else 0,
        "max_loss": min(losses) if losses else 0,
        "total_pnl": sum(t["pnl"] for t in sell_trades)
    }


def compare_all_results():
    """모든 버전 결과 비교"""
    versions_file = os.path.join("strategy_versions", "versions.json")
    
    if not os.path.exists(versions_file):
        print("❌ 버전 파일이 없습니다.")
        return
    
    with open(versions_file, "r") as f:
        data = json.load(f)
    
    versions = data["versions"]
    
    if not versions:
        print("❌ 등록된 버전이 없습니다.")
        return
    
    # 결과 수집
    results = []
    
    for version_info in versions:
        version_id = version_info["version_id"]
        version_dir = os.path.join("strategy_versions", version_id)
        
        # 메타데이터 로드
        metadata_path = os.path.join(version_dir, "metadata.json")
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        # 리포트 파싱
        report_path = os.path.join(version_dir, "results", "report.txt")
        metrics = parse_report(report_path)
        
        # CSV 분석
        trades_path = os.path.join(version_dir, "results", "trades.csv")
        trades_metrics = analyze_trades_csv(trades_path)
        
        result = {
            "version_id": version_id,
            "version_name": version_info["version_name"],
            "description": version_info["description"],
            "config": metadata["config"],
            "strategy": metadata["strategy_params"],
            "metrics": metrics,
            "trades": trades_metrics,
            "status": version_info.get("status", "unknown")
        }
        
        results.append(result)
    
    # 결과 출력
    print("\n" + "="*100)
    print("전략 버전별 백테스트 결과 비교")
    print("="*100)
    
    # 테이블 헤더
    print("\n{:<25} {:<10} {:<10} {:<10} {:<12} {:<10} {:<10}".format(
        "버전", "수익률%", "MDD%", "승률%", "위험/보상", "거래수", "수수료"
    ))
    print("-"*100)
    
    # 각 버전 출력
    for result in results:
        if result["status"] != "tested":
            continue
        
        m = result["metrics"]
        name = result["version_name"][:23]
        
        print("{:<25} {:>9.2f} {:>9.2f} {:>9.2f} {:>11.2f} {:>9d} {:>9.2f}".format(
            name,
            m.get("cumulative_return", 0),
            m.get("mdd", 0),
            m.get("win_rate", 0),
            m.get("risk_reward", 0),
            m.get("trade_count", 0),
            m.get("total_fees", 0)
        ))
    
    # 상세 비교
    print("\n" + "="*100)
    print("상세 비교")
    print("="*100)
    
    for result in results:
        if result["status"] != "tested":
            continue
        
        print(f"\n버전: {result['version_name']}")
        print(f"설명: {result['description']}")
        print(f"\n[설정]")
        print(f"  손절: {result['config']['STOP_LOSS_PCT']*100:.1f}%")
        print(f"  익절: {result['config']['TAKE_PROFIT_PCT']*100:.1f}%")
        print(f"  RSI 매수: {result['strategy']['RSI_BUY_THRESHOLD']}")
        print(f"  RSI 매도: {result['strategy']['RSI_SELL_THRESHOLD']}")
        
        m = result["metrics"]
        t = result["trades"]
        
        print(f"\n[성과]")
        print(f"  누적 수익률: {m.get('cumulative_return', 0):>7.2f}%")
        print(f"  최대 낙폭: {m.get('mdd', 0):>7.2f}%")
        print(f"  승률: {m.get('win_rate', 0):>7.2f}%")
        print(f"  위험/보상: {m.get('risk_reward', 0):>7.2f}")
        print(f"  거래 횟수: {m.get('trade_count', 0):>7d}회")
        
        if t:
            print(f"\n[거래 분석]")
            print(f"  총 거래: {t.get('total_trades', 0)}회")
            print(f"  승리: {t.get('wins', 0)}회 / 패배: {t.get('losses', 0)}회")
            print(f"  평균 수익: {t.get('avg_win', 0):>7.2f}원")
            print(f"  평균 손실: {t.get('avg_loss', 0):>7.2f}원")
            print(f"  최대 수익: {t.get('max_win', 0):>7.2f}원")
            print(f"  최대 손실: {t.get('max_loss', 0):>7.2f}원")
    
    # 최고 성과 버전
    print("\n" + "="*100)
    print("🏆 최고 성과 버전")
    print("="*100)
    
    tested_results = [r for r in results if r["status"] == "tested"]
    
    if tested_results:
        # 수익률 기준
        best_return = max(tested_results, 
                         key=lambda x: x["metrics"].get("cumulative_return", -999))
        print(f"\n📈 최고 수익률: {best_return['version_name']}")
        print(f"   수익률: {best_return['metrics'].get('cumulative_return', 0):.2f}%")
        
        # 승률 기준
        best_winrate = max(tested_results,
                          key=lambda x: x["metrics"].get("win_rate", 0))
        print(f"\n🎯 최고 승률: {best_winrate['version_name']}")
        print(f"   승률: {best_winrate['metrics'].get('win_rate', 0):.2f}%")
        
        # 위험/보상 기준
        best_rr = max(tested_results,
                     key=lambda x: x["metrics"].get("risk_reward", 0))
        print(f"\n⚖️  최고 위험/보상: {best_rr['version_name']}")
        print(f"   위험/보상: {best_rr['metrics'].get('risk_reward', 0):.2f}")
        
        # 거래 효율 (수익/거래수)
        best_efficiency = max(tested_results,
                             key=lambda x: x["metrics"].get("cumulative_return", 0) / 
                                          max(x["metrics"].get("trade_count", 1), 1))
        print(f"\n💎 최고 거래 효율: {best_efficiency['version_name']}")
        efficiency = best_efficiency['metrics'].get('cumulative_return', 0) / \
                    max(best_efficiency['metrics'].get('trade_count', 1), 1)
        print(f"   효율: {efficiency:.4f}% per trade")
    
    # 저장
    summary_file = os.path.join("strategy_versions", "comparison_summary.json")
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 비교 결과 저장: {summary_file}")


if __name__ == "__main__":
    compare_all_results()
