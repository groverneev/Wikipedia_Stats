#!/usr/bin/env python3
"""
Quick Wikipedia Statistics
==========================

This script provides quick answers to basic Wikipedia questions:
- How many pages are there?
- How many words per page on average?
- Basic statistics about Wikipedia
"""

import requests
import json
import time

def get_wikipedia_basic_stats():
    """Get basic Wikipedia statistics"""
    print("Fetching Wikipedia statistics...")
    
    api_url = "https://en.wikipedia.org/w/api.php"
    
    # Get overall statistics
    params = {
        'action': 'query',
        'format': 'json',
        'meta': 'siteinfo',
        'siprop': 'statistics'
    }
    
    try:
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if 'query' in data and 'statistics' in data['query']:
            stats = data['query']['statistics']
            
            print("\n=== WIKIPEDIA BASIC STATISTICS ===")
            print(f"Total pages: {stats.get('pages', 'N/A'):,}")
            print(f"Total articles: {stats.get('articles', 'N/A'):,}")
            print(f"Total edits: {stats.get('edits', 'N/A'):,}")
            print(f"Total users: {stats.get('users', 'N/A'):,}")
            print(f"Active users: {stats.get('activeusers', 'N/A'):,}")
            print(f"Administrators: {stats.get('admins', 'N/A'):,}")
            print(f"Images: {stats.get('images', 'N/A'):,}")
            
            return stats
    except Exception as e:
        print(f"Error fetching statistics: {e}")
        return None

def get_sample_page_stats(sample_size=10):
    """Get statistics from a sample of random pages"""
    print(f"\nAnalyzing {sample_size} random pages for content statistics...")
    
    api_url = "https://en.wikipedia.org/w/api.php"
    
    # Get random pages
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'random',
        'rnnamespace': 0,  # Main namespace (articles only)
        'rnlimit': min(sample_size, 500),
        'rnfilterredir': 'nonredirects'
    }
    
    try:
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if 'query' in data and 'random' in data['query']:
            pages = data['query']['random']
            
            word_counts = []
            edit_counts = []
            
            for page in pages:
                title = page['title']
                print(f"Analyzing: {title}")
                
                # Get page content
                content_params = {
                    'action': 'parse',
                    'format': 'json',
                    'page': title,
                    'prop': 'text'
                }
                
                content_response = requests.get(api_url, params=content_params)
                content_data = content_response.json()
                
                if 'parse' in content_data and 'text' in content_data['parse']:
                    text = content_data['parse']['text']['*']
                    # Remove HTML tags for word count
                    import re
                    clean_text = re.sub(r'<[^>]+>', '', text)
                    word_count = len(clean_text.split())
                    word_counts.append(word_count)
                
                # Get edit count
                edit_params = {
                    'action': 'query',
                    'format': 'json',
                    'prop': 'info',
                    'titles': title,
                    'inprop': 'editcount'
                }
                
                edit_response = requests.get(api_url, params=edit_params)
                edit_data = edit_response.json()
                
                if 'query' in edit_data and 'pages' in edit_data['query']:
                    page_id = list(edit_data['query']['pages'].keys())[0]
                    if page_id != '-1':
                        page_data = edit_data['query']['pages'][page_id]
                        edit_count = page_data.get('editcount', 0)
                        edit_counts.append(edit_count)
                
                time.sleep(0.1)  # Be respectful to the API
            
            if word_counts:
                avg_words = sum(word_counts) / len(word_counts)
                median_words = sorted(word_counts)[len(word_counts)//2]
                
                print(f"\n=== CONTENT STATISTICS (Sample of {len(word_counts)} pages) ===")
                print(f"Average words per page: {avg_words:.0f}")
                print(f"Median words per page: {median_words}")
                print(f"Range: {min(word_counts)} - {max(word_counts)} words")
            
            if edit_counts:
                avg_edits = sum(edit_counts) / len(edit_counts)
                median_edits = sorted(edit_counts)[len(edit_counts)//2]
                
                print(f"\n=== EDIT STATISTICS ===")
                print(f"Average edits per page: {avg_edits:.0f}")
                print(f"Median edits per page: {median_edits}")
                print(f"Range: {min(edit_counts)} - {max(edit_counts)} edits")
    
    except Exception as e:
        print(f"Error analyzing pages: {e}")

def get_controversial_pages_quick():
    """Quick analysis of potentially controversial pages"""
    print("\nSearching for potentially controversial pages...")
    
    api_url = "https://en.wikipedia.org/w/api.php"
    
    # Get pages with high edit counts
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'allpages',
        'aplimit': 50,
        'apnamespace': 0,
        'apfilterredir': 'nonredirects'
    }
    
    try:
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if 'query' in data and 'allpages' in data['query']:
            pages = data['query']['allpages']
            
            controversial_candidates = []
            
            for page in pages[:20]:  # Check first 20 pages
                title = page['title']
                
                # Get edit count
                edit_params = {
                    'action': 'query',
                    'format': 'json',
                    'prop': 'info',
                    'titles': title,
                    'inprop': 'editcount'
                }
                
                edit_response = requests.get(api_url, params=edit_params)
                edit_data = edit_response.json()
                
                if 'query' in edit_data and 'pages' in edit_data['query']:
                    page_id = list(edit_data['query']['pages'].keys())[0]
                    if page_id != '-1':
                        page_data = edit_data['query']['pages'][page_id]
                        edit_count = page_data.get('editcount', 0)
                        
                        if edit_count > 100:  # High edit count threshold
                            controversial_candidates.append({
                                'title': title,
                                'edit_count': edit_count
                            })
                
                time.sleep(0.1)
            
            if controversial_candidates:
                controversial_candidates.sort(key=lambda x: x['edit_count'], reverse=True)
                
                print(f"\n=== POTENTIALLY CONTROVERSIAL PAGES (High Edit Count) ===")
                for i, page in enumerate(controversial_candidates[:10], 1):
                    print(f"{i}. {page['title']} ({page['edit_count']} edits)")
    
    except Exception as e:
        print(f"Error finding controversial pages: {e}")

def main():
    """Main function"""
    print("Quick Wikipedia Statistics Tool")
    print("=" * 40)
    
    # Get basic statistics
    stats = get_wikipedia_basic_stats()
    
    # Get sample page statistics
    get_sample_page_stats(sample_size=15)
    
    # Find controversial pages
    get_controversial_pages_quick()
    
    print("\n" + "=" * 40)
    print("Analysis complete!")
    print("\nFor more detailed analysis, run: python wikipedia_analysis.py")

if __name__ == "__main__":
    main() 