#!/usr/bin/env python3
"""
Wikipedia Comprehensive Analysis Tool
====================================

This script analyzes various aspects of Wikipedia including:
- Total number of pages
- Words per page statistics
- Edit patterns and page evolution
- Controversial page analysis
- Content statistics
"""

import requests
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from collections import Counter, defaultdict
import re
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WikipediaAnalyzer:
    """Comprehensive Wikipedia analysis tool"""
    
    def __init__(self, language='en'):
        self.language = language
        self.base_url = f"https://{language}.wikipedia.org/api/rest_v1"
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WikipediaAnalyzer/1.0 (Educational Research Project)'
        })
    
    def get_wikipedia_statistics(self) -> Dict:
        """Get overall Wikipedia statistics"""
        logger.info("Fetching Wikipedia statistics...")
        
        stats = {}
        
        # Get total number of pages
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'meta': 'siteinfo',
                'siprop': 'statistics'
            }
            response = self.session.get(self.api_url, params=params)
            data = response.json()
            
            if 'query' in data and 'statistics' in data['query']:
                stats_data = data['query']['statistics']
                stats.update({
                    'total_pages': stats_data.get('pages', 0),
                    'total_articles': stats_data.get('articles', 0),
                    'total_edits': stats_data.get('edits', 0),
                    'total_users': stats_data.get('users', 0),
                    'active_users': stats_data.get('activeusers', 0),
                    'admins': stats_data.get('admins', 0),
                    'images': stats_data.get('images', 0)
                })
                logger.info(f"Total pages: {stats['total_pages']:,}")
                logger.info(f"Total articles: {stats['total_articles']:,}")
                logger.info(f"Total edits: {stats['total_edits']:,}")
        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
        
        return stats
    
    def get_random_pages(self, limit: int = 100) -> List[Dict]:
        """Get random pages for analysis"""
        logger.info(f"Fetching {limit} random pages...")
        
        pages = []
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'random',
            'rnnamespace': 0,  # Main namespace (articles only)
            'rnlimit': min(limit, 500),  # API limit is 500
            'rnfilterredir': 'nonredirects'
        }
        
        try:
            response = self.session.get(self.api_url, params=params)
            data = response.json()
            
            if 'query' in data and 'random' in data['query']:
                pages = data['query']['random']
                logger.info(f"Retrieved {len(pages)} random pages")
        except Exception as e:
            logger.error(f"Error fetching random pages: {e}")
        
        return pages
    
    def get_page_content_stats(self, page_title: str) -> Dict:
        """Get content statistics for a specific page"""
        logger.info(f"Analyzing page: {page_title}")
        
        stats = {
            'title': page_title,
            'word_count': 0,
            'char_count': 0,
            'section_count': 0,
            'reference_count': 0,
            'link_count': 0,
            'image_count': 0,
            'edit_count': 0,
            'last_edit': None,
            'creation_date': None
        }
        
        try:
            # Get page content
            params = {
                'action': 'parse',
                'format': 'json',
                'page': page_title,
                'prop': 'text|sections|links|images|externallinks'
            }
            response = self.session.get(self.api_url, params=params)
            data = response.json()
            
            if 'parse' in data:
                parse_data = data['parse']
                
                # Get text content
                if 'text' in parse_data and '*' in parse_data['text']:
                    text = parse_data['text']['*']
                    # Remove HTML tags for word count
                    clean_text = re.sub(r'<[^>]+>', '', text)
                    stats['word_count'] = len(clean_text.split())
                    stats['char_count'] = len(clean_text)
                
                # Count sections
                if 'sections' in parse_data:
                    stats['section_count'] = len(parse_data['sections'])
                
                # Count links
                if 'links' in parse_data:
                    stats['link_count'] = len(parse_data['links'])
                
                # Count images
                if 'images' in parse_data:
                    stats['image_count'] = len(parse_data['images'])
            
            # Get edit history
            edit_params = {
                'action': 'query',
                'format': 'json',
                'prop': 'revisions',
                'titles': page_title,
                'rvprop': 'timestamp|user|comment',
                'rvlimit': 1,
                'rvdir': 'newer'
            }
            edit_response = self.session.get(self.api_url, params=edit_params)
            edit_data = edit_response.json()
            
            if 'query' in edit_data and 'pages' in edit_data['query']:
                page_id = list(edit_data['query']['pages'].keys())[0]
                if page_id != '-1':  # Page exists
                    page_data = edit_data['query']['pages'][page_id]
                    if 'revisions' in page_data:
                        stats['last_edit'] = page_data['revisions'][0]['timestamp']
            
            # Get total edit count
            edit_count_params = {
                'action': 'query',
                'format': 'json',
                'prop': 'info',
                'titles': page_title,
                'inprop': 'editcount'
            }
            edit_count_response = self.session.get(self.api_url, params=edit_count_params)
            edit_count_data = edit_count_response.json()
            
            if 'query' in edit_count_data and 'pages' in edit_count_data['query']:
                page_id = list(edit_count_data['query']['pages'].keys())[0]
                if page_id != '-1':
                    page_data = edit_count_data['query']['pages'][page_id]
                    stats['edit_count'] = page_data.get('editcount', 0)
        
        except Exception as e:
            logger.error(f"Error analyzing page {page_title}: {e}")
        
        return stats
    
    def get_edit_history(self, page_title: str, limit: int = 100) -> List[Dict]:
        """Get detailed edit history for a page"""
        logger.info(f"Fetching edit history for: {page_title}")
        
        edits = []
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'titles': page_title,
            'rvprop': 'timestamp|user|comment|size|tags',
            'rvlimit': min(limit, 500),
            'rvdir': 'newer'
        }
        
        try:
            response = self.session.get(self.api_url, params=params)
            data = response.json()
            
            if 'query' in data and 'pages' in data['query']:
                page_id = list(data['query']['pages'].keys())[0]
                if page_id != '-1':
                    page_data = data['query']['pages'][page_id]
                    if 'revisions' in page_data:
                        edits = page_data['revisions']
                        logger.info(f"Retrieved {len(edits)} edits")
        except Exception as e:
            logger.error(f"Error fetching edit history: {e}")
        
        return edits
    
    def find_controversial_pages(self, limit: int = 50) -> List[Dict]:
        """Find potentially controversial pages based on edit patterns"""
        logger.info("Searching for controversial pages...")
        
        controversial_pages = []
        
        # Get pages with high edit counts (potential controversy indicators)
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'allpages',
            'aplimit': min(limit, 500),
            'apnamespace': 0,
            'apfilterredir': 'nonredirects'
        }
        
        try:
            # This is a simplified approach - in practice, you'd want to analyze
            # edit patterns, talk page activity, and other indicators
            response = self.session.get(self.api_url, params=params)
            data = response.json()
            
            if 'query' in data and 'allpages' in data['query']:
                pages = data['query']['allpages']
                
                # Analyze each page for controversy indicators
                for page in pages[:limit]:
                    title = page['title']
                    
                    # Get edit history to analyze patterns
                    edits = self.get_edit_history(title, limit=50)
                    
                    if edits:
                        # Calculate controversy indicators
                        edit_count = len(edits)
                        unique_editors = len(set(edit['user'] for edit in edits if 'user' in edit))
                        recent_edits = len([e for e in edits if 'timestamp' in e and 
                                          datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) > 
                                          datetime.now().replace(tzinfo=None) - timedelta(days=30)])
                        
                        controversy_score = (edit_count * 0.3 + 
                                           unique_editors * 0.4 + 
                                           recent_edits * 0.3)
                        
                        if controversy_score > 10:  # Threshold for "controversial"
                            controversial_pages.append({
                                'title': title,
                                'edit_count': edit_count,
                                'unique_editors': unique_editors,
                                'recent_edits': recent_edits,
                                'controversy_score': controversy_score
                            })
                    
                    time.sleep(0.1)  # Be respectful to the API
        
        except Exception as e:
            logger.error(f"Error finding controversial pages: {e}")
        
        # Sort by controversy score
        controversial_pages.sort(key=lambda x: x['controversy_score'], reverse=True)
        return controversial_pages
    
    def analyze_page_evolution(self, page_title: str) -> Dict:
        """Analyze how a page evolved over time"""
        logger.info(f"Analyzing page evolution for: {page_title}")
        
        evolution = {
            'title': page_title,
            'creation_date': None,
            'total_edits': 0,
            'size_growth': [],
            'editor_diversity': [],
            'edit_frequency': [],
            'major_changes': []
        }
        
        try:
            # Get full edit history
            edits = self.get_edit_history(page_title, limit=1000)
            
            if edits:
                evolution['total_edits'] = len(edits)
                
                # Find creation date (first edit)
                if edits:
                    evolution['creation_date'] = edits[0]['timestamp']
                
                # Analyze size changes
                sizes = [edit.get('size', 0) for edit in edits if 'size' in edit]
                evolution['size_growth'] = sizes
                
                # Analyze editor diversity over time
                editors = [edit.get('user', 'Anonymous') for edit in edits if 'user' in edit]
                evolution['editor_diversity'] = editors
                
                # Calculate edit frequency
                if len(edits) > 1:
                    timestamps = [datetime.fromisoformat(edit['timestamp'].replace('Z', '+00:00')) 
                                for edit in edits if 'timestamp' in edit]
                    timestamps.sort()
                    
                    # Calculate days between edits
                    edit_intervals = []
                    for i in range(1, len(timestamps)):
                        interval = (timestamps[i] - timestamps[i-1]).days
                        edit_intervals.append(interval)
                    
                    evolution['edit_frequency'] = edit_intervals
                
                # Identify major changes (large size changes)
                for i in range(1, len(sizes)):
                    size_change = sizes[i] - sizes[i-1]
                    if abs(size_change) > 1000:  # Major change threshold
                        evolution['major_changes'].append({
                            'edit_index': i,
                            'size_change': size_change,
                            'timestamp': edits[i]['timestamp'] if 'timestamp' in edits[i] else None
                        })
        
        except Exception as e:
            logger.error(f"Error analyzing page evolution: {e}")
        
        return evolution
    
    def generate_statistics_report(self, sample_size: int = 100) -> Dict:
        """Generate a comprehensive statistics report"""
        logger.info("Generating comprehensive Wikipedia statistics report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_stats': {},
            'content_stats': [],
            'controversial_pages': [],
            'evolution_analysis': [],
            'summary': {}
        }
        
        # Get overall Wikipedia statistics
        report['overall_stats'] = self.get_wikipedia_statistics()
        
        # Get random pages for content analysis
        random_pages = self.get_random_pages(sample_size)
        
        # Analyze content statistics
        for page in random_pages[:min(20, len(random_pages))]:  # Limit to 20 for performance
            content_stats = self.get_page_content_stats(page['title'])
            report['content_stats'].append(content_stats)
            time.sleep(0.1)  # Be respectful to the API
        
        # Find controversial pages
        report['controversial_pages'] = self.find_controversial_pages(limit=10)
        
        # Analyze page evolution for a few sample pages
        sample_titles = [page['title'] for page in random_pages[:5]]
        for title in sample_titles:
            evolution = self.analyze_page_evolution(title)
            report['evolution_analysis'].append(evolution)
            time.sleep(0.1)
        
        # Generate summary statistics
        if report['content_stats']:
            word_counts = [stats['word_count'] for stats in report['content_stats']]
            edit_counts = [stats['edit_count'] for stats in report['content_stats']]
            
            report['summary'] = {
                'avg_words_per_page': np.mean(word_counts),
                'median_words_per_page': np.median(word_counts),
                'avg_edits_per_page': np.mean(edit_counts),
                'median_edits_per_page': np.median(edit_counts),
                'total_pages_analyzed': len(report['content_stats'])
            }
        
        return report
    
    def save_report(self, report: Dict, filename: str = None):
        """Save the analysis report to a file"""
        if filename is None:
            filename = f"wikipedia_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Report saved to {filename}")
        return filename
    
    def create_visualizations(self, report: Dict, output_dir: str = "wikipedia_analysis"):
        """Create visualizations from the analysis report"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Word count distribution
        if report['content_stats']:
            word_counts = [stats['word_count'] for stats in report['content_stats']]
            
            plt.figure(figsize=(12, 8))
            plt.subplot(2, 2, 1)
            plt.hist(word_counts, bins=20, alpha=0.7, edgecolor='black')
            plt.title('Distribution of Words per Page')
            plt.xlabel('Word Count')
            plt.ylabel('Frequency')
            plt.axvline(np.mean(word_counts), color='red', linestyle='--', 
                       label=f'Mean: {np.mean(word_counts):.0f}')
            plt.legend()
            
            # 2. Edit count distribution
            edit_counts = [stats['edit_count'] for stats in report['content_stats']]
            
            plt.subplot(2, 2, 2)
            plt.hist(edit_counts, bins=20, alpha=0.7, edgecolor='black')
            plt.title('Distribution of Edits per Page')
            plt.xlabel('Edit Count')
            plt.ylabel('Frequency')
            plt.axvline(np.mean(edit_counts), color='red', linestyle='--',
                       label=f'Mean: {np.mean(edit_counts):.0f}')
            plt.legend()
            
            # 3. Controversial pages
            if report['controversial_pages']:
                plt.subplot(2, 2, 3)
                titles = [page['title'][:20] + '...' if len(page['title']) > 20 
                         else page['title'] for page in report['controversial_pages'][:10]]
                scores = [page['controversy_score'] for page in report['controversial_pages'][:10]]
                
                plt.barh(range(len(titles)), scores)
                plt.yticks(range(len(titles)), titles)
                plt.title('Top Controversial Pages')
                plt.xlabel('Controversy Score')
            
            # 4. Page evolution example
            if report['evolution_analysis']:
                plt.subplot(2, 2, 4)
                evolution = report['evolution_analysis'][0]
                if evolution['size_growth']:
                    plt.plot(evolution['size_growth'])
                    plt.title(f'Page Size Evolution: {evolution["title"][:20]}...')
                    plt.xlabel('Edit Number')
                    plt.ylabel('Page Size (bytes)')
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/wikipedia_analysis.png", dpi=300, bbox_inches='tight')
            plt.show()
            
            logger.info(f"Visualizations saved to {output_dir}/")

def main():
    """Main function to run the Wikipedia analysis"""
    print("Wikipedia Comprehensive Analysis Tool")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = WikipediaAnalyzer()
    
    # Generate comprehensive report
    print("\n1. Generating comprehensive Wikipedia statistics...")
    report = analyzer.generate_statistics_report(sample_size=50)
    
    # Save report
    print("\n2. Saving report...")
    filename = analyzer.save_report(report)
    
    # Create visualizations
    print("\n3. Creating visualizations...")
    analyzer.create_visualizations(report)
    
    # Print summary
    print("\n4. Analysis Summary:")
    print("-" * 30)
    
    if report['overall_stats']:
        stats = report['overall_stats']
        print(f"Total Wikipedia pages: {stats.get('total_pages', 'N/A'):,}")
        print(f"Total articles: {stats.get('total_articles', 'N/A'):,}")
        print(f"Total edits: {stats.get('total_edits', 'N/A'):,}")
        print(f"Active users: {stats.get('active_users', 'N/A'):,}")
    
    if report['summary']:
        summary = report['summary']
        print(f"\nContent Analysis (based on {summary['total_pages_analyzed']} sample pages):")
        print(f"Average words per page: {summary['avg_words_per_page']:.0f}")
        print(f"Median words per page: {summary['median_words_per_page']:.0f}")
        print(f"Average edits per page: {summary['avg_edits_per_page']:.0f}")
        print(f"Median edits per page: {summary['median_edits_per_page']:.0f}")
    
    if report['controversial_pages']:
        print(f"\nControversial Pages Found: {len(report['controversial_pages'])}")
        for i, page in enumerate(report['controversial_pages'][:5], 1):
            print(f"{i}. {page['title']} (Score: {page['controversy_score']:.1f})")
    
    print(f"\nDetailed report saved to: {filename}")
    print("Visualizations saved to: wikipedia_analysis/")

if __name__ == "__main__":
    main() 