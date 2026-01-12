"""
전략 버전 관리 시스템
각 전략 버전별로 백테스트 결과를 독립적으로 저장하고 관리
"""
import os
import json
import shutil
from datetime import datetime
from typing import Dict, Optional
import subprocess


class StrategyVersionManager:
    """전략 버전 관리 클래스"""
    
    def __init__(self, base_dir: str = "strategy_versions"):
        self.base_dir = base_dir
        self.versions_file = os.path.join(base_dir, "versions.json")
        self._ensure_base_dir()
    
    def _ensure_base_dir(self):
        """기본 디렉토리 생성"""
        os.makedirs(self.base_dir, exist_ok=True)
        if not os.path.exists(self.versions_file):
            with open(self.versions_file, 'w') as f:
                json.dump({"versions": []}, f, indent=2)
    
    def create_version(self, 
                      version_name: str,
                      description: str,
                      config: Dict,
                      strategy_params: Dict) -> str:
        """
        새로운 전략 버전 생성
        
        Args:
            version_name: 버전 이름 (예: v1.0-baseline)
            description: 버전 설명
            config: config.py 설정값 딕셔너리
            strategy_params: strategy.py 파라미터 딕셔너리
        
        Returns:
            생성된 버전 디렉토리 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"{version_name}_{timestamp}"
        version_dir = os.path.join(self.base_dir, version_id)
        
        # 버전 디렉토리 생성
        os.makedirs(version_dir, exist_ok=True)
        os.makedirs(os.path.join(version_dir, "results"), exist_ok=True)
        os.makedirs(os.path.join(version_dir, "config"), exist_ok=True)
        os.makedirs(os.path.join(version_dir, "logs"), exist_ok=True)
        
        # 버전 메타데이터 저장
        metadata = {
            "version_id": version_id,
            "version_name": version_name,
            "description": description,
            "created_at": timestamp,
            "config": config,
            "strategy_params": strategy_params,
            "status": "created"
        }
        
        with open(os.path.join(version_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # 현재 코드 백업
        self._backup_code(version_dir)
        
        # 버전 목록에 추가
        self._register_version(metadata)
        
        print(f"✅ 버전 생성 완료: {version_id}")
        print(f"   디렉토리: {version_dir}")
        
        return version_dir
    
    def _backup_code(self, version_dir: str):
        """현재 코드 백업"""
        code_dir = os.path.join(version_dir, "code")
        os.makedirs(code_dir, exist_ok=True)
        
        # 주요 파일 복사
        files_to_backup = [
            "main.py",
            "config.py",
            "strategy.py",
            "backtest.py",
            "paper_broker.py",
            "report.py",
            "upbit_client.py"
        ]
        
        for filename in files_to_backup:
            if os.path.exists(filename):
                shutil.copy2(filename, os.path.join(code_dir, filename))
    
    def _register_version(self, metadata: Dict):
        """버전 목록에 등록"""
        with open(self.versions_file, 'r') as f:
            data = json.load(f)
        
        data["versions"].append({
            "version_id": metadata["version_id"],
            "version_name": metadata["version_name"],
            "created_at": metadata["created_at"],
            "description": metadata["description"],
            "status": metadata["status"]
        })
        
        with open(self.versions_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save_backtest_results(self, 
                             version_id: str,
                             trades_csv: str,
                             report_output: str):
        """백테스트 결과 저장"""
        version_dir = os.path.join(self.base_dir, version_id)
        if not os.path.exists(version_dir):
            raise ValueError(f"버전 {version_id}가 존재하지 않습니다.")
        
        results_dir = os.path.join(version_dir, "results")
        
        # trades.csv 복사
        if os.path.exists(trades_csv):
            shutil.copy2(trades_csv, os.path.join(results_dir, "trades.csv"))
        
        # 리포트 저장
        with open(os.path.join(results_dir, "report.txt"), 'w') as f:
            f.write(report_output)
        
        # 메타데이터 업데이트
        self._update_version_status(version_id, "tested")
        
        print(f"✅ 백테스트 결과 저장 완료: {version_id}")
    
    def _update_version_status(self, version_id: str, status: str):
        """버전 상태 업데이트"""
        version_dir = os.path.join(self.base_dir, version_id)
        metadata_file = os.path.join(version_dir, "metadata.json")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        metadata["status"] = status
        metadata["updated_at"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def list_versions(self):
        """버전 목록 출력"""
        with open(self.versions_file, 'r') as f:
            data = json.load(f)
        
        print("\n" + "="*80)
        print("전략 버전 목록")
        print("="*80)
        
        if not data["versions"]:
            print("등록된 버전이 없습니다.")
            return
        
        for v in data["versions"]:
            print(f"\n버전: {v['version_name']}")
            print(f"  ID: {v['version_id']}")
            print(f"  생성: {v['created_at']}")
            print(f"  상태: {v['status']}")
            print(f"  설명: {v['description']}")
    
    def compare_versions(self, version_id1: str, version_id2: str):
        """두 버전 비교"""
        v1_dir = os.path.join(self.base_dir, version_id1)
        v2_dir = os.path.join(self.base_dir, version_id2)
        
        # 메타데이터 로드
        with open(os.path.join(v1_dir, "metadata.json"), 'r') as f:
            meta1 = json.load(f)
        
        with open(os.path.join(v2_dir, "metadata.json"), 'r') as f:
            meta2 = json.load(f)
        
        print("\n" + "="*80)
        print(f"버전 비교: {meta1['version_name']} vs {meta2['version_name']}")
        print("="*80)
        
        # Config 비교
        print("\n[설정 차이]")
        config1 = meta1.get("config", {})
        config2 = meta2.get("config", {})
        
        all_keys = set(config1.keys()) | set(config2.keys())
        for key in sorted(all_keys):
            val1 = config1.get(key, "N/A")
            val2 = config2.get(key, "N/A")
            if val1 != val2:
                print(f"  {key}:")
                print(f"    {meta1['version_name']}: {val1}")
                print(f"    {meta2['version_name']}: {val2}")


def run_simulation_suite():
    """다양한 시뮬레이션 실행"""
    manager = StrategyVersionManager()
    
    print("="*80)
    print("전략 시뮬레이션 스위트")
    print("="*80)
    
    # 버전 정의
    simulations = [
        {
            "name": "v1.0-baseline",
            "description": "현재 전략 (손절 -3%, 익절 +5%)",
            "config": {
                "STOP_LOSS_PCT": 0.03,
                "TAKE_PROFIT_PCT": 0.05,
                "RSI_PERIOD": 14,
                "TRADE_AMOUNT_KRW": 10000.0
            },
            "strategy": {
                "RSI_BUY_THRESHOLD": 30,
                "RSI_SELL_THRESHOLD": 70
            }
        },
        {
            "name": "v1.1-tight-tp",
            "description": "익절 낮춤 (손절 -2%, 익절 +1%)",
            "config": {
                "STOP_LOSS_PCT": 0.02,
                "TAKE_PROFIT_PCT": 0.01,
                "RSI_PERIOD": 14,
                "TRADE_AMOUNT_KRW": 10000.0
            },
            "strategy": {
                "RSI_BUY_THRESHOLD": 30,
                "RSI_SELL_THRESHOLD": 70
            }
        },
        {
            "name": "v1.2-balanced",
            "description": "균형 (손절 -2.5%, 익절 +1.5%)",
            "config": {
                "STOP_LOSS_PCT": 0.025,
                "TAKE_PROFIT_PCT": 0.015,
                "RSI_PERIOD": 14,
                "TRADE_AMOUNT_KRW": 10000.0
            },
            "strategy": {
                "RSI_BUY_THRESHOLD": 30,
                "RSI_SELL_THRESHOLD": 70
            }
        },
        {
            "name": "v2.0-strict-rsi",
            "description": "RSI 엄격 + 손익 조정 (RSI 25/75, 손절 -2.5%, 익절 +1.5%)",
            "config": {
                "STOP_LOSS_PCT": 0.025,
                "TAKE_PROFIT_PCT": 0.015,
                "RSI_PERIOD": 14,
                "TRADE_AMOUNT_KRW": 10000.0
            },
            "strategy": {
                "RSI_BUY_THRESHOLD": 25,
                "RSI_SELL_THRESHOLD": 75
            }
        },
        {
            "name": "v2.1-conservative",
            "description": "보수적 (RSI 25/75, 손절 -2%, 익절 +1%)",
            "config": {
                "STOP_LOSS_PCT": 0.02,
                "TAKE_PROFIT_PCT": 0.01,
                "RSI_PERIOD": 14,
                "TRADE_AMOUNT_KRW": 10000.0
            },
            "strategy": {
                "RSI_BUY_THRESHOLD": 25,
                "RSI_SELL_THRESHOLD": 75
            }
        }
    ]
    
    # 각 버전 생성
    created_versions = []
    for sim in simulations:
        version_dir = manager.create_version(
            version_name=sim["name"],
            description=sim["description"],
            config=sim["config"],
            strategy_params=sim["strategy"]
        )
        created_versions.append((sim, version_dir))
        print()
    
    # 버전 목록 출력
    manager.list_versions()
    
    return manager, created_versions


if __name__ == "__main__":
    # 시뮬레이션 스위트 실행
    manager, versions = run_simulation_suite()
    
    print("\n" + "="*80)
    print("다음 단계:")
    print("="*80)
    print("1. run_all_simulations.py를 실행하여 모든 버전 백테스트")
    print("2. compare_results.py로 결과 비교")
    print("3. 최적 버전을 선택하여 적용")
