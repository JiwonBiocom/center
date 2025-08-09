from fastapi import APIRouter, Depends
import requests
from core.auth import get_current_user
from models.user import User

router = APIRouter()

@router.get("/server-ip")
@router.get("/server-ip/")
async def get_server_ip(current_user: User = Depends(get_current_user)):
    """서버의 외부 IP 주소 확인 (관리자만)"""

    if current_user.role != "admin":
        return {"error": "관리자만 접근 가능합니다"}

    try:
        # 외부 서비스를 통해 IP 확인
        response = requests.get("https://api.ipify.org?format=text", timeout=5)
        if response.status_code == 200:
            server_ip = response.text.strip()

            # 알리고 허용 범위 확인
            is_allowed = server_ip.startswith("180.65.83.")

            return {
                "server_ip": server_ip,
                "aligo_allowed_range": "180.65.83.0/24",
                "is_ip_allowed": is_allowed,
                "message": "IP가 알리고 허용 범위에 포함됩니다." if is_allowed else "IP를 알리고에 등록해야 합니다."
            }
    except Exception as e:
        return {"error": f"IP 확인 실패: {str(e)}"}

    return {"error": "IP를 확인할 수 없습니다"}
