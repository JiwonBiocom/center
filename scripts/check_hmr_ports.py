#!/usr/bin/env python3
"""
HMR WebSocket 포트 상태 확인 스크립트
"""
import subprocess
import socket
import sys

def check_port_available(port):
    """포트가 사용 가능한지 확인"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('localhost', port))
        return result != 0  # 연결 실패하면 포트 사용 가능
    finally:
        sock.close()

def check_port_usage(port):
    """포트 사용 중인 프로세스 확인"""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

def main():
    print("🔍 HMR WebSocket 포트 상태 확인\n")
    
    # 필요한 포트들
    ports_to_check = {
        5173: "Vite 개발 서버",
        24678: "HMR WebSocket",
        8000: "Backend API"
    }
    
    all_good = True
    
    for port, description in ports_to_check.items():
        available = check_port_available(port)
        usage = check_port_usage(port)
        
        if port == 5173 or port == 8000:
            # 이 포트들은 사용 중이어야 함
            if not available:
                print(f"✅ 포트 {port} ({description}): 정상 사용 중")
                if usage:
                    lines = usage.split('\n')[1:]  # 헤더 제외
                    for line in lines:
                        if line.strip():
                            print(f"   📍 {line.strip()}")
            else:
                print(f"❌ 포트 {port} ({description}): 사용 중이 아님")
                all_good = False
        else:
            # HMR 포트는 사용 가능해야 함
            if available:
                print(f"✅ 포트 {port} ({description}): 사용 가능")
            else:
                print(f"⚠️  포트 {port} ({description}): 이미 사용 중")
                if usage:
                    lines = usage.split('\n')[1:]
                    for line in lines:
                        if line.strip():
                            print(f"   📍 {line.strip()}")
                print(f"   💡 다른 포트 사용을 권장합니다.")
    
    print(f"\n{'='*50}")
    
    if all_good:
        print("✅ HMR 사용 준비 완료!")
        print("\n🚀 다음 명령어로 HMR 활성화 개발 시작:")
        print("   npm run dev:fast")
    else:
        print("⚠️  일부 포트에 문제가 있습니다.")
        print("\n🛡️  안정적인 개발 모드 사용:")
        print("   npm run dev:stable")
    
    print(f"\n📖 상세 정보:")
    print(f"   frontend/WEBSOCKET-FIX.md 참조")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())