"""영수증 생성 유틸리티"""
from datetime import datetime
from typing import Dict, Optional


def generate_receipt_html(payment_data: Dict, customer_data: Dict, company_info: Optional[Dict] = None) -> str:
    """영수증 HTML 생성"""
    
    if not company_info:
        company_info = {
            "name": "AIBIO 헬스케어 센터",
            "address": "서울특별시 강남구 테헤란로 123",
            "tel": "02-1234-5678",
            "business_no": "123-45-67890",
            "representative": "홍길동"
        }
    
    # 날짜 포맷팅
    payment_date = payment_data.get('payment_date', datetime.now())
    if isinstance(payment_date, str):
        payment_date = datetime.fromisoformat(payment_date)
    
    # 금액 포맷팅
    amount = payment_data.get('amount', 0)
    amount_str = f"{amount:,}원"
    
    # 결제 방법 한글 변환
    payment_methods = {
        'card': '신용카드',
        'cash': '현금',
        'transfer': '계좌이체',
        'kakao': '카카오페이',
        'naver': '네이버페이'
    }
    payment_method = payment_methods.get(payment_data.get('payment_method', ''), payment_data.get('payment_method', ''))
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>영수증</title>
        <style>
            @media print {{
                body {{ margin: 0; }}
                .no-print {{ display: none; }}
            }}
            
            body {{
                font-family: 'Malgun Gothic', sans-serif;
                margin: 20px;
                max-width: 800px;
                margin: 0 auto;
            }}
            
            .receipt {{
                border: 2px solid #333;
                padding: 30px;
                background: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 3px double #333;
                padding-bottom: 20px;
            }}
            
            .title {{
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
                letter-spacing: 5px;
            }}
            
            .company-info {{
                font-size: 14px;
                color: #666;
                line-height: 1.6;
            }}
            
            .content {{
                margin: 30px 0;
            }}
            
            .info-row {{
                display: flex;
                margin-bottom: 15px;
                font-size: 16px;
            }}
            
            .label {{
                font-weight: bold;
                width: 150px;
                flex-shrink: 0;
            }}
            
            .value {{
                flex: 1;
            }}
            
            .amount-section {{
                margin: 30px 0;
                padding: 20px;
                background: #f5f5f5;
                border-radius: 5px;
                text-align: center;
            }}
            
            .amount-label {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            
            .amount-value {{
                font-size: 36px;
                font-weight: bold;
                color: #2563eb;
            }}
            
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                text-align: center;
                font-size: 14px;
                color: #666;
            }}
            
            .stamp-area {{
                float: right;
                margin-top: 20px;
                width: 100px;
                height: 100px;
                border: 2px solid #999;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                font-weight: bold;
                color: #999;
            }}
            
            .print-button {{
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 20px;
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }}
            
            .print-button:hover {{
                background: #1d4ed8;
            }}
            
            @media screen and (max-width: 600px) {{
                .receipt {{ padding: 20px; }}
                .title {{ font-size: 24px; }}
                .info-row {{ 
                    flex-direction: column;
                    margin-bottom: 10px;
                }}
                .label {{ 
                    width: auto;
                    margin-bottom: 5px;
                }}
            }}
        </style>
    </head>
    <body>
        <button class="print-button no-print" onclick="window.print()">🖨️ 인쇄하기</button>
        
        <div class="receipt">
            <div class="header">
                <div class="title">영 수 증</div>
                <div class="company-info">
                    <div>{company_info['name']}</div>
                    <div>{company_info['address']}</div>
                    <div>TEL: {company_info['tel']} | 사업자번호: {company_info['business_no']}</div>
                    <div>대표: {company_info['representative']}</div>
                </div>
            </div>
            
            <div class="content">
                <div class="info-row">
                    <div class="label">영수증 번호:</div>
                    <div class="value">#{payment_data.get('payment_id', 'N/A')}</div>
                </div>
                
                <div class="info-row">
                    <div class="label">발행일:</div>
                    <div class="value">{payment_date.strftime('%Y년 %m월 %d일')}</div>
                </div>
                
                <div class="info-row">
                    <div class="label">고객명:</div>
                    <div class="value">{customer_data.get('name', '')}</div>
                </div>
                
                <div class="info-row">
                    <div class="label">연락처:</div>
                    <div class="value">{customer_data.get('phone', '')}</div>
                </div>
                
                <div class="info-row">
                    <div class="label">구매내역:</div>
                    <div class="value">{payment_data.get('purchase_type', '서비스 이용')}</div>
                </div>
                
                <div class="amount-section">
                    <div class="amount-label">결제금액</div>
                    <div class="amount-value">{amount_str}</div>
                </div>
                
                <div class="info-row">
                    <div class="label">결제방법:</div>
                    <div class="value">{payment_method}</div>
                </div>
                
                {f'''<div class="info-row">
                    <div class="label">카드사:</div>
                    <div class="value">{payment_data.get('card_holder_name', '')}</div>
                </div>''' if payment_data.get('payment_method') == 'card' and payment_data.get('card_holder_name') else ''}
                
                {f'''<div class="info-row">
                    <div class="label">승인번호:</div>
                    <div class="value">{payment_data.get('approval_number', '')}</div>
                </div>''' if payment_data.get('approval_number') else ''}
                
                <div class="info-row">
                    <div class="label">담당직원:</div>
                    <div class="value">{payment_data.get('payment_staff', '')}</div>
                </div>
            </div>
            
            <div class="stamp-area">
                직인
            </div>
            
            <div class="footer" style="clear: both;">
                <p>이용해 주셔서 감사합니다.</p>
                <p>본 영수증은 세금계산서 대용으로 사용하실 수 있습니다.</p>
            </div>
        </div>
        
        <script>
            // 자동으로 인쇄 대화상자 표시 (선택사항)
            // window.onload = function() {{ window.print(); }}
        </script>
    </body>
    </html>
    """
    
    return html


def generate_simple_receipt(payment_data: Dict, customer_data: Dict) -> str:
    """간단한 텍스트 영수증 생성"""
    
    payment_date = payment_data.get('payment_date', datetime.now())
    if isinstance(payment_date, str):
        payment_date = datetime.fromisoformat(payment_date)
    
    amount = payment_data.get('amount', 0)
    
    receipt = f"""
=====================================
           영  수  증
=====================================
AIBIO 헬스케어 센터
서울특별시 강남구 테헤란로 123
TEL: 02-1234-5678

영수증 번호: #{payment_data.get('payment_id', 'N/A')}
발행일: {payment_date.strftime('%Y-%m-%d %H:%M')}
-------------------------------------
고객명: {customer_data.get('name', '')}
연락처: {customer_data.get('phone', '')}
-------------------------------------
구매내역: {payment_data.get('purchase_type', '서비스 이용')}
결제금액: {amount:,}원
결제방법: {payment_data.get('payment_method', '')}
담당직원: {payment_data.get('payment_staff', '')}
=====================================
이용해 주셔서 감사합니다.
    """
    
    return receipt.strip()