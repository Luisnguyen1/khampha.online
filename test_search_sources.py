"""
Test script to verify search sources feature
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agents.search_tool import SearchTool

def test_search_sources():
    """Test that SearchTool returns sources correctly"""
    print("="*80)
    print("Testing SearchTool.extract_sources_for_storage()")
    print("="*80)
    
    search = SearchTool(max_results=3)
    
    # Perform a search
    print("\n1. Performing search for 'du lịch Đà Lạt'...")
    results = search.search("du lịch Đà Lạt", max_results=3)
    print(f"   ✅ Got {len(results)} results")
    
    # Extract sources
    print("\n2. Extracting sources for storage...")
    sources = search.extract_sources_for_storage(results)
    print(f"   ✅ Extracted {len(sources)} sources")
    
    # Display sources
    print("\n3. Source details:")
    for i, source in enumerate(sources, 1):
        print(f"\n   Source {i}:")
        print(f"   - Title: {source['title'][:60]}...")
        print(f"   - URL: {source['url']}")
        print(f"   - Snippet length: {len(source['snippet'])} chars")
    
    # Verify structure
    print("\n4. Verifying structure...")
    for source in sources:
        assert 'title' in source, "Missing 'title' key"
        assert 'url' in source, "Missing 'url' key"
        assert 'snippet' in source, "Missing 'snippet' key"
    print("   ✅ All sources have required keys")
    
    print("\n" + "="*80)
    print("✅ All tests passed!")
    print("="*80)

if __name__ == '__main__':
    test_search_sources()
