"""
Main AI Agent using Google Gemini
Handles conversation and travel planning
"""
import json
import logging
import time
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
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-lite",
                 temperature: float = 0.7, max_tokens: int = 10000):
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
            # Set request timeout (in seconds)
            self.request_timeout = 10000
            self.use_gemini = True
        else:
            logger.warning("google-generativeai not installed, using mock mode")
            self.model = None
            self.use_gemini = False
        
        # Initialize search tool
        self.search = SearchTool(max_results=5)
        
        # Conversation state
        self.conversation_history = []
    
    def chat(self, user_message: str, conversation_history: Optional[List[Dict]] = None, current_plan: Optional[Dict] = None) -> Dict:
        """
        Main chat method with LLM-based intent detection
        
        Args:
            user_message: User's message (can include @plan, @ask, @edit_plan)
            conversation_history: Previous conversation
            current_plan: Current plan data for @edit_plan mode
            
        Returns:
            Response dict with message, has_plan, plan_data, mode
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"💬 NEW CHAT REQUEST")
        logger.info(f"User message: '{user_message}'")
        logger.info(f"History length: {len(conversation_history) if conversation_history else 0}")
        logger.info(f"{'='*80}\n")
        
        # Update conversation history
        if conversation_history:
            self.conversation_history = conversation_history
            logger.info(f"📚 Updated conversation history ({len(conversation_history)} messages)")
        
        # Use LLM to analyze intent and determine mode
        intent_analysis = self._analyze_user_intent(user_message, current_plan)
        logger.info(f"🎯 Intent Analysis:")
        logger.info(f"   Mode: {intent_analysis['mode']}")
        logger.info(f"   Confidence: {intent_analysis.get('confidence', 'N/A')}")
        logger.info(f"   Should respond directly: {intent_analysis.get('direct_response', False)}")
        
        # If LLM suggests direct response, return it immediately
        if intent_analysis.get('direct_response') and intent_analysis.get('response'):
            logger.info(f"💬 Returning direct response from LLM")
            return {
                'success': True,
                'message': intent_analysis['response'],
                'has_plan': False,
                'mode': intent_analysis['mode'],
                'intent_analysis': intent_analysis
            }
        
        # Otherwise, route to appropriate handler based on detected mode
        mode = intent_analysis['mode']
        clean_message = intent_analysis.get('clean_message', user_message)
        
        if mode == 'plan':
            # Pass requirements from intent analysis if available
            requirements = intent_analysis.get('requirements')
            return self._handle_plan_mode(clean_message, requirements=requirements)
        elif mode == 'edit_plan':
            return self._handle_edit_plan_mode(clean_message, current_plan)
        else:  # ask mode
            return self._handle_ask_mode(clean_message)
    
    def _analyze_user_intent(self, message: str, current_plan: Optional[Dict] = None) -> Dict:
        """
        Use LLM to analyze user intent and determine appropriate mode and response
        
        Args:
            message: User's message
            current_plan: Current plan if exists
            
        Returns:
            Dict with:
                - mode: 'plan', 'ask', 'edit_plan', or 'chat'
                - confidence: confidence level (high/medium/low)
                - clean_message: message without mode prefix
                - direct_response: whether to respond directly without further processing
                - response: direct response if applicable
                - reasoning: why this mode was chosen
        """
        # Format conversation history
        history_text = "\n".join([
            f"User: {msg['user']}\nBot: {msg['bot']}"
            for msg in self.conversation_history[-3:]  # Last 3 exchanges
        ]) if self.conversation_history else "Chưa có lịch sử hội thoại"
        
        # Build intent analysis prompt
        intent_prompt = f"""Bạn là trợ lý phân tích ý định người dùng cho hệ thống du lịch thông minh.

Hệ thống có 4 chế độ:
1. **plan** - Tạo kế hoạch du lịch chi tiết (cần: điểm đến, số ngày, ngân sách)
2. **ask** - Trả lời câu hỏi thông tin về địa điểm, giá cả, kinh nghiệm du lịch
3. **edit_plan** - Chỉnh sửa kế hoạch đã có (cần có kế hoạch hiện tại)
4. **chat** - Trò chuyện thông thường, chào hỏi, cảm ơn, không liên quan du lịch

TRẠNG THÁI HIỆN TẠI:
- Có kế hoạch đang mở: {"Có" if current_plan else "Không"}
- Lịch sử hội thoại gần đây:
{history_text}

TIN NHẮN CỦA NGƯỜI DÙNG:
"{message}"

YÊU CẦU:
Phân tích ý định và trả về JSON với cấu trúc:
{{
  "mode": "plan|ask|edit_plan|chat",
  "confidence": "high|medium|low",
  "clean_message": "tin nhắn đã làm sạch (bỏ @plan, @ask...)",
  "direct_response": true/false,
  "response": "câu trả lời trực tiếp nếu direct_response=true",
  "reasoning": "lý do chọn mode này"
}}

QUY TẮC:
1. Nếu có tiền tố @plan/@ask/@edit_plan → dùng mode tương ứng, confidence=high
2. Nếu hỏi về thông tin ("... ở đâu?", "giá bao nhiêu?", "nên đi...") → mode=ask
3. Nếu yêu cầu tạo kế hoạch ("muốn đi", "lên kế hoạch", "tour") → mode=plan
4. Nếu yêu cầu sửa kế hoạch ("thay đổi", "bớt", "thêm", "sửa lại") VÀ có kế hoạch → mode=edit_plan
5. Nếu sửa kế hoạch NHƯNG KHÔNG có kế hoạch → mode=plan, direct_response=true với thông báo lỗi
6. Nếu chào hỏi/cảm ơn đơn giản → mode=chat, direct_response=true
7. Nếu không rõ ràng → confidence=low

**QUAN TRỌNG**: Nếu mode=plan, phải extract thêm:
- requirements: {{
    "destination": "tên điểm đến" hoặc null,
    "duration_days": số ngày (int) hoặc null,
    "budget": ngân sách (số, VD: 5000000) hoặc null,
    "preferences": "sở thích" hoặc null,
    "ready_to_plan": true/false (true CHỈ KHI có đủ: destination, duration_days VÀ budget),
    "missing_fields": ["destination", "duration_days", "budget", "preferences"] - các trường còn thiếu
  }}

VÍ DỤ:
- "Tôi muốn đi Đà Lạt 3 ngày ngân sách 5 triệu" → mode=plan, confidence=high, requirements={{destination:"Đà Lạt", duration_days:3, budget:5000000, preferences:null, ready_to_plan:true, missing_fields:["preferences"]}}
- "Tôi muốn đi Đà Lạt 3 ngày" → mode=plan, confidence=high, requirements={{destination:"Đà Lạt", duration_days:3, budget:null, preferences:null, ready_to_plan:false, missing_fields:["budget","preferences"]}}
- "Hà Nội có gì hay?" → mode=ask, confidence=high
- "Thêm 1 ngày nữa" (có plan) → mode=edit_plan, confidence=high
- "Xin chào" → mode=chat, direct_response=true, response="Xin chào! Tôi là trợ lý du lịch..."
- "Đi du lịch" → mode=plan, confidence=low, requirements={{destination:null, duration_days:null, budget:null, preferences:null, ready_to_plan:false, missing_fields:["destination","duration_days","budget","preferences"]}}

TRẢ VỀ CHỈ JSON, KHÔNG CÓ TEXT KHÁC:"""
        
        try:
            if self.use_gemini and self.model:
                logger.info("🤖 Calling LLM for intent analysis...")
                
                # Retry logic with 15s delay
                max_retries = 3
                retry_delay = 15
                last_error = None
                
                for attempt in range(max_retries):
                    try:
                        response = self.model.generate_content(intent_prompt)
                        response_text = response.text.strip()
                        
                        # Clean markdown code blocks if present
                        if response_text.startswith('```'):
                            response_text = response_text.split('```')[1]
                            if response_text.startswith('json'):
                                response_text = response_text[4:]
                            response_text = response_text.strip()
                        
                        logger.debug(f"LLM Response: {response_text}")
                        
                        # Parse JSON response
                        intent_data = json.loads(response_text)
                        break  # Success, exit retry loop
                        
                    except Exception as e:
                        last_error = e
                        if attempt < max_retries - 1:
                            logger.warning(f"⚠️ Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay}s...")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"❌ All {max_retries} attempts failed")
                            raise last_error
                
                intent_data = intent_data
                
                # Validate and set defaults
                intent_data.setdefault('mode', 'chat')
                intent_data.setdefault('confidence', 'medium')
                intent_data.setdefault('clean_message', message)
                intent_data.setdefault('direct_response', False)
                intent_data.setdefault('reasoning', 'No reasoning provided')
                
                logger.info(f"✅ Intent analysis successful: {intent_data['mode']} ({intent_data['confidence']})")
                return intent_data
                
            else:
                logger.warning("⚠️ Gemini not available, using fallback detection")
                return self._fallback_intent_detection(message, current_plan)
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response was: {response_text[:200]}")
            return self._fallback_intent_detection(message, current_plan)
        except Exception as e:
            logger.error(f"❌ Intent analysis error: {str(e)}")
            return self._fallback_intent_detection(message, current_plan)
    
    def _fallback_intent_detection(self, message: str, current_plan: Optional[Dict] = None) -> Dict:
        """
        Fallback intent detection using simple pattern matching
        """
        message_lower = message.lower().strip()
        
        # Check for explicit mode prefixes
        if message_lower.startswith('@ask'):
            return {
                'mode': 'ask',
                'confidence': 'high',
                'clean_message': message[4:].strip(),
                'direct_response': False,
                'reasoning': 'Explicit @ask prefix'
            }
        elif message_lower.startswith('@edit_plan') or message_lower.startswith('@edit'):
            prefix_len = 10 if '@edit_plan' in message_lower else 5
            if not current_plan:
                return {
                    'mode': 'plan',
                    'confidence': 'high',
                    'clean_message': message[prefix_len:].strip(),
                    'direct_response': True,
                    'response': '⚠️ Bạn chưa có kế hoạch nào để chỉnh sửa. Hãy tạo kế hoạch mới trước nhé!',
                    'reasoning': 'Edit request but no existing plan'
                }
            return {
                'mode': 'edit_plan',
                'confidence': 'high',
                'clean_message': message[prefix_len:].strip(),
                'direct_response': False,
                'reasoning': 'Explicit @edit_plan prefix'
            }
        elif message_lower.startswith('@plan'):
            return {
                'mode': 'plan',
                'confidence': 'high',
                'clean_message': message[5:].strip(),
                'direct_response': False,
                'reasoning': 'Explicit @plan prefix'
            }
        
        # Pattern-based detection
        # Greeting patterns
        greetings = ['xin chào', 'hello', 'hi', 'chào bạn', 'chào bot']
        if any(greeting in message_lower for greeting in greetings):
            return {
                'mode': 'chat',
                'confidence': 'high',
                'clean_message': message,
                'direct_response': True,
                'response': 'Xin chào! 👋 Tôi là trợ lý du lịch ảo của bạn. Tôi có thể giúp bạn:\n\n🗺️ Tạo kế hoạch du lịch chi tiết\n❓ Trả lời câu hỏi về địa điểm\n✏️ Chỉnh sửa kế hoạch của bạn\n\nBạn muốn đi đâu hôm nay?',
                'reasoning': 'Greeting detected'
            }
        
        # Thank you patterns
        thanks = ['cảm ơn', 'thanks', 'cám ơn', 'thank you']
        if any(thank in message_lower for thank in thanks):
            return {
                'mode': 'chat',
                'confidence': 'high',
                'clean_message': message,
                'direct_response': True,
                'response': 'Rất vui được giúp bạn! 😊 Chúc bạn có chuyến đi thú vị! Nếu cần gì thêm, cứ hỏi nhé!',
                'reasoning': 'Thank you detected'
            }
        
        # Question patterns (ask mode)
        question_keywords = ['ở đâu', 'như thế nào', 'bao nhiêu', 'có gì', 'nên đi', 'có nên', 'giá', 'chi phí']
        if any(keyword in message_lower for keyword in question_keywords) or message.endswith('?'):
            return {
                'mode': 'ask',
                'confidence': 'medium',
                'clean_message': message,
                'direct_response': False,
                'reasoning': 'Question pattern detected'
            }
        
        # Edit patterns (edit_plan mode)
        edit_keywords = ['thay đổi', 'sửa', 'bớt', 'thêm', 'đổi', 'thay thế', 'cập nhật']
        if any(keyword in message_lower for keyword in edit_keywords) and current_plan:
            return {
                'mode': 'edit_plan',
                'confidence': 'medium',
                'clean_message': message,
                'direct_response': False,
                'reasoning': 'Edit keywords detected with existing plan'
            }
        
        # Planning patterns (plan mode)
        plan_keywords = ['muốn đi', 'đi du lịch', 'kế hoạch', 'tour', 'lên kế hoạch', 'tạo kế hoạch']
        if any(keyword in message_lower for keyword in plan_keywords):
            return {
                'mode': 'plan',
                'confidence': 'medium',
                'clean_message': message,
                'direct_response': False,
                'reasoning': 'Planning keywords detected'
            }
        
        # Default to plan mode
        return {
            'mode': 'plan',
            'confidence': 'low',
            'clean_message': message,
            'direct_response': False,
            'reasoning': 'No clear pattern, defaulting to plan mode'
        }
    
    def _handle_ask_mode(self, message: str) -> Dict:
        """
        Handle @ask mode - Answer general questions using RAG
        """
        logger.info("❓ ASK MODE - Answering general question")
        
        try:
            # Search for relevant information
            logger.info(f"🔍 Searching for: '{message}'")
            search_results = self.search.search(message, max_results=5)
            formatted_results = self.search.format_results_for_llm(search_results)
            
            # Generate answer using Gemini
            if self.use_gemini:
                try:
                    prompt = f"""Dựa trên câu hỏi và thông tin tìm kiếm, hãy trả lời câu hỏi một cách chi tiết, hữu ích.

CÂU HỎI: {message}

{formatted_results}

HÃY TRẢ LỜI:
- Ngắn gọn, súc tích
- Dựa trên thông tin tìm kiếm
- Thân thiện, hữu ích
- Sử dụng emoji phù hợp
"""
                    logger.debug(prompt)
                    
                    # Retry logic with 15s delay
                    max_retries = 3
                    retry_delay = 15
                    answer = None
                    
                    for attempt in range(max_retries):
                        try:
                            response = self.model.generate_content(prompt)
                            answer = response.text
                            break  # Success
                        except Exception as retry_error:
                            if attempt < max_retries - 1:
                                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {str(retry_error)}. Retrying in {retry_delay}s...")
                                time.sleep(retry_delay)
                            else:
                                raise
                    
                    logger.info(f"✅ Answer generated: {answer[:100]}...")
                    
                    return {
                        'success': True,
                        'message': answer,
                        'has_plan': False,
                        'mode': 'ask',
                        'search_results': search_results[:3]  # Include top 3 for reference
                    }
                    
                except Exception as e:
                    logger.error(f"❌ Gemini error: {str(e)}")
                    # Fallback to simple response
                    pass
            
            # Fallback: Simple formatted response from search results
            if search_results:
                answer = f"Đây là thông tin tôi tìm được về '{message}':\n\n"
                answer += formatted_results
                answer += "\n\n💡 Bạn có câu hỏi nào khác không?"
            else:
                answer = f"Xin lỗi, tôi không tìm thấy thông tin về '{message}'. Bạn có thể hỏi câu khác hoặc cụ thể hơn không? 🤔"
            
            return {
                'success': True,
                'message': answer,
                'has_plan': False,
                'mode': 'ask'
            }
            
        except Exception as e:
            logger.error(f"❌ Ask mode error: {str(e)}")
            return {
                'success': False,
                'message': f"Xin lỗi, có lỗi khi tìm kiếm thông tin: {str(e)}",
                'mode': 'ask'
            }
    
    def _handle_edit_plan_mode(self, message: str, current_plan: Optional[Dict]) -> Dict:
        """
        Handle @edit_plan mode - Modify existing plan based on user request
        """
        logger.info("✏️ EDIT_PLAN MODE - Modifying existing plan")
        
        if not current_plan:
            return {
                'success': False,
                'message': "⚠️ Không có kế hoạch nào để chỉnh sửa. Hãy tạo kế hoạch mới bằng @plan trước nhé!",
                'mode': 'edit_plan'
            }
        
        try:
            logger.info(f"📋 Current plan: {current_plan.get('plan_name', 'Unnamed')}")
            logger.info(f"✏️ Edit request: '{message}'")
            
            # Use Gemini to modify the plan
            if self.use_gemini and self.model:
                try:
                    # Simplified prompt to avoid token limit issues
                    # Only send relevant parts of the plan
                    prompt = f"""Bạn là trợ lý du lịch. Phân tích yêu cầu chỉnh sửa và cập nhật kế hoạch.

TÊN KẾ HOẠCH: {current_plan.get('plan_name', 'Chưa đặt tên')}
ĐIỂM ĐẾN: {current_plan.get('destination', '')}
SỐ NGÀY: {current_plan.get('duration_days', 0)}
NGÂN SÁCH: {current_plan.get('budget', 0)}

LỊCH TRÌNH HIỆN TẠI (rút gọn):
{json.dumps(current_plan.get('itinerary', [])[:2], ensure_ascii=False, indent=2) if current_plan.get('itinerary') else 'Chưa có'}
... (còn {len(current_plan.get('itinerary', [])) - 2} ngày nữa)

YÊU CẦU CHỈNH SỬA: {message}

HÃY:
1. Xác định phần nào cần sửa (ngày nào, hoạt động nào)
2. Mô tả chi tiết sự thay đổi
3. Trả về JSON ĐƠN GIẢN:

{{
  "success": true,
  "changes": "Mô tả ngắn gọn những gì đã thay đổi (2-3 câu)",
  "modified_sections": [
    {{
      "day": 1,
      "activity_index": 0,
      "new_activity": {{ "time": "07:00", "title": "...", "description": "..." }}
    }}
  ]
}}

CHỈ TRẢ VỀ JSON NGẮN GỌN, KHÔNG TRẢ VỀ TOÀN BỘ KẾ HOẠCH."""
                    
                    logger.info("🤖 Calling Gemini to modify plan...")
                    response = self.model.generate_content(prompt)
                    result_text = response.text.strip()
                    
                    logger.debug(f"Gemini response: {result_text[:200]}...")
                    
                    # Clean markdown code blocks if present
                    if result_text.startswith('```'):
                        parts = result_text.split('```')
                        if len(parts) >= 2:
                            result_text = parts[1]
                            if result_text.startswith('json'):
                                result_text = result_text[4:]
                        result_text = result_text.strip()
                    
                    # Try to parse JSON response
                    try:
                        edit_result = json.loads(result_text)
                        
                        if edit_result.get('success'):
                            # Apply modifications to the plan
                            modified_plan = current_plan.copy()
                            
                            # Apply changes from modified_sections
                            if 'modified_sections' in edit_result:
                                for modification in edit_result['modified_sections']:
                                    day_num = modification.get('day', 1)
                                    activity_idx = modification.get('activity_index', 0)
                                    new_activity = modification.get('new_activity')
                                    
                                    # Update the specific activity
                                    if (modified_plan.get('itinerary') and 
                                        day_num <= len(modified_plan['itinerary']) and
                                        new_activity):
                                        
                                        day_data = modified_plan['itinerary'][day_num - 1]
                                        if activity_idx < len(day_data.get('activities', [])):
                                            day_data['activities'][activity_idx] = new_activity
                                            logger.info(f"   Updated Day {day_num}, Activity {activity_idx}")
                            
                            # Or use full modified_plan if provided (backward compatible)
                            elif 'modified_plan' in edit_result:
                                modified_plan = edit_result['modified_plan']
                                logger.info(f"   Using full modified plan from response")
                            
                            changes_description = edit_result.get('changes', 'Đã cập nhật kế hoạch theo yêu cầu')
                            
                            logger.info(f"✅ Plan modified successfully")
                            logger.info(f"   Changes: {changes_description[:100]}...")
                            
                            return {
                                'success': True,
                                'message': f"✅ Đã chỉnh sửa kế hoạch!\n\n**Những gì đã thay đổi:**\n{changes_description}\n\n💡 Bạn có thể xem chi tiết kế hoạch đã cập nhật bên dưới.",
                                'has_plan': True,
                                'plan_data': modified_plan,
                                'mode': 'edit_plan'
                            }
                        else:
                            logger.warning("⚠️ JSON response has success=false")
                            
                    except json.JSONDecodeError as json_err:
                        logger.error(f"❌ Failed to parse JSON: {json_err}")
                        logger.debug(f"Response text: {result_text[:300]}")
                        
                        # Fallback: Use Gemini text response as explanation
                        # But keep original plan since we couldn't parse the modification
                        return {
                            'success': True,
                            'message': f"✅ Tôi đã phân tích yêu cầu của bạn:\n\n{result_text[:800]}\n\n⚠️ Hiện tại bạn có thể tự chỉnh sửa kế hoạch bằng nút 'Chỉnh sửa' trên trang chi tiết.",
                            'has_plan': False,
                            'mode': 'edit_plan'
                        }
                    
                except Exception as e:
                    logger.error(f"❌ Gemini error: {type(e).__name__}: {str(e)}")
                    import traceback
                    logger.debug(f"Traceback:\n{traceback.format_exc()}")
            
            # Fallback: Simple acknowledgment message
            logger.info("⚠️ Falling back to simple response")
            return {
                'success': True,
                'message': f"📝 Tôi đã ghi nhận yêu cầu chỉnh sửa: '{message}'\n\n⚙️ Tính năng tự động chỉnh sửa kế hoạch đang được hoàn thiện.\n\nHiện tại bạn có thể:\n• Tự chỉnh sửa bằng nút '✏️ Chỉnh sửa' trên trang chi tiết kế hoạch\n• Hoặc yêu cầu tạo kế hoạch mới với @plan",
                'has_plan': False,
                'mode': 'edit_plan'
            }
            
        except Exception as e:
            logger.error(f"❌ Edit plan mode error: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return {
                'success': False,
                'message': f"⚠️ Xin lỗi, có lỗi khi xử lý yêu cầu chỉnh sửa.\n\nBạn có thể:\n• Thử lại với yêu cầu cụ thể hơn\n• Tự chỉnh sửa kế hoạch bằng nút 'Chỉnh sửa'\n• Tạo kế hoạch mới với @plan",
                'mode': 'edit_plan'
            }
    
    def _handle_plan_mode(self, message: str, requirements: Optional[Dict] = None) -> Dict:
        """
        Handle @plan mode (default) - Create travel plan
        
        Args:
            message: User's message
            requirements: Pre-extracted requirements from intent analysis (optional)
        """
        logger.info("📋 PLAN MODE - Creating travel plan")
        
        try:
            # Use requirements from intent analysis if available, otherwise extract
            if requirements:
                logger.info("✅ Using requirements from intent analysis")
                logger.info(f"   Requirements: {requirements}")
            else:
                logger.info("🔍 Step 1: Extracting requirements...")
                requirements = self._extract_requirements(message)
                logger.info(f"✅ Requirements extracted: {requirements}")
            
            # Check if we have MINIMUM required info to create plan
            # CHANGED: Now requires destination, duration_days AND budget (not just destination + duration)
            has_destination = requirements.get('destination') is not None
            has_duration = requirements.get('duration_days') is not None
            has_budget = requirements.get('budget') is not None
            
            ready_to_plan = has_destination and has_duration and has_budget
            
            # Update requirements with corrected ready_to_plan status
            requirements['ready_to_plan'] = ready_to_plan
            
            # Recalculate missing_fields to ensure accuracy
            required_core_fields = ['destination', 'duration_days', 'budget']
            optional_fields = ['preferences']
            
            missing_fields = []
            for field in required_core_fields:
                if not requirements.get(field):
                    missing_fields.append(field)
            
            # Preferences is optional, but we still track it
            if not requirements.get('preferences'):
                missing_fields.append('preferences')
            
            requirements['missing_fields'] = missing_fields
            
            logger.info(f"   📊 Readiness check:")
            logger.info(f"      - Destination: {has_destination} ({requirements.get('destination')})")
            logger.info(f"      - Duration: {has_duration} ({requirements.get('duration_days')} days)")
            budget_display = self._format_currency(requirements.get('budget')) if requirements.get('budget') else "None"
            logger.info(f"      - Budget: {has_budget} ({budget_display})")
            logger.info(f"      - Ready to plan: {ready_to_plan}")
            logger.info(f"      - Missing fields: {missing_fields}")
            
            # Check if we have enough info to create plan
            if ready_to_plan:
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
                    'requirements': requirements,
                    'mode': 'plan'
                }
            
            else:
                # Ask for missing information
                logger.info("⚠️ Not ready to plan yet. Missing REQUIRED information.")
                missing = requirements.get('missing_fields', [])
                logger.info(f"   Missing fields: {missing}")
                
                # Create a more specific message based on what's missing
                if not has_destination and not has_duration and not has_budget:
                    response_text = "Để tạo kế hoạch du lịch hoàn chỉnh, tôi cần bạn cho biết:\n\n"
                    response_text += "📍 **Điểm đến**: Bạn muốn đi đâu?\n"
                    response_text += "📅 **Số ngày**: Bạn dự định đi bao nhiêu ngày?\n"
                    response_text += "💰 **Ngân sách**: Bạn có ngân sách khoảng bao nhiêu?\n"
                    response_text += "🎯 **Sở thích** (tùy chọn): Bạn thích hoạt động gì? (VD: tham quan, ẩm thực, mạo hiểm...)\n\n"
                    response_text += "Ví dụ: *'Tôi muốn đi Đà Lạt 3 ngày, ngân sách 5 triệu, thích thiên nhiên và ẩm thực'*"
                else:
                    response_text = get_response_template(
                        'missing_info',
                        missing_fields=format_missing_fields(missing)
                    )
                
                logger.info(f"💬 Response prepared: Asking for missing info")
                
                return {
                    'success': True,
                    'message': response_text,
                    'has_plan': False,
                    'requirements': requirements,
                    'mode': 'plan'
                }
        
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return {
                'success': False,
                'message': get_response_template('error', error=str(e)),
                'has_plan': False,
                'mode': 'plan'
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
        
        # Check if ready - NOW requires destination, duration_days AND budget
        ready = destination is not None and duration_days is not None and budget is not None
        
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
                'duration_days' in requirements and
                'budget' in requirements
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
        """
        Generate detailed itinerary using progressive API calls to avoid timeout.
        
        Strategy:
        1. First call: Generate plan outline (name, budget breakdown, general suggestions)
        2. Subsequent calls: Generate detailed activities for each day individually
        
        This approach:
        - Avoids API timeout by keeping each request small
        - Provides better error handling per day
        - Cleaner and more maintainable code
        """
        try:
            if not self.model:
                logger.warning("   ⚠️ Gemini model not available, using mock data")
                return self._create_mock_itinerary(requirements)
            
            # Step 1: Generate plan outline
            logger.info("   📋 Step 1: Generating plan outline...")
            plan_outline = self._generate_plan_outline(requirements, search_results)
            
            if not plan_outline:
                logger.warning("   ⚠️ Failed to generate outline, using mock data")
                return self._create_mock_itinerary(requirements)
            
            # Step 2: Generate detailed itinerary for each day
            logger.info(f"   📅 Step 2: Generating detailed itinerary for {requirements.get('duration_days', 3)} days...")
            itinerary = self._generate_daily_itineraries(requirements, plan_outline, search_results)
            
            # Step 3: Combine outline and daily itineraries
            plan_data = {
                'plan_name': plan_outline.get('plan_name', f"Khám phá {requirements.get('destination', 'Việt Nam')}"),
                'destination': requirements.get('destination', 'Việt Nam'),
                'duration_days': requirements.get('duration_days', 3),
                'budget': requirements.get('budget'),
                'preferences': requirements.get('preferences'),
                'itinerary': itinerary,
                'cost_breakdown': plan_outline.get('cost_breakdown', {}),
                'total_cost': plan_outline.get('total_cost', requirements.get('budget', 0)),
                'notes': plan_outline.get('notes', [])
            }
            
            logger.info(f"   ✅ Complete plan generated with {len(itinerary)} days")
            return plan_data
            
        except Exception as e:
            logger.error(f"   ❌ Itinerary generation error: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            logger.warning("   ⚠️ Falling back to mock itinerary")
            return self._create_mock_itinerary(requirements)
    
    def _generate_plan_outline(self, requirements: Dict, search_results: str) -> Optional[Dict]:
        """
        Generate high-level plan outline (Step 1)
        
        Returns:
            Dict with plan_name, cost_breakdown, total_cost, notes, day_themes
        """
        budget_number = requirements.get('budget', 5000000)
        duration_days = requirements.get('duration_days', 3)
        destination = requirements.get('destination', 'Việt Nam')
        preferences = requirements.get('preferences', 'khám phá, ẩm thực')
        
        # Limit search results to avoid timeout
        search_summary = search_results[:300] if len(search_results) > 300 else search_results
        
        prompt = f"""Tạo OUTLINE kế hoạch du lịch {destination} {duration_days} ngày.

THÔNG TIN:
- Ngân sách: {self._format_currency(budget_number)}
- Sở thích: {preferences}
- Tham khảo: {search_summary}

TRẢ VỀ JSON:
{{
  "plan_name": "Tên hấp dẫn cho kế hoạch",
  "cost_breakdown": {{
    "accommodation": {{"amount": 1500000, "description": "Mô tả ngắn"}},
    "food": {{"amount": 1200000, "description": "Mô tả ngắn"}},
    "transportation": {{"amount": 800000, "description": "Mô tả ngắn"}},
    "activities": {{"amount": 500000, "description": "Mô tả ngắn"}}
  }},
  "total_cost": {budget_number},
  "general_notes": [
    "Lưu ý chung về thời tiết, khí hậu",
    "Lưu ý về di chuyển, phương tiện",
    "Lưu ý về ăn uống, đặc sản",
    "Lưu ý về an toàn, số điện thoại khẩn cấp",
    "Tips hữu ích cho chuyến đi"
  ],
  "day_themes": [
    {{"day": 1, "theme": "Khám phá trung tâm"}},
    {{"day": 2, "theme": "Vùng ngoại ô"}}
  ]
}}

YÊU CẦU:
- general_notes: 3-5 lưu ý TỔNG QUAN cho cả chuyến đi
- Lưu ý phải cụ thể, hữu ích, thực tế
- CHỈ TRẢ VỀ JSON, KHÔNG TEXT KHÁC."""
        
        try:
            logger.info(f"      🤖 Calling Gemini for outline (prompt: {len(prompt)} chars)...")
            logger.info(prompt)
            
            # Retry logic with 15s delay
            max_retries = 3
            retry_delay = 15
            outline = None
            
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    response_text = response.text.strip()
                    
                    logger.info(f"      ✅ Outline received ({len(response_text)} chars)")
                    
                    # Parse JSON
                    outline = self._parse_json_response(response_text)
                    break  # Success
                    
                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"      ⚠️ Attempt {attempt + 1} failed: {str(retry_error)}. Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"      ❌ All {max_retries} attempts failed")
                        return None
            
            if outline:
                logger.info(f"      ✅ Outline parsed: {outline.get('plan_name', 'N/A')}")
                return outline
            else:
                logger.warning("      ⚠️ Failed to parse outline JSON")
                return None
                
        except Exception as e:
            logger.error(f"      ❌ Outline generation error: {str(e)}")
            return None
    
    def _generate_daily_itineraries(self, requirements: Dict, plan_outline: Dict, 
                                   search_results: str) -> List[Dict]:
        """
        Generate detailed activities for each day (Step 2)
        
        Returns:
            List of daily itineraries with activities
        """
        duration_days = requirements.get('duration_days', 3)
        destination = requirements.get('destination', 'Việt Nam')
        day_themes = plan_outline.get('day_themes', [])
        
        itinerary = []
        
        for day_num in range(1, duration_days + 1):
            logger.info(f"      📅 Generating Day {day_num}/{duration_days}...")
            
            # Get theme for this day
            theme = "Khám phá"
            for dt in day_themes:
                if dt.get('day') == day_num:
                    theme = dt.get('theme', 'Khám phá')
                    break
            
            # Generate activities for this specific day
            day_data = self._generate_single_day(
                day_num=day_num,
                destination=destination,
                theme=theme,
                search_results=search_results
            )
            
            if day_data:
                itinerary.append(day_data)
                logger.info(f"      ✅ Day {day_num} completed: {len(day_data.get('activities', []))} activities")
            else:
                logger.warning(f"      ⚠️ Day {day_num} generation failed, using template")
                # Fallback: use a simple template
                itinerary.append({
                    'day': day_num,
                    'title': f'Ngày {day_num}: {theme}',
                    'activities': [
                        {'time': '08:00', 'title': 'Khám phá địa điểm', 'description': f'{theme} tại {destination}', 'cost': 100000}
                    ]
                })
        
        return itinerary
    
    def _generate_single_day(self, day_num: int, destination: str, 
                            theme: str, search_results: str) -> Optional[Dict]:
        """
        Generate detailed activities for a single day
        
        Args:
            day_num: Day number (1, 2, 3, ...)
            destination: Destination name
            theme: Theme for this day (e.g., "Khám phá trung tâm")
            search_results: Search results for reference
            
        Returns:
            Dict with day, title, activities
        """
        # Limit search for each day to avoid long prompts
        search_snippet = search_results[:200] if len(search_results) > 200 else search_results
        
        prompt = f"""Tạo lịch trình CHI TIẾT cho NGÀY {day_num} tại {destination}.

CHỦ ĐỀ NGÀY {day_num}: {theme}
THAM KHẢO: {search_snippet}

TRẢ VỀ JSON:
{{
  "day": {day_num},
  "title": "Ngày {day_num}: {theme}",
  "description": "Mô tả ngắn gọn về ngày này",
  "activities": [
    {{
      "time": "07:00",
      "type": "breakfast",
      "title": "Tên quán/hoạt động",
      "description": "Mô tả chi tiết, địa chỉ, giá cả",
      "location": "Địa chỉ cụ thể",
      "cost": 50000
    }},
    {{
      "time": "08:30",
      "type": "sightseeing",
      "title": "Tên địa điểm",
      "description": "Mô tả, địa chỉ, giá vé",
      "location": "Địa chỉ cụ thể",
      "cost": 100000
    }}
  ],
  "notes": [
    "Lưu ý riêng cho ngày này (thời tiết, tránh giờ cao điểm...)",
    "Tips hữu ích cho các hoạt động trong ngày",
    "Những điều cần chuẩn bị, mang theo"
  ]
}}

YÊU CẦU:
- Ít nhất 5-7 hoạt động/ngày
- Bao gồm: ăn sáng, tham quan, ăn trưa, hoạt động chiều, ăn tối
- Có địa chỉ cụ thể (location) và giá tiền thực tế
- notes: 2-4 lưu ý CỤ THỂ cho ngày này
- CHỈ TRẢ VỀ JSON"""
        
        try:
            # Retry logic with 15s delay
            max_retries = 3
            retry_delay = 15
            day_data = None
            
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    response_text = response.text.strip()
                    
                    # Parse JSON
                    day_data = self._parse_json_response(response_text)
                    break  # Success
                    
                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"         ⚠️ Day {day_num} attempt {attempt + 1} failed: {str(retry_error)}. Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"         ❌ Day {day_num} all {max_retries} attempts failed")
                        return None
            
            if day_data and 'activities' in day_data:
                return day_data
            else:
                logger.warning(f"         ⚠️ Failed to parse day {day_num} JSON")
                return None
                
        except Exception as e:
            logger.error(f"         ❌ Day {day_num} generation error: {str(e)}")
            return None
    
    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """
        Clean and parse JSON response from Gemini
        
        Handles:
        - Markdown code blocks (```json ... ```)
        - Extra whitespace
        - Text before/after JSON
        """
        try:
            # Clean markdown code blocks
            cleaned_text = text.strip()
            if cleaned_text.startswith('```'):
                parts = cleaned_text.split('```')
                if len(parts) >= 2:
                    cleaned_text = parts[1]
                    if cleaned_text.startswith('json'):
                        cleaned_text = cleaned_text[4:]
                cleaned_text = cleaned_text.strip()
            
            # Try to find JSON object
            if '{' in cleaned_text and '}' in cleaned_text:
                start = cleaned_text.index('{')
                end = cleaned_text.rindex('}') + 1
                json_str = cleaned_text[start:end]
                
                # Parse
                data = json.loads(json_str)
                return data
            else:
                return None
                
        except json.JSONDecodeError as e:
            logger.debug(f"         JSON parse error: {str(e)}")
            return None
        except Exception as e:
            logger.debug(f"         Parse error: {str(e)}")
            return None
    
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
                'description': 'Ngày đầu tiên khám phá các điểm tham quan trung tâm thành phố',
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
                ],
                'notes': [
                    'Mang theo áo ấm vì thời tiết Đà Lạt mát quanh năm, buổi tối có thể xuống 15°C',
                    'Nên thuê xe máy để di chuyển linh hoạt (100-150k/ngày) hoặc dùng Grab',
                    'Đặt bàn trước tại các nhà hàng nổi tiếng, đặc biệt vào cuối tuần',
                    'Mang theo kem chống nắng và mũ vì ban ngày nắng gắt'
                ]
            })
        
        if days >= 2:
            itinerary.append({
                'day': 2,
                'title': f'Ngày 2: Khám phá ngoại thành {destination}',
                'description': 'Tham quan các điểm du lịch ngoại thành và làng hoa',
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
                ],
                'notes': [
                    'Khởi hành sớm để tránh kẹt xe, đặc biệt khi đi Thung Lũng Tình Yêu',
                    'Mang theo đồ ăn nhẹ và nước uống vì một số điểm tham quan xa trung tâm',
                    'Nên thuê xe máy hoặc xe ô tô riêng để thuận tiện di chuyển',
                    'Kiểm tra thời tiết trước khi đi, tránh ngày mưa'
                ]
            })
        
        if days >= 3:
            itinerary.append({
                'day': 3,
                'title': f'Ngày 3: Mua sắm và trở về',
                'description': 'Mua sắm đặc sản và chuẩn bị về',
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
                ],
                'notes': [
                    'Nên mua đặc sản tại các cửa hàng uy tín có niêm yết giá rõ ràng',
                    'Tránh mua hàng ở khu vực du lịch vì giá thường cao hơn',
                    'Đặt xe về trước để có giá tốt, tránh kẹt xe giờ cao điểm',
                    'Nhớ mang theo thuốc say xe nếu đi đường đèo dốc'
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
            'general_notes': [
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
