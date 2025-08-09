#!/usr/bin/env python3
"""
AI 건강분석 고도화 보고서 이메일 발송 스크립트
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import argparse

def send_report_email(recipient_email, smtp_server=None, smtp_port=None, sender_email=None, sender_password=None):
    """
    AI 건강분석 고도화 보고서를 이메일로 발송
    
    Args:
        recipient_email: 수신자 이메일 주소
        smtp_server: SMTP 서버 주소
        smtp_port: SMTP 포트 번호
        sender_email: 발신자 이메일 주소
        sender_password: 발신자 이메일 비밀번호
    """
    
    # 보고서 파일 경로
    report_dir = "/Users/vibetj/coding/center/docs"
    md_file = os.path.join(report_dir, "ai-health-analysis-report.md")
    html_file = os.path.join(report_dir, "ai-health-analysis-report.html")
    
    # 파일 존재 확인
    if not os.path.exists(md_file) or not os.path.exists(html_file):
        print("Error: 보고서 파일을 찾을 수 없습니다.")
        return False
    
    # HTML 파일 읽기
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 이메일 메시지 구성
    msg = MIMEMultipart('mixed')
    msg['Subject'] = f'[AIBIO 센터] AI 건강분석 시스템 고도화 보고서 - {datetime.now().strftime("%Y년 %m월 %d일")}'
    msg['From'] = sender_email or 'AIBIO Center <noreply@aibio.center>'
    msg['To'] = recipient_email
    
    # 이메일 본문 (HTML)
    email_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #667eea; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .summary {{ background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .highlight {{ color: #667eea; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>AI 건강분석 시스템 고도화 보고서</h2>
        </div>
        
        <div class="content">
            <p>안녕하세요,</p>
            
            <p>AIBIO 센터의 AI 건강분석 시스템 고도화를 위한 심층 분석 보고서를 보내드립니다.</p>
            
            <div class="summary">
                <h3>보고서 주요 내용</h3>
                <ul>
                    <li><span class="highlight">현재 시스템 문제점 분석</span>: 데이터 통합, AI 분석, UX 한계점</li>
                    <li><span class="highlight">5가지 대표 페르소나</span>: 직장인, 주부, 대학생, 사업가, 은퇴자</li>
                    <li><span class="highlight">페르소나별 시뮬레이션</span>: 30가지 케이스 중 5가지 심층 분석</li>
                    <li><span class="highlight">개선 방향</span>: AI 엔진 구축, 예측 분석, 개인화 추천</li>
                    <li><span class="highlight">구현 로드맵</span>: 12개월 단계별 실행 계획</li>
                </ul>
            </div>
            
            <p>첨부된 파일:</p>
            <ul>
                <li><strong>HTML 버전</strong>: 웹 브라우저에서 바로 열어보실 수 있습니다.</li>
                <li><strong>Markdown 버전</strong>: 문서 편집이나 공유가 용이합니다.</li>
            </ul>
            
            <p>보고서 검토 후 고도화 방향에 대한 의견을 주시면 감사하겠습니다.</p>
            
            <p>감사합니다.</p>
        </div>
        
        <div class="footer">
            <p>AIBIO Center | AI-powered Healthcare Solutions</p>
            <p>이 이메일은 자동으로 발송되었습니다.</p>
        </div>
    </body>
    </html>
    """
    
    # HTML 본문 추가
    html_part = MIMEText(email_body, 'html')
    msg.attach(html_part)
    
    # MD 파일 첨부
    with open(md_file, 'rb') as f:
        md_attachment = MIMEBase('application', 'octet-stream')
        md_attachment.set_payload(f.read())
        encoders.encode_base64(md_attachment)
        md_attachment.add_header('Content-Disposition', f'attachment; filename="ai-health-analysis-report.md"')
        msg.attach(md_attachment)
    
    # HTML 파일 첨부
    with open(html_file, 'rb') as f:
        html_attachment = MIMEBase('application', 'octet-stream')
        html_attachment.set_payload(f.read())
        encoders.encode_base64(html_attachment)
        html_attachment.add_header('Content-Disposition', f'attachment; filename="ai-health-analysis-report.html"')
        msg.attach(html_attachment)
    
    # 이메일 발송 시뮬레이션 (실제 발송을 위해서는 SMTP 설정 필요)
    print(f"이메일 발송 준비 완료:")
    print(f"- 수신자: {recipient_email}")
    print(f"- 제목: {msg['Subject']}")
    print(f"- 첨부파일: ai-health-analysis-report.md, ai-health-analysis-report.html")
    
    # 실제 SMTP 발송 코드 (설정이 제공된 경우)
    if smtp_server and smtp_port and sender_email and sender_password:
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                print("이메일이 성공적으로 발송되었습니다.")
                return True
        except Exception as e:
            print(f"이메일 발송 중 오류 발생: {e}")
            return False
    else:
        print("\n[참고] 실제 이메일 발송을 위해서는 SMTP 서버 설정이 필요합니다.")
        print("Gmail 사용 예시:")
        print("  python send_report_email.py --smtp-server smtp.gmail.com --smtp-port 587 \\")
        print("  --sender-email your-email@gmail.com --sender-password your-app-password")
        return True

def main():
    parser = argparse.ArgumentParser(description='AI 건강분석 고도화 보고서 이메일 발송')
    parser.add_argument('--recipient', default='ej8641@gmail.com', help='수신자 이메일 주소')
    parser.add_argument('--smtp-server', help='SMTP 서버 주소 (예: smtp.gmail.com)')
    parser.add_argument('--smtp-port', type=int, default=587, help='SMTP 포트 번호')
    parser.add_argument('--sender-email', help='발신자 이메일 주소')
    parser.add_argument('--sender-password', help='발신자 이메일 비밀번호 (앱 비밀번호)')
    
    args = parser.parse_args()
    
    success = send_report_email(
        recipient_email=args.recipient,
        smtp_server=args.smtp_server,
        smtp_port=args.smtp_port,
        sender_email=args.sender_email,
        sender_password=args.sender_password
    )
    
    if success:
        print("\n보고서 발송 프로세스가 완료되었습니다.")
    else:
        print("\n보고서 발송 중 문제가 발생했습니다.")

if __name__ == "__main__":
    main()