#!/usr/bin/env python3
"""
서버의 외부 IP 주소 확인 스크립트
"""

import requests
import socket

def check_server_ip():
    """서버의 외부 IP 확인"""

    print("=== 서버 IP 확인 ===\n")

    # 방법 1: 외부 서비스를 통한 IP 확인
    try:
        # 여러 서비스 시도
        services = [
            "https://api.ipify.org?format=text",
            "https://ifconfig.me/ip",
            "https://icanhazip.com",
            "https://checkip.amazonaws.com"
        ]

        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    print(f"외부 IP (from {service}): {ip}")

                    # IP가 알리고 허용 범위에 있는지 확인
                    if ip.startswith("180.65.83."):
                        print("✅ 이 IP는 알리고 허용 범위(180.65.83.0/24)에 포함됩니다!")
                    else:
                        print("❌ 이 IP는 알리고 허용 범위에 포함되지 않습니다.")
                        print("   알리고 관리자 페이지에서 이 IP를 추가해야 합니다.")
                    break
            except:
                continue

    except Exception as e:
        print(f"외부 IP 확인 실패: {e}")

    # 방법 2: 호스트명 확인
    print(f"\n호스트명: {socket.gethostname()}")

    # 방법 3: 로컬 IP 확인
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"로컬 IP: {local_ip}")
    except:
        pass

if __name__ == "__main__":
    check_server_ip()
