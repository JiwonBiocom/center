#!/usr/bin/env python3
"""
자동 콘솔 모니터링 시스템 - 설정 변경 후 자동으로 콘솔 메시지 확인
"""
import asyncio
import sys
import time
from playwright.async_api import async_playwright
from datetime import datetime
import subprocess
import signal
import os

class ConsoleMonitor:
    def __init__(self, url="http://localhost:5173"):
        self.url = url
        self.browser = None
        self.page = None
        self.console_messages = []
        self.errors = []
        self.warnings = []
        self.running = True
        
    async def start_monitoring(self):
        """모니터링 시작"""
        print(f"🔍 자동 콘솔 모니터링 시작: {self.url}")
        print("📌 Ctrl+C로 중지할 수 있습니다.\n")
        
        async with async_playwright() as p:
            # 브라우저 시작 (headless)
            self.browser = await p.chromium.launch(headless=True)
            context = await self.browser.new_context()
            self.page = await context.new_page()
            
            # 콘솔 메시지 리스너
            def handle_console(msg):
                timestamp = datetime.now().strftime('%H:%M:%S')
                message_data = {
                    'type': msg.type,
                    'text': msg.text,
                    'timestamp': timestamp
                }
                
                self.console_messages.append(message_data)
                
                # 실시간 출력
                if msg.type == 'error':
                    print(f"🚨 [{timestamp}] ERROR: {msg.text}")
                    self.errors.append(message_data)
                elif msg.type == 'warning':
                    print(f"⚠️  [{timestamp}] WARNING: {msg.text}")
                    self.warnings.append(message_data)
                elif msg.type == 'info':
                    print(f"ℹ️  [{timestamp}] INFO: {msg.text}")
                else:
                    print(f"📝 [{timestamp}] {msg.type.upper()}: {msg.text}")
            
            self.page.on("console", handle_console)
            
            # 페이지 에러 리스너
            def handle_page_error(err):
                timestamp = datetime.now().strftime('%H:%M:%S')
                error_text = str(err)
                print(f"💥 [{timestamp}] PAGE ERROR: {error_text}")
                self.errors.append({
                    'type': 'pageerror',
                    'text': error_text,
                    'timestamp': timestamp
                })
            
            self.page.on("pageerror", handle_page_error)
            
            try:
                # 초기 페이지 로드
                await self.load_page()
                
                # 주기적 체크 루프
                while self.running:
                    await asyncio.sleep(5)  # 5초마다 체크
                    
                    # 페이지 상태 확인
                    try:
                        await self.page.evaluate("console.log('🔄 Monitor alive')")
                    except:
                        print("🔌 페이지 연결 끊김, 재연결 시도...")
                        await self.load_page()
                        
            except KeyboardInterrupt:
                print("\n🛑 모니터링 중지됨")
            finally:
                await self.browser.close()
    
    async def load_page(self):
        """페이지 로드"""
        try:
            print(f"🔗 페이지 로드 중: {self.url}")
            response = await self.page.goto(self.url, wait_until='networkidle', timeout=10000)
            
            if response and response.ok:
                print(f"✅ 페이지 로드 성공 (상태: {response.status})")
            else:
                print(f"❌ 페이지 로드 실패 (상태: {response.status if response else 'None'})")
                
            # 2초 대기 (JavaScript 로드)
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"❌ 페이지 로드 에러: {str(e)}")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.running = False
    
    def get_summary(self):
        """요약 정보 반환"""
        return {
            'total_messages': len(self.console_messages),
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'last_errors': self.errors[-3:] if self.errors else [],
            'last_warnings': self.warnings[-3:] if self.warnings else []
        }

async def main():
    """메인 함수"""
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"
    
    monitor = ConsoleMonitor(url)
    
    # Ctrl+C 핸들러
    def signal_handler(sig, frame):
        print("\n🛑 모니터링 중지 요청됨...")
        monitor.stop_monitoring()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await monitor.start_monitoring()
    finally:
        # 최종 요약
        summary = monitor.get_summary()
        print(f"\n{'='*50}")
        print("📊 모니터링 요약")
        print(f"{'='*50}")
        print(f"총 메시지: {summary['total_messages']}개")
        print(f"에러: {summary['errors']}개")
        print(f"경고: {summary['warnings']}개")
        
        if summary['last_errors']:
            print(f"\n🚨 최근 에러:")
            for error in summary['last_errors']:
                print(f"  [{error['timestamp']}] {error['text']}")
        
        if summary['last_warnings']:
            print(f"\n⚠️  최근 경고:")
            for warning in summary['last_warnings']:
                print(f"  [{warning['timestamp']}] {warning['text']}")
        
        print(f"\n모니터링 완료!")

if __name__ == "__main__":
    asyncio.run(main())