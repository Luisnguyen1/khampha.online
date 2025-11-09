"""
PDF Generator for Travel Plans
Generates beautiful PDF documents from travel plan data using WeasyPrint
"""
import os
import io
import base64
from datetime import datetime
from typing import Optional, Dict, Any, List
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import requests
from flask import render_template_string


class TravelPlanPDFGenerator:
    """Generate PDF documents for travel plans"""
    
    def __init__(self):
        """Initialize PDF generator with font configuration"""
        self.font_config = FontConfiguration()
        
    def generate_pdf(
        self, 
        plan: Dict[str, Any], 
        hotel: Optional[Dict[str, Any]] = None,
        flights: Optional[List[Dict[str, Any]]] = None
    ) -> bytes:
        """
        Generate PDF from travel plan data
        
        Args:
            plan: Travel plan dictionary
            hotel: Optional hotel data
            flights: Optional list of flight data
            
        Returns:
            PDF file as bytes
        """
        # Prepare data for template
        template_data = self._prepare_template_data(plan, hotel, flights)
        
        # Render HTML template
        html_content = self._render_html_template(template_data)
        
        # Generate PDF from HTML
        pdf_bytes = self._html_to_pdf(html_content)
        
        return pdf_bytes
    
    def _prepare_template_data(
        self, 
        plan: Dict[str, Any], 
        hotel: Optional[Dict[str, Any]],
        flights: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Prepare and format data for PDF template"""
        
        # Parse itinerary
        itinerary = plan.get('itinerary', [])
        if isinstance(itinerary, str):
            import json
            itinerary = json.loads(itinerary)
        
        # Calculate total costs
        activities_cost = 0
        if isinstance(itinerary, list):
            for day in itinerary:
                activities = day.get('activities', [])
                for activity in activities:
                    activities_cost += activity.get('cost', 0)
        
        hotel_cost = hotel.get('total_price', 0) if hotel else 0
        flights_cost = sum(f.get('price', 0) for f in (flights or []))
        total_cost = activities_cost + hotel_cost + flights_cost
        
        # Format dates
        start_date_formatted = self._format_date(plan.get('start_date'))
        end_date_formatted = self._format_date(plan.get('end_date'))
        
        return {
            'plan': plan,
            'hotel': hotel,
            'flights': flights or [],
            'itinerary': itinerary,
            'costs': {
                'activities': activities_cost,
                'hotel': hotel_cost,
                'flights': flights_cost,
                'total': total_cost
            },
            'start_date_formatted': start_date_formatted,
            'end_date_formatted': end_date_formatted,
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """Format ISO date to Vietnamese format"""
        if not date_str:
            return ""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%d/%m/%Y')
        except:
            return date_str
    
    def _format_currency(self, amount: float, currency: str = "VND") -> str:
        """Format currency for display"""
        if currency == "VND":
            return f"{amount:,.0f} ₫"
        return f"{amount:,.2f} {currency}"
    
    def _render_html_template(self, data: Dict[str, Any]) -> str:
        """Render HTML template with data"""
        
        template = PDF_TEMPLATE
        
        # Render with Flask template engine
        html = render_template_string(template, **data, format_currency=self._format_currency)
        
        return html
    
    def _html_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint"""
        
        # Create PDF
        pdf_file = HTML(string=html_content).write_pdf(
            font_config=self.font_config
        )
        
        return pdf_file


# PDF HTML Template with beautiful styling
PDF_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{{ plan.plan_name or plan.destination }}</title>
    <style>
        @page {
            size: A4;
            margin: 2cm 1.5cm;
            @top-right {
                content: "Trang " counter(page) " / " counter(pages);
                font-size: 10px;
                color: #666;
            }
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'DejaVu Sans', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }
        
        h1 {
            color: #13a4ec;
            font-size: 24pt;
            margin-bottom: 0.5cm;
            border-bottom: 3px solid #13a4ec;
            padding-bottom: 0.3cm;
        }
        
        h2 {
            color: #13a4ec;
            font-size: 18pt;
            margin-top: 0.8cm;
            margin-bottom: 0.4cm;
            page-break-after: avoid;
        }
        
        h3 {
            color: #111618;
            font-size: 14pt;
            margin-top: 0.5cm;
            margin-bottom: 0.3cm;
            page-break-after: avoid;
        }
        
        .header {
            text-align: center;
            margin-bottom: 1cm;
        }
        
        .subtitle {
            color: #666;
            font-size: 12pt;
            margin-top: 0.3cm;
        }
        
        .info-grid {
            display: table;
            width: 100%;
            margin: 0.5cm 0;
            padding: 0.5cm;
            background: #f9fafb;
            border-radius: 8px;
            page-break-inside: avoid;
        }
        
        .info-row {
            display: table-row;
        }
        
        .info-item {
            display: table-cell;
            width: 50%;
            padding: 0.3cm;
            vertical-align: top;
        }
        
        .info-label {
            font-weight: bold;
            color: #13a4ec;
            font-size: 10pt;
        }
        
        .info-value {
            margin-top: 0.1cm;
            color: #111618;
        }
        
        .day-section {
            margin: 0.7cm 0;
            page-break-inside: avoid;
            border-left: 4px solid #13a4ec;
            padding-left: 0.5cm;
        }
        
        .day-header {
            background: #e8f4fc;
            padding: 0.4cm;
            border-radius: 6px;
            margin-bottom: 0.4cm;
        }
        
        .day-title {
            font-size: 14pt;
            font-weight: bold;
            color: #13a4ec;
        }
        
        .activity {
            margin: 0.4cm 0 0.4cm 0.5cm;
            padding: 0.3cm;
            border-left: 2px solid #ddd;
            padding-left: 0.4cm;
            page-break-inside: avoid;
        }
        
        .activity-time {
            color: #13a4ec;
            font-weight: bold;
            font-size: 10pt;
        }
        
        .activity-title {
            font-weight: bold;
            margin-top: 0.1cm;
            font-size: 12pt;
        }
        
        .activity-description {
            color: #666;
            margin-top: 0.2cm;
            font-size: 10pt;
        }
        
        .activity-location {
            color: #888;
            font-size: 9pt;
            margin-top: 0.1cm;
        }
        
        .activity-location:before {
            content: "📍 ";
        }
        
        .activity-cost {
            color: #13a4ec;
            font-weight: bold;
            margin-top: 0.1cm;
        }
        
        .notes-box {
            background: #fff9e6;
            border: 2px solid #ffd966;
            border-radius: 6px;
            padding: 0.4cm;
            margin: 0.5cm 0;
            page-break-inside: avoid;
        }
        
        .notes-title {
            color: #d97706;
            font-weight: bold;
            margin-bottom: 0.2cm;
        }
        
        .notes-title:before {
            content: "💡 ";
        }
        
        .hotel-card, .flight-card {
            background: #f9fafb;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 0.5cm;
            margin: 0.5cm 0;
            page-break-inside: avoid;
        }
        
        .hotel-name, .flight-carrier {
            font-size: 14pt;
            font-weight: bold;
            color: #111618;
        }
        
        .hotel-rating {
            color: #fbbf24;
            margin-top: 0.1cm;
        }
        
        .hotel-details, .flight-details {
            margin-top: 0.3cm;
            color: #666;
            font-size: 10pt;
        }
        
        .price-box {
            background: #13a4ec;
            color: white;
            padding: 0.3cm;
            border-radius: 6px;
            text-align: right;
            margin-top: 0.3cm;
        }
        
        .price-label {
            font-size: 9pt;
            opacity: 0.9;
        }
        
        .price-value {
            font-size: 16pt;
            font-weight: bold;
            margin-top: 0.1cm;
        }
        
        .cost-summary {
            margin: 0.5cm 0;
            page-break-inside: avoid;
        }
        
        .cost-row {
            display: flex;
            justify-content: space-between;
            padding: 0.3cm;
            border-bottom: 1px solid #ddd;
        }
        
        .cost-total {
            background: #e8f4fc;
            font-weight: bold;
            font-size: 14pt;
            color: #13a4ec;
            padding: 0.4cm;
            border-radius: 6px;
            margin-top: 0.3cm;
        }
        
        .footer {
            margin-top: 1cm;
            padding-top: 0.5cm;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #888;
            font-size: 9pt;
        }
        
        ul {
            margin-left: 0.5cm;
            margin-top: 0.2cm;
        }
        
        li {
            margin: 0.1cm 0;
        }
        
        .page-break-before {
            page-break-before: always;
        }
        
        .avoid-break {
            page-break-inside: avoid;
        }
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="header">
        <h1>{{ plan.plan_name or ('Kế hoạch du lịch ' + plan.destination) }}</h1>
        <p class="subtitle">{{ plan.destination }}</p>
        <p class="subtitle">{{ plan.duration_days }} ngày {{ plan.duration_days - 1 }} đêm</p>
        {% if start_date_formatted %}
        <p class="subtitle">{{ start_date_formatted }} - {{ end_date_formatted }}</p>
        {% endif %}
    </div>
    
    <!-- Plan Overview -->
    <div class="info-grid">
        <div class="info-row">
            <div class="info-item">
                <div class="info-label">Điểm đến</div>
                <div class="info-value">{{ plan.destination }}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Thời gian</div>
                <div class="info-value">{{ plan.duration_days }} ngày</div>
            </div>
        </div>
        <div class="info-row">
            {% if plan.budget %}
            <div class="info-item">
                <div class="info-label">Ngân sách dự kiến</div>
                <div class="info-value">{{ format_currency(plan.budget, plan.budget_currency) }}</div>
            </div>
            {% endif %}
            <div class="info-item">
                <div class="info-label">Tổng chi phí ước tính</div>
                <div class="info-value">{{ format_currency(costs.total, 'VND') }}</div>
            </div>
        </div>
    </div>
    
    <!-- Itinerary -->
    <h2>Lịch trình chi tiết</h2>
    
    {% for day in itinerary %}
    <div class="day-section">
        <div class="day-header">
            <div class="day-title">Ngày {{ day.day }}: {{ day.title }}</div>
            {% if day.description %}
            <div style="margin-top: 0.2cm; color: #666; font-size: 10pt;">{{ day.description }}</div>
            {% endif %}
        </div>
        
        {% if day.activities %}
        {% for activity in day.activities %}
        <div class="activity">
            {% if activity.time %}
            <div class="activity-time">⏰ {{ activity.time }}</div>
            {% endif %}
            <div class="activity-title">{{ activity.title }}</div>
            {% if activity.description %}
            <div class="activity-description">{{ activity.description }}</div>
            {% endif %}
            {% if activity.location %}
            <div class="activity-location">{{ activity.location }}</div>
            {% endif %}
            {% if activity.cost %}
            <div class="activity-cost">Chi phí: {{ format_currency(activity.cost, 'VND') }}</div>
            {% endif %}
        </div>
        {% endfor %}
        {% endif %}
        
        {% if day.notes and day.notes|length > 0 %}
        <div class="notes-box">
            <div class="notes-title">Lưu ý quan trọng</div>
            <ul>
            {% for note in day.notes %}
                <li>{{ note }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
    {% endfor %}
    
    <!-- Hotel Information -->
    {% if hotel %}
    <div class="page-break-before"></div>
    <h2>Thông tin khách sạn</h2>
    <div class="hotel-card">
        <div class="hotel-name">{{ hotel.hotel_name }}</div>
        {% if hotel.star_rating %}
        <div class="hotel-rating">
            {% for i in range(hotel.star_rating) %}⭐{% endfor %}
        </div>
        {% endif %}
        <div class="hotel-details">
            {% if hotel.address %}
            <div style="margin-top: 0.2cm;">📍 {{ hotel.address }}</div>
            {% endif %}
            <div style="margin-top: 0.2cm;">📅 Nhận phòng: {{ hotel.checkin_date }}</div>
            <div>📅 Trả phòng: {{ hotel.checkout_date }}</div>
            <div>🛏️ {{ hotel.nights }} đêm • {{ hotel.rooms }} phòng • {{ hotel.guests }} khách</div>
            {% if hotel.guest_rating %}
            <div style="margin-top: 0.2cm;">⭐ Đánh giá: {{ hotel.guest_rating }}/10 ({{ hotel.review_count }} đánh giá)</div>
            {% endif %}
        </div>
        <div class="price-box">
            <div class="price-label">Tổng chi phí khách sạn</div>
            <div class="price-value">{{ format_currency(hotel.total_price, hotel.currency) }}</div>
        </div>
    </div>
    {% endif %}
    
    <!-- Flight Information -->
    {% if flights and flights|length > 0 %}
    <h2>Thông tin chuyến bay</h2>
    {% for flight in flights %}
    <div class="flight-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="flight-carrier">{{ flight.carrier_name }}</div>
            <div style="color: #666; font-size: 10pt;">{{ flight.flight_number }}</div>
        </div>
        <div style="margin-top: 0.3cm; padding: 0.3cm; background: white; border-radius: 4px;">
            <div style="font-weight: bold;">
                {% if flight.flight_type == 'outbound' %}✈️ Chuyến đi{% else %}🔙 Chuyến về{% endif %}
            </div>
            <div style="margin-top: 0.2cm; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: bold; font-size: 12pt;">{{ flight.origin_code }}</div>
                    <div style="color: #666; font-size: 9pt;">{{ flight.departure_time }}</div>
                </div>
                <div style="text-align: center; color: #666; font-size: 9pt;">
                    <div>{{ flight.duration }} phút</div>
                    <div style="margin: 0.1cm 0;">―――――✈―――――</div>
                    <div>{% if flight.stops == 0 %}Bay thẳng{% else %}{{ flight.stops }} điểm dừng{% endif %}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight: bold; font-size: 12pt;">{{ flight.destination_code }}</div>
                    <div style="color: #666; font-size: 9pt;">{{ flight.arrival_time }}</div>
                </div>
            </div>
        </div>
        <div class="flight-details">
            <div>👥 {{ flight.adults }} người lớn{% if flight.children > 0 %} • {{ flight.children }} trẻ em{% endif %}</div>
            <div>💺 Hạng: {{ flight.cabin_class }}</div>
        </div>
        <div class="price-box">
            <div class="price-label">Giá vé</div>
            <div class="price-value">{{ format_currency(flight.price, flight.currency) }}</div>
        </div>
    </div>
    {% endfor %}
    {% endif %}
    
    <!-- Cost Summary -->
    <div class="page-break-before"></div>
    <h2>Tổng kết chi phí</h2>
    <div class="cost-summary">
        <div class="cost-row">
            <span>Hoạt động & Tham quan</span>
            <span>{{ format_currency(costs.activities, 'VND') }}</span>
        </div>
        {% if hotel %}
        <div class="cost-row">
            <span>Khách sạn ({{ hotel.nights }} đêm)</span>
            <span>{{ format_currency(costs.hotel, 'VND') }}</span>
        </div>
        {% endif %}
        {% if flights and flights|length > 0 %}
        <div class="cost-row">
            <span>Chuyến bay ({{ flights|length }} chuyến)</span>
            <span>{{ format_currency(costs.flights, 'VND') }}</span>
        </div>
        {% endif %}
        <div class="cost-total">
            <div style="display: flex; justify-content: space-between;">
                <span>TỔNG CỘNG</span>
                <span>{{ format_currency(costs.total, 'VND') }}</span>
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <div class="footer">
        <p>Tài liệu được tạo tự động bởi khampha.online</p>
        <p>Ngày tạo: {{ generated_at }}</p>
        <p style="margin-top: 0.3cm; color: #666;">
            🌏 Chúc bạn có một chuyến đi vui vẻ và an toàn!
        </p>
    </div>
</body>
</html>
"""
