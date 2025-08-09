"""모든 모델 import 확인 스크립트"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models.user import User
    print("✓ User")
    from models.customer import Customer
    print("✓ Customer")
    from models.service import ServiceUsage, ServiceType
    print("✓ ServiceUsage, ServiceType")
    from models.payment import Payment
    print("✓ Payment")
    from models.package import Package, PackagePurchase
    print("✓ Package, PackagePurchase")
    from models.lead_management import LeadConsultationHistory, ReregistrationCampaign, CampaignTarget
    print("✓ LeadConsultationHistory, ReregistrationCampaign, CampaignTarget")
    from models.notification import Notification, NotificationSettings
    print("✓ Notification, NotificationSettings")
    from models.reservation import Reservation
    print("✓ Reservation")
    from models.kit import KitType, KitManagement
    print("✓ KitType, KitManagement")
    from models.customer_extended import CustomerPreference, CustomerAnalytics, MarketingLead, KitReceipt
    print("✓ CustomerPreference, CustomerAnalytics, MarketingLead, KitReceipt")
    from models.staff_schedule import StaffSchedule
    print("✓ StaffSchedule")
    from models.inbody import InBodyData
    print("✓ InBodyData")
    from models.system import SystemSetting, AuditLog
    print("✓ SystemSetting, AuditLog")
    
    print("\n모든 모델 import 성공!")
except ImportError as e:
    print(f"\n❌ Import 에러: {e}")