"""
모든 전략 버전에 대해 백테스트 실행
"""
import os
import sys
import json
import subprocess
from datetime import datetime
import shutil


def backup_original_files():
    """원본 파일 백업"""
    backup_dir = "original_backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    files = ["config.py", "strategy.py", "backtest.py"]
    for filename in files:
        if os.path.exists(filename):
            shutil.copy2(filename, os.path.join(backup_dir, filename))
    
    print(f"✅ 원본 파일 백업 완료: {backup_dir}")


def restore_original_files():
    """원본 파일 복원"""
    backup_dir = "original_backup"
    if not os.path.exists(backup_dir):
        return
    
    for filename in os.listdir(backup_dir):
        src = os.path.join(backup_dir, filename)
        dst = filename
        shutil.copy2(src, dst)
    
    print(f"✅ 원본 파일 복원 완료")


def modify_config(config_params: dict):
    """config.py 수정"""
    # config.py 읽기
    with open("config.py", "r") as f:
        lines = f.readlines()
    
    # 수정할 라인 찾아서 변경
    modified_lines = []
    for line in lines:
        modified = False
        for key, value in config_params.items():
            if line.strip().startswith(f"{key} ="):
                if isinstance(value, str):
                    modified_lines.append(f'{key} = "{value}"\n')
                else:
                    modified_lines.append(f"{key} = {value}\n")
                modified = True
                break
        
        if not modified:
            modified_lines.append(line)
    
    # 파일 쓰기
    with open("config.py", "w") as f:
        f.writelines(modified_lines)


def modify_strategy(strategy_params: dict):
    """strategy.py 수정"""
    with open("strategy.py", "r") as f:
        content = f.read()
    
    # RSI 임계값 변경
    buy_threshold = strategy_params.get("RSI_BUY_THRESHOLD", 30)
    sell_threshold = strategy_params.get("RSI_SELL_THRESHOLD", 70)
    
    # 패턴 교체
    import re
    content = re.sub(
        r"if latest <= \d+:",
        f"if latest <= {buy_threshold}:",
        content
    )
    content = re.sub(
        r"if latest >= \d+:",
        f"if latest >= {sell_threshold}:",
        content
    )
    
    with open("strategy.py", "w") as f:
        f.write(content)


def run_backtest(version_id: str, days: int = 90):
    """백테스트 실행"""
    print(f"\n{'='*80}")
    print(f"백테스트 실행: {version_id}")
    print(f"{'='*80}")
    
    # 백테스트 실행
    result = subprocess.run(
        ["python", "backtest.py", "--ticker", "KRW-BTC", "--days", str(days)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ 백테스트 실패:")
        print(result.stderr)
        return False
    
    print(result.stdout)
    
    # 리포트 생성
    result = subprocess.run(
        ["python", "report.py"],
        capture_output=True,
        text=True
    )
    
    report_output = result.stdout
    print(report_output)
    
    # 결과 저장
    version_dir = os.path.join("strategy_versions", version_id)
    results_dir = os.path.join(version_dir, "results")
    
    # trades.csv 복사
    if os.path.exists("trades.csv"):
        shutil.copy2("trades.csv", os.path.join(results_dir, "trades.csv"))
    
    # 리포트 저장
    with open(os.path.join(results_dir, "report.txt"), "w") as f:
        f.write(report_output)
    
    # 메타데이터 업데이트
    metadata_file = os.path.join(version_dir, "metadata.json")
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    
    metadata["status"] = "tested"
    metadata["tested_at"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 결과 저장 완료: {results_dir}")
    
    return True


def run_all_simulations():
    """모든 시뮬레이션 실행"""
    # 버전 목록 로드
    versions_file = os.path.join("strategy_versions", "versions.json")
    
    if not os.path.exists(versions_file):
        print("❌ 버전 파일이 없습니다. version_manager.py를 먼저 실행하세요.")
        return
    
    with open(versions_file, "r") as f:
        data = json.load(f)
    
    versions = data["versions"]
    
    if not versions:
        print("❌ 등록된 버전이 없습니다.")
        return
    
    # 원본 백업
    backup_original_files()
    
    try:
        for version_info in versions:
            version_id = version_info["version_id"]
            version_dir = os.path.join("strategy_versions", version_id)
            
            # 메타데이터 로드
            with open(os.path.join(version_dir, "metadata.json"), "r") as f:
                metadata = json.load(f)
            
            config = metadata["config"]
            strategy_params = metadata["strategy_params"]
            
            print(f"\n{'='*80}")
            print(f"버전 설정: {version_info['version_name']}")
            print(f"{'='*80}")
            print(f"설명: {version_info['description']}")
            print(f"Config: {config}")
            print(f"Strategy: {strategy_params}")
            
            # 파일 수정
            modify_config(config)
            modify_strategy(strategy_params)
            
            # 백테스트 실행
            success = run_backtest(version_id)
            
            if not success:
                print(f"⚠️  {version_id} 백테스트 실패")
            
            print()
        
        print("\n" + "="*80)
        print("모든 시뮬레이션 완료!")
        print("="*80)
        print("결과 확인: python compare_results.py")
        
    finally:
        # 원본 복원
        restore_original_files()


if __name__ == "__main__":
    run_all_simulations()
