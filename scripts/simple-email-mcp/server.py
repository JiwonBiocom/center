#!/usr/bin/env python3
"""
Simple Email MCP Server
간단한 이메일 발송을 위한 MCP 서버
"""

import json
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Any, Dict, List
from datetime import datetime

# MCP Server 기본 구조
class SimpleEmailMCPServer:
    def __init__(self):
        self.name = "simple-email"
        self.version = "1.0.0"
        self.smtp_config = {
            "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "user": os.getenv("SMTP_USER", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "from": os.getenv("SMTP_FROM", "")
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 요청 처리"""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "tools/list":
            return self.list_tools()
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return await self.call_tool(tool_name, arguments)
        else:
            return {"error": f"Unknown method: {method}"}
    
    def list_tools(self) -> Dict[str, Any]:
        """사용 가능한 도구 목록 반환"""
        return {
            "tools": [
                {
                    "name": "send_email",
                    "description": "이메일을 발송합니다",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "수신자 이메일 주소"
                            },
                            "subject": {
                                "type": "string",
                                "description": "이메일 제목"
                            },
                            "body": {
                                "type": "string",
                                "description": "이메일 본문 (HTML 지원)"
                            },
                            "attachments": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "첨부파일 경로 목록"
                            }
                        },
                        "required": ["to", "subject", "body"]
                    }
                },
                {
                    "name": "send_report",
                    "description": "AI 건강분석 보고서를 이메일로 발송합니다",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "수신자 이메일 주소"
                            }
                        },
                        "required": ["to"]
                    }
                }
            ]
        }
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """도구 실행"""
        if tool_name == "send_email":
            return await self.send_email(
                to=arguments.get("to"),
                subject=arguments.get("subject"),
                body=arguments.get("body"),
                attachments=arguments.get("attachments", [])
            )
        elif tool_name == "send_report":
            return await self.send_report(to=arguments.get("to"))
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    async def send_email(self, to: str, subject: str, body: str, attachments: List[str] = None) -> Dict[str, Any]:
        """이메일 발송"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['from']
            msg['To'] = to
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0900")
            
            # 본문 추가
            msg.attach(MIMEText(body, 'html'))
            
            # 첨부파일 추가
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{os.path.basename(filepath)}"'
                            )
                            msg.attach(part)
            
            # 이메일 발송
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['user'], self.smtp_config['password'])
                server.send_message(msg)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"이메일이 성공적으로 발송되었습니다.\n수신자: {to}\n제목: {subject}"
                    }
                ]
            }
        except Exception as e:
            return {
                "error": f"이메일 발송 실패: {str(e)}"
            }
    
    async def send_report(self, to: str) -> Dict[str, Any]:
        """AI 건강분석 보고서 발송"""
        report_dir = "/Users/vibetj/coding/center/docs"
        md_file = os.path.join(report_dir, "ai-health-analysis-report.md")
        html_file = os.path.join(report_dir, "ai-health-analysis-report.html")
        
        if not os.path.exists(md_file) or not os.path.exists(html_file):
            return {"error": "보고서 파일을 찾을 수 없습니다."}
        
        subject = f"[AIBIO 센터] AI 건강분석 시스템 고도화 보고서 - {datetime.now().strftime('%Y년 %m월 %d일')}"
        
        body = """
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>AI 건강분석 시스템 고도화 보고서</h2>
            <p>안녕하세요,</p>
            <p>AIBIO 센터의 AI 건강분석 시스템 고도화를 위한 심층 분석 보고서를 보내드립니다.</p>
            <h3>보고서 주요 내용</h3>
            <ul>
                <li>현재 시스템 문제점 분석</li>
                <li>5가지 대표 페르소나 시뮬레이션</li>
                <li>AI 기반 개선 방향</li>
                <li>12개월 구현 로드맵</li>
            </ul>
            <p>첨부파일을 확인해주세요.</p>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=to,
            subject=subject,
            body=body,
            attachments=[md_file, html_file]
        )

async def main():
    """MCP 서버 실행"""
    server = SimpleEmailMCPServer()
    
    # 표준 입출력으로 통신
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, input)
            request = json.loads(line)
            response = await server.handle_request(request)
            print(json.dumps(response))
        except Exception as e:
            print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    asyncio.run(main())