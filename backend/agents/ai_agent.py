"""
Main AI Agent using Google Gemini
Handles conversation and travel planning
"""
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from .prompts import (
    SYSTEM_PROMPT,
    REQUIREMENTS_PROMPT,
    ITINERARY_PROMPT,
    get_response_template,
    format_missing_fields,
    create_search_queries
)
from .search_tool import SearchTool

logger = logging.getLogger(__name__)


class TravelAgent:
    """AI Travel Planning Agent using Gemini"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp",
                 temperature: float = 0.7, max_tokens: int = 2048):
        """
        Initialize Travel Agent
        
        Args:
            api_key: Gemini API key
            model_name: Gemini model name
            temperature: Generation temperature
            max_tokens: Maximum tokens
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize Gemini
        if genai:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    'temperature': temperature,
                    'max_output_tokens': max_tokens,
                }
            )
        else:
            logger.warning("google-generativeai not installed, using mock mode")
            self.model = None
        
        # Initialize search tool
        self.search = SearchTool(max_results=5)
        
        # Conversation state
        self.conversation_history = []
    
    def chat(self, user_message: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        Main chat method
        
        Args:
            user_message: User's message
            conversation_history: Previous conversation
            
        Returns:
            Response dict with message, has_plan, plan_data
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"💬 NEW CHAT REQUEST")
        logger.info(f"User message: '{user_message}'")
        logger.info(f"History length: {len(conversation_history) if conversation_history else 0}")
        logger.info(f"{'='*80}\n")
        
        try:
            # Update conversation history
            if conversation_history:
                self.conversation_history = conversation_history
                logger.info(f"📚 Updated conversation history ({len(conversation_history)} messages)")
            
            # Analyze user intent and extract requirements
            logger.info("🔍 Step 1: Extracting requirements...")
            requirements = self._extract_requirements(user_message)
            logger.info(f"✅ Requirements extracted: {requirements}")
            
            # Check if we have enough info to create plan
            if requirements['ready_to_plan']:
                logger.info("✅ Ready to plan! Proceeding with itinerary generation...")
                
                # Search for information
                logger.info(f"🔍 Step 2: Searching for destination '{requirements['destination']}'...")
                try:
                    search_results = self._search_for_destination(
                        requirements['destination'],
                        requirements.get('preferences')
                    )
                    logger.info(f"✅ Search completed. Results length: {len(search_results)} chars")
                except Exception as search_error:
                    logger.error(f"❌ Search failed: {type(search_error).__name__}: {str(search_error)}")
                    search_results = "Không tìm thấy thông tin tìm kiếm."
                
                # Generate itinerary
                logger.info("📋 Step 3: Generating itinerary...")
                try:
                    plan_data = self._generate_itinerary(requirements, search_results)
                    logger.info(f"✅ Itinerary generated successfully")
                    logger.info(f"   - Destination: {plan_data.get('destination')}")
                    logger.info(f"   - Days: {plan_data.get('duration_days')}")
                    logger.info(f"   - Activities: {len(plan_data.get('itinerary', []))} days")
                except Exception as itinerary_error:
                    logger.error(f"❌ Itinerary generation failed: {type(itinerary_error).__name__}: {str(itinerary_error)}")
                    import traceback
                    logger.error(f"Traceback:\n{traceback.format_exc()}")
                    raise
                
                # Format response
                response_text = get_response_template(
                    'plan_ready',
                    duration_days=requirements['duration_days'],
                    total_cost=self._format_currency(plan_data.get('total_cost', 0))
                )
                
                return {
                    'success': True,
                    'message': response_text,
                    'has_plan': True,
                    'plan_data': plan_data,
                    'requirements': requirements
                }
            
            else:
                # Ask for missing information
                logger.info("⚠️ Not ready to plan yet. Missing information.")
                missing = requirements.get('missing_fields', [])
                logger.info(f"   Missing fields: {missing}")
                response_text = get_response_template(
                    'missing_info',
                    missing_fields=format_missing_fields(missing)
                )
                logger.info(f"💬 Response prepared: Asking for missing info")
                
                return {
                    'success': True,
                    'message': response_text,
                    'has_plan': False,
                    'requirements': requirements
                }
        
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return {
                'success': False,
                'message': get_response_template('error', error=str(e)),
                'has_plan': False
            }
    
    def _extract_requirements(self, user_message: str) -> Dict:
        """Extract travel requirements from user message"""
        
        # Format conversation history
        history_text = "\n".join([
            f"User: {msg['user']}\nBot: {msg['bot']}"
            for msg in self.conversation_history[-3:]  # Last 3 exchanges
        ])
        
        # Create prompt
        prompt = REQUIREMENTS_PROMPT.format(
            user_message=user_message,
            conversation_history=history_text or "Chưa có"
        )
        
        try:
            if self.model:
                # Use Gemini to extract requirements
                response = self.model.generate_content(prompt)
                analysis = response.text
                
                # Parse the analysis (simplified)
                requirements = self._parse_requirements_response(analysis, user_message)
            else:
                # Fallback: simple keyword matching
                requirements = self._simple_extract_requirements(user_message)
            
            return requirements
            
        except Exception as e:
            logger.error(f"Requirements extraction error: {str(e)}")
            return self._simple_extract_requirements(user_message)
    
    def _simple_extract_requirements(self, text: str) -> Dict:
        """Simple keyword-based requirement extraction"""
        text_lower = text.lower()
        
        # Common Vietnamese destinations
        destinations = ['đà lạt', 'nha trang', 'phú quốc', 'đà nẵng', 'hội an', 
                       'sapa', 'hạ long', 'vũng tàu', 'hà nội', 'sài gòn', 'huế']
        
        destination = None
        for dest in destinations:
            if dest in text_lower:
                destination = dest.title()
                break
        
        # Extract days
        duration_days = None
        for word in text.split():
            if word.isdigit() and int(word) <= 30:
                duration_days = int(word)
                break
        
        # Extract budget (millions)
        budget = None
        if 'triệu' in text_lower or 'tr' in text_lower:
            for i, word in enumerate(text.split()):
                if word.replace(',', '').replace('.', '').isdigit():
                    budget = float(word.replace(',', '')) * 1000000
                    break
        
        # Extract preferences
        preferences = []
        pref_keywords = {
            'biển': 'tắm biển', 'ẩm thực': 'ẩm thực', 'núi': 'leo núi',
            'văn hóa': 'văn hóa', 'lịch sử': 'lịch sử', 'thiên nhiên': 'thiên nhiên'
        }
        for keyword, pref in pref_keywords.items():
            if keyword in text_lower:
                preferences.append(pref)
        
        # Check if ready
        ready = destination is not None and duration_days is not None
        
        missing = []
        if not destination:
            missing.append('destination')
        if not duration_days:
            missing.append('duration_days')
        if not budget:
            missing.append('budget')
        if not preferences:
            missing.append('preferences')
        
        return {
            'destination': destination,
            'duration_days': duration_days,
            'budget': budget,
            'preferences': ', '.join(preferences) if preferences else None,
            'ready_to_plan': ready,
            'missing_fields': missing
        }
    
    def _parse_requirements_response(self, analysis: str, original_text: str) -> Dict:
        """Parse Gemini's requirements analysis"""
        # Try to extract from structured response
        # Fallback to simple extraction if parsing fails
        try:
            # Look for patterns in the response
            lines = analysis.split('\n')
            requirements = {}
            
            for line in lines:
                if 'điểm đến:' in line.lower():
                    dest = line.split(':')[1].strip()
                    if 'chưa rõ' not in dest.lower():
                        requirements['destination'] = dest
                
                elif 'số ngày:' in line.lower():
                    days = line.split(':')[1].strip()
                    if days.isdigit():
                        requirements['duration_days'] = int(days)
                
                elif 'ngân sách:' in line.lower():
                    budget = line.split(':')[1].strip()
                    # Extract numbers
                    numbers = ''.join([c for c in budget if c.isdigit() or c == '.'])
                    if numbers:
                        requirements['budget'] = float(numbers)
                
                elif 'sở thích:' in line.lower():
                    prefs = line.split(':')[1].strip()
                    if 'chưa rõ' not in prefs.lower():
                        requirements['preferences'] = prefs
            
            # Use simple extraction as fallback
            simple = self._simple_extract_requirements(original_text)
            for key, value in simple.items():
                if key not in requirements and value:
                    requirements[key] = value
            
            # Check readiness
            requirements['ready_to_plan'] = (
                'destination' in requirements and 
                'duration_days' in requirements
            )
            
            # Determine missing fields
            required_fields = ['destination', 'duration_days', 'budget', 'preferences']
            requirements['missing_fields'] = [
                field for field in required_fields 
                if field not in requirements or not requirements[field]
            ]
            
            return requirements
            
        except Exception as e:
            logger.error(f"Parse error: {str(e)}")
            return self._simple_extract_requirements(original_text)
    
    def _search_for_destination(self, destination: str, preferences: Optional[str] = None) -> str:
        """Search for destination information"""
        logger.info(f"   🔍 Searching for: {destination}")
        logger.info(f"   🎯 Preferences: {preferences}")
        
        # Create search queries
        queries = create_search_queries(destination, preferences)
        logger.info(f"   📖 Generated {len(queries)} search queries:")
        for i, q in enumerate(queries, 1):
            logger.info(f"      {i}. {q}")
        
        # Perform searches
        all_results = []
        for i, query in enumerate(queries[:3], 1):  # Top 3 queries
            logger.info(f"   🔍 Query {i}/3: '{query}'")
            try:
                results = self.search.search(query, max_results=2)
                logger.info(f"      ✅ Got {len(results)} results")
                all_results.extend(results)
            except Exception as e:
                logger.error(f"      ❌ Query failed: {str(e)}")
        
        logger.info(f"   📊 Total results collected: {len(all_results)}")
        
        # Format for LLM
        formatted = self.search.format_results_for_llm(all_results)
        logger.info(f"   📝 Formatted results: {len(formatted)} chars")
        return formatted
    
    def _generate_itinerary(self, requirements: Dict, search_results: str) -> Dict:
        """Generate detailed itinerary"""
        
        # Create prompt
        prompt = ITINERARY_PROMPT.format(
            destination=requirements.get('destination', 'Việt Nam'),
            duration_days=requirements.get('duration_days', 3),
            budget=self._format_currency(requirements.get('budget', 5000000)),
            preferences=requirements.get('preferences', 'khám phá, ẩm thực'),
            search_results=search_results
        )
        
        try:
            if self.model:
                # Use Gemini to generate itinerary
                response = self.model.generate_content(prompt)
                itinerary_text = response.text
                
                # Parse the response into structured data
                plan_data = self._parse_itinerary(itinerary_text, requirements)
            else:
                # Mock itinerary
                plan_data = self._create_mock_itinerary(requirements)
            
            return plan_data
            
        except Exception as e:
            logger.error(f"Itinerary generation error: {str(e)}")
            return self._create_mock_itinerary(requirements)
    
    def _parse_itinerary(self, text: str, requirements: Dict) -> Dict:
        """Parse Gemini's itinerary response"""
        logger.info(f"   📝 Parsing itinerary text ({len(text)} chars)...")
        logger.debug(f"   Text preview: {text[:200]}...")
        
        # Try to extract JSON structure
        # Fallback to creating structured plan from text
        
        plan_data = {
            'plan_name': f"Khám phá {requirements.get('destination', 'Việt Nam')}",
            'destination': requirements.get('destination', 'Việt Nam'),
            'duration_days': requirements.get('duration_days', 3),
            'budget': requirements.get('budget'),
            'preferences': requirements.get('preferences'),
            'itinerary': [],
            'cost_breakdown': {},
            'total_cost': requirements.get('budget', 0),
            'notes': []
        }
        
        # Parse daily activities from text
        # This is simplified - in production would use better parsing
        days = []
        current_day = None
        
        logger.info("   🔍 Parsing lines for daily activities...")
        for line_num, line in enumerate(text.split('\n'), 1):
            if 'ngày' in line.lower() and ':' in line:
                if current_day:
                    logger.info(f"      ✅ Day {current_day['day']} completed with {len(current_day['activities'])} activities")
                    days.append(current_day)
                current_day = {
                    'day': len(days) + 1,
                    'title': line.strip(),
                    'activities': []
                }
                logger.info(f"      📅 Started Day {current_day['day']}: {line.strip()[:50]}...")
            elif current_day and line.strip() and any(c.isdigit() for c in line[:10]) and ':' in line[:10]:
                # Activity line with time
                try:
                    time_part = line[:5].strip()
                    desc_part = line[5:].strip() if len(line) > 5 else line.strip()
                    current_day['activities'].append({
                        'time': time_part,
                        'title': desc_part[:50],
                        'description': desc_part
                    })
                    logger.debug(f"         + Activity: {time_part} - {desc_part[:30]}...")
                except Exception as e:
                    logger.warning(f"         ⚠️ Failed to parse activity line {line_num}: {str(e)}")
        
        if current_day:
            logger.info(f"      ✅ Day {current_day['day']} completed with {len(current_day['activities'])} activities")
            days.append(current_day)
        
        logger.info(f"   📊 Parsed {len(days)} days from text")
        
        # Use parsed days or fallback to mock
        if days and len(days) > 0:
            plan_data['itinerary'] = days
            logger.info(f"   ✅ Using parsed itinerary with {len(days)} days")
        else:
            logger.warning(f"   ⚠️ No days parsed from text, using mock itinerary")
            mock_plan = self._create_mock_itinerary(requirements)
            plan_data['itinerary'] = mock_plan.get('itinerary', [])
            logger.info(f"   🎭 Mock itinerary created with {len(plan_data['itinerary'])} days")
        
        return plan_data
    
    def _create_mock_itinerary(self, requirements: Dict) -> Dict:
        """Create detailed mock itinerary with specific addresses and prices"""
        destination = requirements.get('destination', 'Đà Lạt')
        days = requirements.get('duration_days', 3)
        budget = requirements.get('budget', 5000000)
        
        # Detailed mock data for Đà Lạt (can be expanded for other destinations)
        itinerary = []
        
        if days >= 1:
            itinerary.append({
                'day': 1,
                'title': f'Ngày 1: Khám phá trung tâm {destination}',
                'activities': [
                    {
                        'time': '07:00',
                        'type': 'breakfast',
                        'title': 'Ăn sáng tại Quán Bánh Mì Phượng',
                        'restaurant_name': 'Bánh Mì Phượng',
                        'address': '25 Bùi Thị Xuân, Phường 2, TP. Đà Lạt',
                        'dishes': ['Bánh mì thịt nướng: 25.000đ', 'Sữa đậu nành: 10.000đ'],
                        'description': 'Quán bánh mì nổi tiếng với nhân thịt nướng đậm đà, rau thơm tươi',
                        'cost': 35000,
                        'duration': '30 phút',
                        'notes': 'Nên đến sớm trước 8h để tránh đông, bánh mì thịt nướng đặc biệt rất ngon'
                    },
                    {
                        'time': '08:00',
                        'type': 'sightseeing',
                        'title': 'Tham quan Hồ Xuân Hương',
                        'place_name': 'Hồ Xuân Hương',
                        'address': 'Trung tâm TP. Đà Lạt, Lâm Đồng',
                        'activities': ['Đi bộ quanh hồ', 'Chụp ảnh', 'Thuê thuyền thiên nga'],
                        'description': 'Hồ nước ngọt nằm ở trung tâm thành phố, có chu vi 7km, cảnh đẹp thơ mộng',
                        'entrance_fee': 0,
                        'other_costs': 'Thuê thuyền thiên nga: 50.000đ/30 phút, Gửi xe: 5.000đ',
                        'cost': 55000,
                        'duration': '1.5 giờ',
                        'transportation': 'Đi bộ 10 phút từ quán ăn sáng',
                        'notes': 'Mở cửa cả ngày, nên đi sáng sớm để không nắng, view đẹp nhất ở góc Đồi Cù'
                    },
                    {
                        'time': '10:00',
                        'type': 'sightseeing',
                        'title': 'Chợ Đà Lạt',
                        'place_name': 'Chợ Đà Lạt',
                        'address': 'Nguyễn Thị Minh Khai, Phường 1, TP. Đà Lạt',
                        'activities': ['Mua hoa tươi', 'Thử ẩm thực địa phương', 'Mua đặc sản'],
                        'description': 'Chợ trung tâm 3 tầng, đầy đủ hoa tươi, thực phẩm, quần áo, đặc sản',
                        'entrance_fee': 0,
                        'other_costs': 'Hoa tươi: 50.000đ/bó, Dâu tây: 100.000đ/kg',
                        'cost': 150000,
                        'duration': '1 giờ',
                        'transportation': 'Đi bộ 5 phút từ Hồ Xuân Hương',
                        'notes': 'Mở cửa từ 6h sáng, cần mặc cả khi mua, tầng 1 có nhiều quán ăn vặt ngon'
                    },
                    {
                        'time': '12:00',
                        'type': 'lunch',
                        'title': 'Ăn trưa tại Lẩu Dê Lạng Sơn',
                        'restaurant_name': 'Lẩu Dê Lạng Sơn',
                        'address': '123 Phan Đình Phùng, Phường 2, TP. Đà Lạt',
                        'dishes': ['Lẩu dê: 250.000đ/kg', 'Rau các loại: 50.000đ', 'Nước ngọt: 15.000đ'],
                        'description': 'Nhà hàng chuyên lẩu dê, thịt dê tươi mỗi ngày, nước lẩu đậm đà',
                        'cost': 200000,
                        'duration': '1 giờ',
                        'notes': 'Nên gọi 1kg dê cho 2-3 người, nhớ gọi thêm bánh tráng nướng'
                    },
                    {
                        'time': '14:00',
                        'type': 'sightseeing',
                        'title': 'Tham quan Ga Đà Lạt',
                        'place_name': 'Ga Đà Lạt (Cremaillere Railway)',
                        'address': '1 Quang Trung, Phường 10, TP. Đà Lạt',
                        'activities': ['Chụp ảnh ga cổ', 'Ngắm tàu hỏa cổ', 'Đi tàu đến Trại Mát'],
                        'description': 'Nhà ga xe lửa cổ kiến trúc Pháp, còn duy trì tuyến đường ray răng cưa',
                        'entrance_fee': 5000,
                        'other_costs': 'Vé tàu khứ hồi đến Trại Mát: 120.000đ/người',
                        'cost': 125000,
                        'duration': '2 giờ (bao gồm đi tàu)',
                        'transportation': 'Taxi từ nhà hàng 10 phút, ~40.000đ',
                        'notes': 'Tàu chạy 7h45, 9h50, 11h55, 14h, 16h05. Nên mua vé trước 30 phút'
                    },
                    {
                        'time': '16:30',
                        'type': 'cafe',
                        'title': 'Thư giãn tại Mê Linh Coffee Garden',
                        'restaurant_name': 'Mê Linh Coffee Garden',
                        'address': '1A Đống Đa, Phường 2, TP. Đà Lạt',
                        'dishes': ['Cà phê sữa đá: 30.000đ', 'Sinh tố dâu: 35.000đ', 'Bánh su kem: 25.000đ'],
                        'description': 'Quán cafe view vườn hoa, không gian yên tĩnh, view núi đồi đẹp',
                        'cost': 90000,
                        'duration': '1 giờ',
                        'notes': 'Nên ngồi ngoài vườn để ngắm cảnh, wifi mạnh, phù hợp làm việc'
                    },
                    {
                        'time': '18:30',
                        'type': 'dinner',
                        'title': 'Ăn tối tại Lẩu Bò Hà Tiên',
                        'restaurant_name': 'Lẩu Bò Hà Tiên',
                        'address': '89 Nguyễn Thị Minh Khai, Phường 1, TP. Đà Lạt',
                        'dishes': ['Lẩu bò nhúng dấm: 280.000đ', 'Bò nướng lá lốt: 120.000đ', 'Bia: 25.000đ'],
                        'description': 'Lẩu bò nhúng dấm đặc sản, thịt bò tươi ngon, nước lẩu chua cay hấp dẫn',
                        'cost': 250000,
                        'duration': '1.5 giờ',
                        'notes': 'Đặt chỗ trước vì quán rất đông buổi tối, nên gọi set 2-3 người 400.000đ'
                    },
                    {
                        'time': '20:30',
                        'type': 'entertainment',
                        'title': 'Dạo chợ đêm Đà Lạt',
                        'place_name': 'Chợ đêm Đà Lạt',
                        'address': 'Nguyễn Thị Minh Khai, Phường 1 (quanh khu vực chợ)',
                        'activities': ['Mua quà lưu niệm', 'Ăn vặt', 'Thử đồ giữ ấm'],
                        'description': 'Chợ đêm với nhiều món ăn vặt, quần áo len, đồ lưu niệm, rất nhộn nhịp',
                        'entrance_fee': 0,
                        'other_costs': 'Ăn vặt, mua sắm tùy ý: 100.000đ - 300.000đ',
                        'cost': 100000,
                        'duration': '1 giờ',
                        'transportation': 'Đi bộ từ nhà hàng',
                        'notes': 'Mở từ 19h-23h, nên mặc cả giá, thử bánh tráng nướng và sữa đậu nành nóng'
                    }
                ]
            })
        
        if days >= 2:
            itinerary.append({
                'day': 2,
                'title': f'Ngày 2: Khám phá ngoại thành {destination}',
                'activities': [
                    {
                        'time': '07:00',
                        'type': 'breakfast',
                        'title': 'Ăn sáng tại Bánh Canh Bà Già',
                        'restaurant_name': 'Bánh Canh Bà Già',
                        'address': '77 Yersin, Phường 10, TP. Đà Lạt',
                        'dishes': ['Bánh canh cua: 40.000đ', 'Nem nướng: 5.000đ/xiên', 'Trà đá: 5.000đ'],
                        'description': 'Quán bánh canh cua nổi tiếng, nước dùng đậm đà, topping nhiều',
                        'cost': 50000,
                        'duration': '30 phút',
                        'notes': 'Quán mở từ 6h sáng, hết sớm nên nên đến trước 9h'
                    },
                    {
                        'time': '08:00',
                        'type': 'sightseeing',
                        'title': 'Chinh phục Đỉnh Langbiang',
                        'place_name': 'Đỉnh Langbiang',
                        'address': 'Xã Lạc Dương, cách trung tâm Đà Lạt 12km',
                        'activities': ['Leo núi', 'Ngắm toàn cảnh Đà Lạt', 'Chụp ảnh đỉnh núi'],
                        'description': 'Ngọn núi cao nhất Đà Lạt (2.169m), view 360 độ tuyệt đẹp, có cả đường jeep',
                        'entrance_fee': 50000,
                        'other_costs': 'Thuê jeep lên đỉnh: 200.000đ/xe (4-5 người), Leo bộ: 0đ',
                        'cost': 90000,
                        'duration': '3 giờ',
                        'transportation': 'Thuê xe máy cả ngày: 100.000đ hoặc Grab: 80.000đ',
                        'notes': 'Mở cửa 6h-17h, nên đi sáng sớm để tránh nắng, mang áo ấm và nước'
                    },
                    {
                        'time': '12:00',
                        'type': 'lunch',
                        'title': 'Ăn trưa tại Nhà hàng Âm Phủ',
                        'restaurant_name': 'Nhà hàng Âm Phủ',
                        'address': 'Trại Mát, Phường 4, TP. Đà Lạt',
                        'dishes': ['Lẩu cá tầm: 350.000đ/kg', 'Cá tầm nướng: 150.000đ', 'Rau rừng: 30.000đ'],
                        'description': 'Nhà hàng chuyên cá tầm, không gian độc đáo theo phong cách âm phủ',
                        'cost': 250000,
                        'duration': '1 giờ',
                        'notes': 'Cá tầm tươi sống, 1kg đủ 3-4 người ăn, nhớ thử rượu sim'
                    },
                    {
                        'time': '14:00',
                        'type': 'sightseeing',
                        'title': 'Thác Datanla',
                        'place_name': 'Thác Datanla',
                        'address': 'Đèo Prenn, Phường 3, TP. Đà Lạt (cách trung tâm 7km)',
                        'activities': ['Ngắm thác nước', 'Trải nghiệm xe trượt Alpine Coaster', 'Chụp ảnh'],
                        'description': 'Thác nước đẹp với xe trượt gần 1km, mạo hiểm và thú vị',
                        'entrance_fee': 30000,
                        'other_costs': 'Xe trượt 1 chiều: 50.000đ, Khứ hồi: 80.000đ',
                        'cost': 110000,
                        'duration': '2 giờ',
                        'transportation': 'Xe máy 15 phút từ nhà hàng',
                        'notes': 'Mở cửa 7h-17h, xe trượt rất vui, nên mua vé khứ hồi'
                    },
                    {
                        'time': '16:30',
                        'type': 'cafe',
                        'title': 'Cafe tại The Married Beans',
                        'restaurant_name': 'The Married Beans Coffee',
                        'address': '180 Nguyễn Văn Trỗi, Phường 4, TP. Đà Lạt',
                        'dishes': ['Espresso: 35.000đ', 'Cappuccino: 45.000đ', 'Tiramisu: 40.000đ'],
                        'description': 'Quán cafe phong cách châu Âu, hạt cà phê nguyên chất, không gian ấm cúng',
                        'cost': 120000,
                        'duration': '1 giờ',
                        'notes': 'Wifi tốt, yên tĩnh, phù hợp đọc sách hoặc làm việc'
                    },
                    {
                        'time': '18:30',
                        'type': 'dinner',
                        'title': 'Ăn tối tại Nhà hàng Thảo Nguyên',
                        'restaurant_name': 'Nhà hàng Thảo Nguyên',
                        'address': '145 Phan Đình Phùng, Phường 1, TP. Đà Lạt',
                        'dishes': ['Bò tơ nướng tảng: 180.000đ', 'Gà đồi Đà Lạt: 150.000đ', 'Rau rừng: 40.000đ'],
                        'description': 'Nhà hàng chuyên món nướng, thực đơn phong phú, không gian rộng rãi',
                        'cost': 300000,
                        'duration': '1.5 giờ',
                        'notes': 'Đặt chỗ trước, bò nướng tảng là món đặc sản nên thử'
                    }
                ]
            })
        
        if days >= 3:
            itinerary.append({
                'day': 3,
                'title': f'Ngày 3: Mua sắm và trở về',
                'activities': [
                    {
                        'time': '07:00',
                        'type': 'breakfast',
                        'title': 'Ăn sáng tại Phở Hòa',
                        'restaurant_name': 'Quán Phở Hòa',
                        'address': '256 Phan Đình Phùng, Phường 2, TP. Đà Lạt',
                        'dishes': ['Phở bò tái: 45.000đ', 'Phở gà: 40.000đ', 'Nước ngọt: 10.000đ'],
                        'description': 'Phở nước dùng trong, thịt mềm, bánh phở dai ngon',
                        'cost': 55000,
                        'duration': '30 phút',
                        'notes': 'Quán sạch sẽ, phục vụ nhanh, nên thử phở tái'
                    },
                    {
                        'time': '08:00',
                        'type': 'shopping',
                        'title': 'Mua đặc sản tại Cửa hàng Đặc Sản Đà Lạt 247',
                        'place_name': 'Cửa hàng Đặc Sản Đà Lạt 247',
                        'address': '247 Phan Đình Phùng, Phường 2, TP. Đà Lạt',
                        'activities': ['Mua mứt dâu tây', 'Mua rượu sim', 'Mua atiso đà lạt'],
                        'description': 'Cửa hàng đặc sản uy tín, đầy đủ các loại đặc sản Đà Lạt',
                        'entrance_fee': 0,
                        'other_costs': 'Mứt: 50-100.000đ/hộp, Rượu sim: 120.000đ/chai, Atiso: 150.000đ/hộp',
                        'cost': 300000,
                        'duration': '1 giờ',
                        'transportation': 'Đi bộ từ quán phở',
                        'notes': 'Có niêm yết giá rõ ràng, hàng chất lượng tốt, ship về tận nhà'
                    },
                    {
                        'time': '09:30',
                        'type': 'sightseeing',
                        'title': 'Vườn hoa thành phố',
                        'place_name': 'Vườn Hoa Đà Lạt',
                        'address': '2 Phù Đổng Thiên Vương, Phường 8, TP. Đà Lạt',
                        'activities': ['Ngắm hoa', 'Chụp ảnh', 'Mua hoa tươi mang về'],
                        'description': 'Vườn hoa lớn với hàng trăm loại hoa, có nhà kính hoa lan, hoa hồng',
                        'entrance_fee': 50000,
                        'other_costs': 'Mua hoa tươi: 100-300.000đ',
                        'cost': 150000,
                        'duration': '1.5 giờ',
                        'transportation': 'Taxi 10 phút, ~35.000đ',
                        'notes': 'Mở cửa 7h-18h, sáng sớm hoa đẹp nhất, có nhiều góc check-in đẹp'
                    },
                    {
                        'time': '11:30',
                        'type': 'lunch',
                        'title': 'Ăn trưa tại Nem Nướng Nguyệt',
                        'restaurant_name': 'Nem Nướng Nguyệt',
                        'address': '58 Hồ Tùng Mậu, Phường 3, TP. Đà Lạt',
                        'dishes': ['Nem nướng: 150.000đ/phần', 'Bánh hỏi: 30.000đ', 'Nước mía: 10.000đ'],
                        'description': 'Nem nướng thơm ngon, ăn kèm bánh tráng rau sống rất hấp dẫn',
                        'cost': 120000,
                        'duration': '1 giờ',
                        'notes': 'Quán nhỏ nhưng rất nổi tiếng, nên đến trước 12h'
                    },
                    {
                        'time': '13:00',
                        'type': 'checkout',
                        'title': 'Trả phòng và chuẩn bị về',
                        'description': 'Check out khách sạn, thu xếp hành lý, kiểm tra đồ đạc',
                        'cost': 0,
                        'duration': '30 phút',
                        'notes': 'Nhớ kiểm tra phòng trước khi trả, giữ hóa đơn nếu cần'
                    }
                ]
            })
        
        return {
            'plan_name': f'Khám phá {destination} {days} ngày chi tiết',
            'destination': destination,
            'duration_days': days,
            'budget': budget,
            'preferences': requirements.get('preferences', 'khám phá, ẩm thực, thiên nhiên'),
            'itinerary': itinerary,
            'cost_breakdown': {
                'accommodation': {
                    'amount': budget * 0.30,
                    'description': 'Khách sạn 3 sao trung tâm, 2 đêm'
                },
                'food': {
                    'amount': budget * 0.30,
                    'description': 'Ăn uống đầy đủ 3 bữa/ngày'
                },
                'transportation': {
                    'amount': budget * 0.20,
                    'description': 'Vé xe + thuê xe máy + di chuyển nội thành'
                },
                'activities': {
                    'amount': budget * 0.15,
                    'description': 'Vé tham quan các điểm du lịch'
                },
                'shopping': {
                    'amount': budget * 0.05,
                    'description': 'Mua đặc sản, quà lưu niệm'
                }
            },
            'total_cost': budget,
            'notes': [
                '🌡️ Thời tiết Đà Lạt mát mẻ quanh năm 15-25°C, nên mang áo ấm',
                '🚗 Nên thuê xe máy để di chuyển linh hoạt (100-150k/ngày)',
                '📱 Số điện thoại khẩn cấp: 113 (Cảnh sát), 114 (Cứu hỏa), 115 (Cấp cứu)',
                '💡 Tips: Đặt khách sạn trước, mặc cả khi mua đặc sản, tránh mua ở khu du lịch',
                '🍓 Đặc sản nên mua: Mứt dâu, Rượu sim, Atiso, Khoai mật, Bơ Đà Lạt'
            ]
        }
    
    @staticmethod
    def _format_currency(amount: float) -> str:
        """Format currency to Vietnamese style"""
        if amount >= 1000000:
            return f"{amount/1000000:.1f} triệu VNĐ"
        else:
            return f"{int(amount):,} VNĐ".replace(',', '.')


# Example usage
if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv('GEMINI_API_KEY', 'mock-key')
    agent = TravelAgent(api_key)
    
    # Test conversation
    response = agent.chat("Tôi muốn đi Đà Lạt 3 ngày, ngân sách 5 triệu")
    print(json.dumps(response, indent=2, ensure_ascii=False))
