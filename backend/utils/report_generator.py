"""보고서 생성 유틸리티"""
import io
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import pandas as pd
import numpy as np

# matplotlib 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False


class ReportGenerator:
    """보고서 생성 클래스"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_korean_styles()
    
    def _setup_korean_styles(self):
        """한글 스타일 설정"""
        # 제목 스타일
        self.styles.add(ParagraphStyle(
            name='KoreanTitle',
            fontName='Helvetica-Bold',
            fontSize=20,
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        # 부제목 스타일
        self.styles.add(ParagraphStyle(
            name='KoreanHeading',
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=12
        ))
        
        # 본문 스타일
        self.styles.add(ParagraphStyle(
            name='KoreanNormal',
            fontName='Helvetica',
            fontSize=10,
            spaceAfter=6
        ))
    
    def create_chart(self, chart_type: str, data: Dict[str, Any], title: str) -> io.BytesIO:
        """차트 생성"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if chart_type == 'bar':
            labels = list(data.keys())
            values = list(data.values())
            bars = ax.bar(labels, values, color='#4F46E5')
            
            # 막대 위에 값 표시
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height):,}',
                       ha='center', va='bottom')
        
        elif chart_type == 'line':
            labels = list(data.keys())
            values = list(data.values())
            ax.plot(labels, values, marker='o', linewidth=2, markersize=8, color='#4F46E5')
            
            # 데이터 포인트에 값 표시
            for i, (x, y) in enumerate(zip(labels, values)):
                ax.text(i, y, f'{int(y):,}', ha='center', va='bottom')
        
        elif chart_type == 'pie':
            labels = list(data.keys())
            values = list(data.values())
            colors_list = ['#4F46E5', '#7C3AED', '#EC4899', '#F59E0B', '#10B981', '#3B82F6']
            ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors_list[:len(labels)])
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        # 이미지로 저장
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer
    
    def generate_monthly_revenue_report(self, data: Dict[str, Any]) -> bytes:
        """월간 매출 보고서 생성"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # 제목
        title = f"{data['year']}년 {data['month']}월 매출 보고서"
        story.append(Paragraph(title, self.styles['KoreanTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # 요약 정보
        summary_data = [
            ['구분', '금액/건수'],
            ['총 매출액', f"{data['total_revenue']:,}원"],
            ['결제 건수', f"{data['total_transactions']:,}건"],
            ['일평균 매출', f"{data['daily_average']:,}원"],
            ['전월 대비', f"{data['month_over_month_growth']:+.1f}%"],
            ['전년 동월 대비', f"{data['year_over_year_growth']:+.1f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.5*inch))
        
        # 일별 매출 차트
        if 'daily_revenue' in data:
            story.append(Paragraph("일별 매출 추이", self.styles['KoreanHeading']))
            chart_img = self.create_chart('line', data['daily_revenue'], '일별 매출액')
            img = Image(chart_img, width=6*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 0.3*inch))
        
        # 서비스별 매출
        if 'service_revenue' in data:
            story.append(Paragraph("서비스별 매출 분포", self.styles['KoreanHeading']))
            chart_img = self.create_chart('pie', data['service_revenue'], '서비스별 매출 비중')
            img = Image(chart_img, width=5*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 0.3*inch))
        
        # 결제 방법별 통계
        if 'payment_methods' in data:
            story.append(PageBreak())
            story.append(Paragraph("결제 방법별 통계", self.styles['KoreanHeading']))
            
            method_data = [['결제 방법', '건수', '금액', '비율']]
            for method, stats in data['payment_methods'].items():
                method_data.append([
                    method,
                    f"{stats['count']:,}건",
                    f"{stats['amount']:,}원",
                    f"{stats['percentage']:.1f}%"
                ])
            
            method_table = Table(method_data, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
            method_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(method_table)
        
        # 문서 생성
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def generate_customer_analysis_report(self, data: Dict[str, Any]) -> bytes:
        """고객 분석 보고서 생성"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # 제목
        period = f"{data['start_date']} ~ {data['end_date']}"
        title = f"고객 분석 보고서 ({period})"
        story.append(Paragraph(title, self.styles['KoreanTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # 고객 통계 요약
        summary_data = [
            ['구분', '수치'],
            ['전체 고객 수', f"{data['total_customers']:,}명"],
            ['신규 고객', f"{data['new_customers']:,}명"],
            ['재방문 고객', f"{data['returning_customers']:,}명"],
            ['평균 방문 횟수', f"{data['avg_visits']:.1f}회"],
            ['평균 구매 금액', f"{data['avg_purchase_amount']:,}원"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.5*inch))
        
        # 지역별 고객 분포
        if 'region_distribution' in data:
            story.append(Paragraph("지역별 고객 분포", self.styles['KoreanHeading']))
            chart_img = self.create_chart('bar', data['region_distribution'], '지역별 고객 수')
            img = Image(chart_img, width=6*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 0.3*inch))
        
        # 유입 경로별 분석
        if 'referral_sources' in data:
            story.append(PageBreak())
            story.append(Paragraph("유입 경로별 분석", self.styles['KoreanHeading']))
            chart_img = self.create_chart('pie', data['referral_sources'], '유입 경로별 비중')
            img = Image(chart_img, width=5*inch, height=4*inch)
            story.append(img)
        
        # 상위 고객 리스트
        if 'top_customers' in data:
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("상위 고객 TOP 10", self.styles['KoreanHeading']))
            
            top_data = [['순위', '고객명', '방문 횟수', '총 구매액']]
            for i, customer in enumerate(data['top_customers'][:10], 1):
                top_data.append([
                    str(i),
                    customer['name'],
                    f"{customer['visits']:,}회",
                    f"{customer['total_amount']:,}원"
                ])
            
            top_table = Table(top_data, colWidths=[1*inch, 2*inch, 1.5*inch, 2.5*inch])
            top_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(top_table)
        
        # 문서 생성
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data