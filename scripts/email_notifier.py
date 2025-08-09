#!/usr/bin/env python3
"""
Email Notification Service
Gmail을 통해 시스템 알림을 이메일로 전송합니다.
"""
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class EmailNotifier:
    def __init__(self, token_path='config/gmail_token.json'):
        """Gmail 서비스 초기화"""
        self.service = None
        self.sender_email = None
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path)
            self.service = build('gmail', 'v1', credentials=creds)
            
            # 발신자 이메일 설정 (프로필 권한이 없을 수 있으므로 환경변수 사용)
            self.sender_email = os.getenv('GMAIL_SENDER_EMAIL', 'noreply@aibio-system.com')
    
    def send_health_check_alert(self, recipients, health_report):
        """건강 체크 실패 알림 발송"""
        if not self.service:
            print("❌ Gmail service not initialized")
            return False
        
        subject = f"🚨 AIBIO 시스템 Health Check 실패 - {datetime.now().strftime('%Y-%m-%d')}"
        
        # HTML 이메일 본문 생성
        html_body = self._create_health_check_html(health_report)
        
        return self.send_email(recipients, subject, html_body, is_html=True)
    
    def send_schema_drift_alert(self, recipients, drift_report):
        """스키마 변경 알림 발송"""
        if not self.service:
            print("❌ Gmail service not initialized")
            return False
        
        subject = "📊 AIBIO 데이터베이스 스키마 변경 감지"
        
        # 마크다운을 HTML로 변환
        html_body = self._markdown_to_html(drift_report)
        
        return self.send_email(recipients, subject, html_body, is_html=True)
    
    def send_email(self, recipients, subject, body, is_html=False):
        """이메일 발송"""
        try:
            message = MIMEMultipart()
            message['to'] = ', '.join(recipients) if isinstance(recipients, list) else recipients
            message['from'] = self.sender_email
            message['subject'] = subject
            
            # 본문 추가
            mime_type = 'html' if is_html else 'plain'
            msg = MIMEText(body, mime_type)
            message.attach(msg)
            
            # base64 인코딩
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()).decode('utf-8')
            
            # 이메일 전송
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"✅ Email sent successfully! Message ID: {send_message['id']}")
            return True
            
        except HttpError as error:
            print(f"❌ An error occurred: {error}")
            return False
    
    def _create_health_check_html(self, report):
        """Health check 리포트를 HTML로 변환"""
        status_emoji = "✅" if report['overall_status'] == 'healthy' else "❌"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background-color: #f44336; color: white; padding: 20px; }}
                .content {{ padding: 20px; }}
                .status {{ font-size: 18px; margin: 10px 0; }}
                .healthy {{ color: #4CAF50; }}
                .unhealthy {{ color: #f44336; }}
                .timestamp {{ color: #666; font-size: 14px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨 AIBIO 시스템 Health Check 알림</h1>
            </div>
            <div class="content">
                <p class="timestamp">검사 시간: {report['timestamp']}</p>
                
                <h2>시스템 상태</h2>
                <p class="status {'healthy' if report['database_healthy'] else 'unhealthy'}">
                    {'✅' if report['database_healthy'] else '❌'} 데이터베이스: {'정상' if report['database_healthy'] else '비정상'}
                </p>
                <p class="status {'healthy' if report['api_healthy'] else 'unhealthy'}">
                    {'✅' if report['api_healthy'] else '❌'} API 서버: {'정상' if report['api_healthy'] else '비정상'}
                </p>
                <p class="status {'healthy' if report['overall_status'] == 'healthy' else 'unhealthy'}">
                    {status_emoji} 전체 상태: {report['overall_status'].upper()}
                </p>
                
                <h2>조치 필요 사항</h2>
                <ul>
                    {'<li>데이터베이스 연결을 확인해주세요.</li>' if not report['database_healthy'] else ''}
                    {'<li>API 서버 상태를 확인해주세요.</li>' if not report['api_healthy'] else ''}
                    <li>Railway 대시보드에서 로그를 확인해주세요.</li>
                    <li>필요시 서버를 재시작해주세요.</li>
                </ul>
                
                <p style="margin-top: 30px; color: #666; font-size: 12px;">
                    이 이메일은 AIBIO 시스템 자동 모니터링에 의해 발송되었습니다.
                </p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _markdown_to_html(self, markdown):
        """간단한 마크다운을 HTML로 변환"""
        html = markdown
        
        # 헤더 변환
        html = html.replace('### ', '<h3>').replace('\n## ', '</h3>\n<h2>').replace('## ', '<h2>')
        html = html.replace('\n', '</h2>\n', 1) if html.startswith('<h2>') else html
        
        # 리스트 변환
        lines = html.split('\n')
        in_list = False
        new_lines = []
        
        for line in lines:
            if line.startswith('- '):
                if not in_list:
                    new_lines.append('<ul>')
                    in_list = True
                new_lines.append(f'<li>{line[2:]}</li>')
            else:
                if in_list and not line.startswith('- '):
                    new_lines.append('</ul>')
                    in_list = False
                new_lines.append(line)
        
        if in_list:
            new_lines.append('</ul>')
        
        html = '\n'.join(new_lines)
        
        # 코드 블록 변환
        html = html.replace('`', '<code>', 1).replace('`', '</code>', 1)
        
        # 줄바꿈 처리
        html = html.replace('\n\n', '</p><p>').replace('\n', '<br>')
        html = f'<p>{html}</p>'
        
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
                h2 {{ color: #333; }}
                h3 {{ color: #666; }}
                code {{ background-color: #f4f4f4; padding: 2px 4px; }}
                ul {{ margin: 10px 0; }}
            </style>
        </head>
        <body>{html}</body>
        </html>
        """

# 단독 실행 테스트
if __name__ == "__main__":
    notifier = EmailNotifier()
    
    # 테스트 이메일 발송
    test_report = {
        'timestamp': datetime.now().isoformat(),
        'database_healthy': False,
        'api_healthy': True,
        'overall_status': 'unhealthy'
    }
    
    # 환경 변수에서 수신자 이메일 가져오기
    recipients = os.getenv('ALERT_EMAIL_RECIPIENTS', 'test@example.com').split(',')
    
    print(f"📧 Sending test email to: {recipients}")
    notifier.send_health_check_alert(recipients, test_report)