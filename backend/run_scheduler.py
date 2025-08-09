"""스케줄러 실행 스크립트"""
import schedule
import time
from datetime import datetime
from services.scheduled_tasks import ScheduledTasks
from core.logging_config import setup_logging, get_logger

# 로깅 설정
setup_logging()
logger = get_logger(__name__)


def run_package_expiry_check():
    """패키지 만료 확인 작업 실행"""
    logger.info("패키지 만료 확인 작업 시작")
    ScheduledTasks.check_package_expiry()


def run_daily_report():
    """일일 리포트 작업 실행"""
    logger.info("일일 리포트 작업 시작")
    ScheduledTasks.send_daily_report()


def setup_schedule():
    """스케줄 설정"""
    # 매일 오전 9시에 패키지 만료 확인
    schedule.every().day.at("09:00").do(run_package_expiry_check)
    
    # 매일 오전 8시에 일일 리포트
    schedule.every().day.at("08:00").do(run_daily_report)
    
    # 테스트를 위한 즉시 실행 (개발 중)
    # run_package_expiry_check()
    # run_daily_report()
    
    logger.info("스케줄러 설정 완료")
    logger.info(f"다음 실행 시간: {schedule.next_run()}")


def main():
    """메인 실행 함수"""
    logger.info("알림 스케줄러 시작")
    
    # 스케줄 설정
    setup_schedule()
    
    # 무한 루프로 스케줄 실행
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            logger.info("스케줄러 종료")
            break
        except Exception as e:
            logger.error(f"스케줄러 오류: {str(e)}")
            time.sleep(60)


if __name__ == "__main__":
    main()