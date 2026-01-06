"""
자동 매매 스케줄러
5분마다 자동으로 거래 실행
"""
import schedule
import time
import subprocess
import sys
from datetime import datetime
from loguru import logger

# 로거 설정
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
logger.add("scheduler.log", rotation="1 day", retention="7 days", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")


def run_trading_bot():
    """트레이딩 봇 실행"""
    try:
        logger.info("="*60)
        logger.info("Starting trading bot execution")
        logger.info("="*60)
        
        # main.py 실행
        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
            timeout=120  # 2분 타임아웃
        )
        
        if result.returncode == 0:
            logger.success("✅ Trading bot executed successfully")
            if result.stdout:
                logger.info("Output: {}", result.stdout.strip())
        else:
            logger.error("❌ Trading bot execution failed")
            if result.stderr:
                logger.error("Error: {}", result.stderr.strip())
                
    except subprocess.TimeoutExpired:
        logger.error("⏰ Trading bot execution timeout (2 minutes)")
    except Exception as e:
        logger.exception("💥 Unexpected error: {}", e)


def main():
    """메인 함수"""
    logger.info("🤖 Minimi Trading Bot Scheduler Started")
    logger.info("⏱️  Schedule: Every 5 minutes")
    logger.info("🛑 Press Ctrl+C to stop")
    logger.info("")
    
    # 즉시 한 번 실행
    run_trading_bot()
    
    # 5분마다 실행 스케줄 등록
    schedule.every(5).minutes.do(run_trading_bot)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Scheduler stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
