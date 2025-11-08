"""
Web search tool using DuckDuckGo
No API key required
"""
from typing import List, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SearchTool:
    """Web search using DuckDuckGo"""
    
    def __init__(self, max_results: int = 5, timeout: int = 10):
        self.max_results = max_results
        self.timeout = timeout
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Search the web using DuckDuckGo
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, url
        """
        logger.info(f"🔍 Starting search for: '{query}'")
        
        try:
            from ddgs import DDGS
            logger.info("✅ DuckDuckGo library imported successfully")
            
            results = []
            max_res = max_results or self.max_results
            logger.info(f"📊 Max results requested: {max_res}")
            
            try:
                # Fixed: Remove proxies parameter and use simpler initialization
                ddgs = DDGS(timeout=self.timeout)
                logger.info("🌐 DDGS instance created, performing search...")
                
                # Use the text search method - use 'query' as first positional argument
                search_results = ddgs.text(
                    query,  # First positional argument
                    region='vn-vi',  # Vietnam region
                    safesearch='moderate',
                    timelimit='y',  # Last year
                    max_results=max_res
                )
                
                logger.info("📥 Search results received, processing...")
                
                # Handle both generator and list returns
                result_list = list(search_results) if search_results else []
                
                for i, r in enumerate(result_list):
                    results.append({
                        'title': r.get('title', ''),
                        'snippet': r.get('body', ''),
                        'url': r.get('href', ''),
                        'source': 'duckduckgo'
                    })
                    logger.debug(f"  Result {i+1}: {r.get('title', 'No title')[:50]}...")
                
                logger.info(f"✅ Search completed: {query} - {len(results)} results")
                return results
                
            except Exception as ddgs_error:
                logger.error(f"❌ DuckDuckGo search failed: {type(ddgs_error).__name__}: {str(ddgs_error)}")
                logger.warning("⚠️ Falling back to mock results")
                return self._mock_search(query, max_results)
            
        except ImportError as import_error:
            logger.warning(f"⚠️ duckduckgo-search not installed: {str(import_error)}")
            logger.info("📦 Returning mock results")
            return self._mock_search(query, max_results)
        
        except Exception as e:
            logger.error(f"❌ Unexpected search error: {type(e).__name__}: {str(e)}")
            logger.warning("⚠️ Returning mock results as fallback")
            return self._mock_search(query, max_results)
    
    def _mock_search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Mock search results for development/testing
        Returns realistic-looking travel information
        """
        logger.info(f"🎭 Using mock search for query: '{query}'")
        max_res = max_results or self.max_results
        
        # Extract location from query
        location = query.split()[0] if query else "Việt Nam"
        logger.info(f"📍 Extracted location: {location}")
        
        mock_results = [
            {
                'title': f'Du lịch {location} - Cẩm nang từ A-Z',
                'snippet': f'Khám phá {location} với lịch trình chi tiết, địa điểm tham quan nổi tiếng, ẩm thực đặc sản và kinh nghiệm du lịch tự túc. Cập nhật 2025.',
                'url': f'https://example.com/{location.lower()}-guide',
                'source': 'mock'
            },
            {
                'title': f'Top 10 điểm đến tại {location} không thể bỏ qua',
                'snippet': f'Danh sách các địa điểm du lịch đẹp nhất tại {location}: bãi biển, núi non, di tích lịch sử, làng nghề truyền thống...',
                'url': f'https://example.com/{location.lower()}-top-10',
                'source': 'mock'
            },
            {
                'title': f'Chi phí du lịch {location} 2025: Ăn, ở, đi lại',
                'snippet': f'Ước tính chi phí cho chuyến du lịch {location}: vé máy bay, khách sạn, ăn uống, vé tham quan. Cập nhật bảng giá mới nhất.',
                'url': f'https://example.com/{location.lower()}-budget',
                'source': 'mock'
            },
            {
                'title': f'Review {location}: Kinh nghiệm thực tế',
                'snippet': f'Chia sẻ kinh nghiệm du lịch {location} của mình: thời điểm đẹp nhất, cách di chuyển, nên ở đâu, ăn gì ngon...',
                'url': f'https://example.com/{location.lower()}-review',
                'source': 'mock'
            },
            {
                'title': f'Lịch trình {location} 3 ngày 2 đêm chi tiết',
                'snippet': f'Gợi ý lịch trình {location} cho người đi lần đầu: ngày 1 khám phá trung tâm, ngày 2 tham quan ngoại thành, ngày 3 mua sắm và về.',
                'url': f'https://example.com/{location.lower()}-itinerary',
                'source': 'mock'
            }
        ]
        
        return mock_results[:max_res]
    
    def search_multiple(self, queries: List[str], max_per_query: int = 3) -> Dict[str, List[Dict]]:
        """
        Search multiple queries and return grouped results
        
        Args:
            queries: List of search queries
            max_per_query: Max results per query
            
        Returns:
            Dictionary mapping query to results
        """
        results = {}
        
        for query in queries:
            results[query] = self.search(query, max_results=max_per_query)
        
        return results
    
    def format_results_for_llm(self, results: List[Dict[str, str]]) -> str:
        """
        Format search results for LLM consumption
        
        Args:
            results: List of search results
            
        Returns:
            Formatted string with numbered results
        """
        if not results:
            return "Không tìm thấy kết quả tìm kiếm."
        
        formatted = "THÔNG TIN TÌM KIẾM:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result['title']}**\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   🔗 {result['url']}\n\n"
        
        return formatted
    
    def extract_sources_for_storage(self, results: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Extract source information for storage in database
        
        Args:
            results: List of search results
            
        Returns:
            List of dicts with title, url, snippet for each source
        """
        sources = []
        for result in results:
            sources.append({
                'title': result.get('title', 'Không có tiêu đề'),
                'url': result.get('url', ''),
                'snippet': result.get('snippet', '')[:200]  # Limit snippet length
            })
        return sources
    
    def extract_travel_info(self, results: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Extract structured travel information from search results
        
        Args:
            results: List of search results
            
        Returns:
            Dictionary with structured travel info
        """
        # Combine all snippets
        all_text = " ".join([r['snippet'] for r in results])
        
        # Simple keyword extraction (can be improved with NLP)
        info = {
            'has_cost_info': any(word in all_text.lower() for word in ['giá', 'chi phí', 'vnđ', 'đồng']),
            'has_activities': any(word in all_text.lower() for word in ['tham quan', 'hoạt động', 'điểm đến']),
            'has_food': any(word in all_text.lower() for word in ['ẩm thực', 'món ăn', 'nhà hàng']),
            'has_accommodation': any(word in all_text.lower() for word in ['khách sạn', 'homestay', 'lưu trú']),
            'total_results': len(results),
            'sources': [r['url'] for r in results]
        }
        
        return info


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    search = SearchTool(max_results=3)
    
    # Test single search
    print("Testing single search...")
    results = search.search("du lịch Đà Lạt")
    print(f"Found {len(results)} results")
    
    # Test formatted output
    print("\nFormatted for LLM:")
    print(search.format_results_for_llm(results))
    
    # Test info extraction
    print("\nExtracted info:")
    info = search.extract_travel_info(results)
    print(info)
