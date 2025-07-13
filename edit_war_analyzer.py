#!/usr/bin/env python3
"""
Wikipedia Edit War Analyzer
===========================

This tool analyzes edit wars on Wikipedia, including:
- Edit war frequency and patterns
- Most contested articles
- Revert analysis and timing
- Editor participation patterns
- 3-revert rule violations
- Behavioral patterns of participants
- Page protection analysis
- Talk page activity correlation
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

class EditWarAnalyzer:
    """Comprehensive edit war analysis tool"""
    
    def __init__(self, language='en'):
        self.language = language
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EditWarAnalyzer/1.0 (Educational Research Project)'
        })
        
        # Edit war detection parameters
        self.revert_threshold = 3  # Minimum reverts to consider it an edit war
        self.time_window_hours = 24  # Time window for edit war detection
        self.min_editors = 2  # Minimum unique editors for edit war
    
    def get_page_revisions(self, page_title: str, limit: int = 1000) -> List[Dict]:
        """Get detailed revision history for a page"""
        logger.info(f"Fetching revisions for: {page_title}")
        
        revisions = []
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'titles': page_title,
            'rvprop': 'timestamp|user|comment|size|tags|revid|parentid',
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
                        revisions = page_data['revisions']
                        logger.info(f"Retrieved {len(revisions)} revisions")
        except Exception as e:
            logger.error(f"Error fetching revisions: {e}")
        
        return revisions
    
    def detect_reverts(self, revisions: List[Dict]) -> List[Dict]:
        """Detect reverts in revision history"""
        reverts = []
        
        for i in range(1, len(revisions)):
            current_rev = revisions[i]
            previous_rev = revisions[i-1]
            
            # Check if this is a revert (size similar to earlier revision)
            if 'size' in current_rev and 'size' in previous_rev:
                size_diff = abs(current_rev['size'] - previous_rev['size'])
                size_ratio = size_diff / max(current_rev['size'], 1)
                
                # Look for size patterns that suggest reverts
                if size_ratio < 0.1:  # Size change less than 10%
                    # Check if comment indicates revert
                    comment = current_rev.get('comment', '').lower()
                    revert_indicators = ['revert', 'undo', 'rv', 'rollback', 'restore']
                    
                    is_revert = any(indicator in comment for indicator in revert_indicators)
                    
                    if is_revert:
                        reverts.append({
                            'timestamp': current_rev['timestamp'],
                            'user': current_rev.get('user', 'Anonymous'),
                            'comment': current_rev.get('comment', ''),
                            'size': current_rev['size'],
                            'revid': current_rev['revid'],
                            'parentid': current_rev.get('parentid'),
                            'reverted_to_size': previous_rev['size']
                        })
        
        return reverts
    
    def detect_edit_wars(self, page_title: str) -> Dict:
        """Detect edit wars on a specific page"""
        logger.info(f"Analyzing edit wars for: {page_title}")
        
        # Get revisions
        revisions = self.get_page_revisions(page_title, limit=1000)
        if not revisions:
            return {}
        
        # Detect reverts
        reverts = self.detect_reverts(revisions)
        
        # Analyze revert patterns
        edit_war_data = {
            'page_title': page_title,
            'total_revisions': len(revisions),
            'total_reverts': len(reverts),
            'revert_rate': len(reverts) / len(revisions) if revisions else 0,
            'edit_wars': [],
            'revert_intervals': [],
            'editor_participation': {},
            'three_revert_violations': []
        }
        
        if len(reverts) >= self.revert_threshold:
            # Group reverts by time windows
            revert_groups = self._group_reverts_by_time(reverts)
            
            for group in revert_groups:
                if len(group) >= self.revert_threshold:
                    # This is an edit war
                    war_data = self._analyze_edit_war_group(group, revisions)
                    edit_war_data['edit_wars'].append(war_data)
        
        # Analyze editor participation
        edit_war_data['editor_participation'] = self._analyze_editor_participation(revisions, reverts)
        
        # Check for 3-revert rule violations
        edit_war_data['three_revert_violations'] = self._detect_three_revert_violations(revisions)
        
        return edit_war_data
    
    def _group_reverts_by_time(self, reverts: List[Dict]) -> List[List[Dict]]:
        """Group reverts that occur within the time window"""
        if not reverts:
            return []
        
        groups = []
        current_group = [reverts[0]]
        
        for i in range(1, len(reverts)):
            current_time = datetime.fromisoformat(reverts[i]['timestamp'].replace('Z', '+00:00'))
            prev_time = datetime.fromisoformat(reverts[i-1]['timestamp'].replace('Z', '+00:00'))
            
            time_diff = (current_time - prev_time).total_seconds() / 3600  # hours
            
            if time_diff <= self.time_window_hours:
                current_group.append(reverts[i])
            else:
                if len(current_group) >= self.revert_threshold:
                    groups.append(current_group)
                current_group = [reverts[i]]
        
        if len(current_group) >= self.revert_threshold:
            groups.append(current_group)
        
        return groups
    
    def _analyze_edit_war_group(self, revert_group: List[Dict], all_revisions: List[Dict]) -> Dict:
        """Analyze a specific edit war group"""
        start_time = datetime.fromisoformat(revert_group[0]['timestamp'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(revert_group[-1]['timestamp'].replace('Z', '+00:00'))
        duration = (end_time - start_time).total_seconds() / 3600  # hours
        
        editors = [revert['user'] for revert in revert_group]
        unique_editors = list(set(editors))
        
        # Calculate revert intervals
        intervals = []
        for i in range(1, len(revert_group)):
            current_time = datetime.fromisoformat(revert_group[i]['timestamp'].replace('Z', '+00:00'))
            prev_time = datetime.fromisoformat(revert_group[i-1]['timestamp'].replace('Z', '+00:00'))
            interval = (current_time - prev_time).total_seconds() / 60  # minutes
            intervals.append(interval)
        
        return {
            'start_time': revert_group[0]['timestamp'],
            'end_time': revert_group[-1]['timestamp'],
            'duration_hours': duration,
            'revert_count': len(revert_group),
            'unique_editors': len(unique_editors),
            'editors': unique_editors,
            'avg_interval_minutes': np.mean(intervals) if intervals else 0,
            'median_interval_minutes': np.median(intervals) if intervals else 0,
            'min_interval_minutes': min(intervals) if intervals else 0,
            'max_interval_minutes': max(intervals) if intervals else 0
        }
    
    def _analyze_editor_participation(self, revisions: List[Dict], reverts: List[Dict]) -> Dict:
        """Analyze editor participation patterns"""
        # Count edits per editor
        editor_edits = Counter()
        editor_reverts = Counter()
        
        for rev in revisions:
            editor = rev.get('user', 'Anonymous')
            editor_edits[editor] += 1
        
        for revert in reverts:
            editor = revert.get('user', 'Anonymous')
            editor_reverts[editor] += 1
        
        # Calculate editor experience (based on edit count)
        total_edits = sum(editor_edits.values())
        editor_experience = {}
        
        for editor, edit_count in editor_edits.items():
            experience_level = 'new' if edit_count < 10 else 'intermediate' if edit_count < 100 else 'veteran'
            editor_experience[editor] = {
                'total_edits': edit_count,
                'reverts': editor_reverts.get(editor, 0),
                'experience_level': experience_level,
                'edit_percentage': (edit_count / total_edits) * 100 if total_edits > 0 else 0
            }
        
        return {
            'total_editors': len(editor_edits),
            'editor_breakdown': editor_experience,
            'new_editors': len([e for e in editor_experience.values() if e['experience_level'] == 'new']),
            'intermediate_editors': len([e for e in editor_experience.values() if e['experience_level'] == 'intermediate']),
            'veteran_editors': len([e for e in editor_experience.values() if e['experience_level'] == 'veteran'])
        }
    
    def _detect_three_revert_violations(self, revisions: List[Dict]) -> List[Dict]:
        """Detect violations of the 3-revert rule"""
        violations = []
        
        # Group revisions by user and check for rapid reverts
        user_revisions = defaultdict(list)
        
        for rev in revisions:
            user = rev.get('user', 'Anonymous')
            user_revisions[user].append(rev)
        
        for user, user_revs in user_revisions.items():
            if len(user_revs) >= 4:  # Need at least 4 edits to have 3 reverts
                # Check for rapid reverts (within 24 hours)
                user_revs.sort(key=lambda x: x['timestamp'])
                
                revert_count = 0
                for i in range(1, len(user_revs)):
                    current_time = datetime.fromisoformat(user_revs[i]['timestamp'].replace('Z', '+00:00'))
                    prev_time = datetime.fromisoformat(user_revs[i-1]['timestamp'].replace('Z', '+00:00'))
                    
                    time_diff = (current_time - prev_time).total_seconds() / 3600
                    
                    # Check if this looks like a revert
                    if 'size' in user_revs[i] and 'size' in user_revs[i-1]:
                        size_diff = abs(user_revs[i]['size'] - user_revs[i-1]['size'])
                        if size_diff < 100:  # Small size change suggests revert
                            revert_count += 1
                    
                    if time_diff <= 24 and revert_count >= 3:
                        violations.append({
                            'user': user,
                            'timestamp': user_revs[i]['timestamp'],
                            'revert_count': revert_count,
                            'time_window_hours': time_diff
                        })
                        break
        
        return violations
    
    def get_page_protection_status(self, page_title: str) -> Dict:
        """Get page protection status"""
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'info',
            'titles': page_title,
            'inprop': 'protection'
        }
        
        try:
            response = self.session.get(self.api_url, params=params)
            data = response.json()
            
            if 'query' in data and 'pages' in data['query']:
                page_id = list(data['query']['pages'].keys())[0]
                if page_id != '-1':
                    page_data = data['query']['pages'][page_id]
                    return {
                        'protected': 'protection' in page_data,
                        'protection_level': page_data.get('protection', []),
                        'page_id': page_id
                    }
        except Exception as e:
            logger.error(f"Error getting protection status: {e}")
        
        return {'protected': False, 'protection_level': [], 'page_id': None}
    
    def get_talk_page_activity(self, page_title: str) -> Dict:
        """Get talk page activity for a page"""
        talk_title = f"Talk:{page_title}"
        
        # Get talk page revisions
        talk_revisions = self.get_page_revisions(talk_title, limit=500)
        
        if not talk_revisions:
            return {'has_talk_page': False, 'activity_level': 'none'}
        
        # Analyze talk page activity
        recent_activity = 0
        for rev in talk_revisions[-10:]:  # Last 10 revisions
            rev_time = datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))
            if (datetime.now().replace(tzinfo=None) - rev_time.replace(tzinfo=None)).days <= 30:
                recent_activity += 1
        
        activity_level = 'high' if recent_activity >= 5 else 'medium' if recent_activity >= 2 else 'low'
        
        return {
            'has_talk_page': True,
            'total_revisions': len(talk_revisions),
            'recent_activity': recent_activity,
            'activity_level': activity_level,
            'last_edit': talk_revisions[-1]['timestamp'] if talk_revisions else None
        }
    
    def find_contested_articles(self, limit: int = 50) -> List[Dict]:
        """Find articles with high edit war potential"""
        logger.info(f"Searching for contested articles...")
        
        contested_articles = []
        
        # Get random pages and analyze them
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'random',
            'rnnamespace': 0,
            'rnlimit': min(limit, 500),
            'rnfilterredir': 'nonredirects'
        }
        
        try:
            response = self.session.get(self.api_url, params=params)
            data = response.json()
            
            if 'query' in data and 'random' in data['query']:
                pages = data['query']['random']
                
                for page in pages:
                    title = page['title']
                    logger.info(f"Analyzing: {title}")
                    
                    # Get edit war data
                    edit_war_data = self.detect_edit_wars(title)
                    
                    if edit_war_data.get('edit_wars'):
                        # Get additional data
                        protection_status = self.get_page_protection_status(title)
                        talk_activity = self.get_talk_page_activity(title)
                        
                        contested_articles.append({
                            'title': title,
                            'edit_wars': edit_war_data['edit_wars'],
                            'total_reverts': edit_war_data['total_reverts'],
                            'revert_rate': edit_war_data['revert_rate'],
                            'editor_participation': edit_war_data['editor_participation'],
                            'three_revert_violations': edit_war_data['three_revert_violations'],
                            'protected': protection_status['protected'],
                            'talk_activity': talk_activity
                        })
                    
                    time.sleep(0.1)  # Be respectful to the API
        
        except Exception as e:
            logger.error(f"Error finding contested articles: {e}")
        
        # Sort by revert rate
        contested_articles.sort(key=lambda x: x['revert_rate'], reverse=True)
        return contested_articles
    
    def generate_edit_war_report(self, sample_size: int = 100) -> Dict:
        """Generate comprehensive edit war analysis report"""
        logger.info("Generating edit war analysis report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_parameters': {
                'revert_threshold': self.revert_threshold,
                'time_window_hours': self.time_window_hours,
                'min_editors': self.min_editors
            },
            'contested_articles': [],
            'overall_statistics': {},
            'editor_behavior_patterns': {},
            'protection_analysis': {},
            'talk_page_correlation': {}
        }
        
        # Find contested articles
        contested_articles = self.find_contested_articles(sample_size)
        report['contested_articles'] = contested_articles
        
        # Calculate overall statistics
        if contested_articles:
            total_edit_wars = sum(len(article['edit_wars']) for article in contested_articles)
            total_reverts = sum(article['total_reverts'] for article in contested_articles)
            total_violations = sum(len(article['three_revert_violations']) for article in contested_articles)
            
            # Editor behavior analysis
            all_editors = []
            for article in contested_articles:
                for war in article['edit_wars']:
                    all_editors.extend(war['editors'])
            
            editor_counts = Counter(all_editors)
            
            # Protection analysis
            protected_count = sum(1 for article in contested_articles if article['protected'])
            
            # Talk page correlation
            talk_active_count = sum(1 for article in contested_articles 
                                  if article['talk_activity']['activity_level'] in ['high', 'medium'])
            
            report['overall_statistics'] = {
                'articles_analyzed': len(contested_articles),
                'articles_with_edit_wars': len([a for a in contested_articles if a['edit_wars']]),
                'total_edit_wars': total_edit_wars,
                'total_reverts': total_reverts,
                'total_three_revert_violations': total_violations,
                'avg_reverts_per_article': total_reverts / len(contested_articles) if contested_articles else 0,
                'avg_edit_wars_per_article': total_edit_wars / len(contested_articles) if contested_articles else 0
            }
            
            report['editor_behavior_patterns'] = {
                'total_unique_editors': len(editor_counts),
                'most_active_editors': dict(editor_counts.most_common(10)),
                'editor_participation_distribution': {
                    'single_war': len([e for e in editor_counts.values() if e == 1]),
                    'multiple_wars': len([e for e in editor_counts.values() if e > 1])
                }
            }
            
            report['protection_analysis'] = {
                'protected_articles': protected_count,
                'protection_rate': (protected_count / len(contested_articles)) * 100 if contested_articles else 0
            }
            
            report['talk_page_correlation'] = {
                'articles_with_talk_activity': talk_active_count,
                'talk_activity_rate': (talk_active_count / len(contested_articles)) * 100 if contested_articles else 0
            }
        
        return report
    
    def save_report(self, report: Dict, filename: str = None):
        """Save the edit war analysis report"""
        if filename is None:
            filename = f"edit_war_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Edit war report saved to {filename}")
        return filename
    
    def create_visualizations(self, report: Dict, output_dir: str = "edit_war_analysis"):
        """Create visualizations for edit war analysis"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if not report['contested_articles']:
            logger.warning("No contested articles found for visualization")
            return
        
        # Set up plotting
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # 1. Revert rate distribution
        revert_rates = [article['revert_rate'] for article in report['contested_articles']]
        axes[0, 0].hist(revert_rates, bins=20, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Distribution of Revert Rates')
        axes[0, 0].set_xlabel('Revert Rate')
        axes[0, 0].set_ylabel('Number of Articles')
        
        # 2. Edit war duration
        durations = []
        for article in report['contested_articles']:
            for war in article['edit_wars']:
                durations.append(war['duration_hours'])
        
        if durations:
            axes[0, 1].hist(durations, bins=20, alpha=0.7, edgecolor='black')
            axes[0, 1].set_title('Edit War Duration Distribution')
            axes[0, 1].set_xlabel('Duration (hours)')
            axes[0, 1].set_ylabel('Number of Edit Wars')
        
        # 3. Editor participation
        editor_counts = [len(war['editors']) for article in report['contested_articles'] 
                        for war in article['edit_wars']]
        if editor_counts:
            axes[0, 2].hist(editor_counts, bins=range(min(editor_counts), max(editor_counts) + 2), 
                           alpha=0.7, edgecolor='black')
            axes[0, 2].set_title('Editor Participation in Edit Wars')
            axes[0, 2].set_xlabel('Number of Unique Editors')
            axes[0, 2].set_ylabel('Number of Edit Wars')
        
        # 4. Revert intervals
        intervals = []
        for article in report['contested_articles']:
            for war in article['edit_wars']:
                intervals.append(war['avg_interval_minutes'])
        
        if intervals:
            axes[1, 0].hist(intervals, bins=20, alpha=0.7, edgecolor='black')
            axes[1, 0].set_title('Average Revert Intervals')
            axes[1, 0].set_xlabel('Interval (minutes)')
            axes[1, 0].set_ylabel('Number of Edit Wars')
        
        # 5. Protection status
        protected_count = sum(1 for article in report['contested_articles'] if article['protected'])
        unprotected_count = len(report['contested_articles']) - protected_count
        
        axes[1, 1].pie([protected_count, unprotected_count], 
                      labels=['Protected', 'Unprotected'], 
                      autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('Page Protection Status')
        
        # 6. Talk page activity
        talk_levels = [article['talk_activity']['activity_level'] 
                      for article in report['contested_articles']]
        talk_counts = Counter(talk_levels)
        
        if talk_counts:
            axes[1, 2].bar(talk_counts.keys(), talk_counts.values(), alpha=0.7)
            axes[1, 2].set_title('Talk Page Activity Levels')
            axes[1, 2].set_xlabel('Activity Level')
            axes[1, 2].set_ylabel('Number of Articles')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/edit_war_analysis.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"Edit war visualizations saved to {output_dir}/")

def main():
    """Main function to run edit war analysis"""
    print("Wikipedia Edit War Analysis Tool")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = EditWarAnalyzer()
    
    # Generate comprehensive report
    print("\n1. Analyzing edit wars...")
    report = analyzer.generate_edit_war_report(sample_size=50)
    
    # Save report
    print("\n2. Saving report...")
    filename = analyzer.save_report(report)
    
    # Create visualizations
    print("\n3. Creating visualizations...")
    analyzer.create_visualizations(report)
    
    # Print summary
    print("\n4. Edit War Analysis Summary:")
    print("-" * 30)
    
    if report['overall_statistics']:
        stats = report['overall_statistics']
        print(f"Articles analyzed: {stats['articles_analyzed']}")
        print(f"Articles with edit wars: {stats['articles_with_edit_wars']}")
        print(f"Total edit wars found: {stats['total_edit_wars']}")
        print(f"Total reverts: {stats['total_reverts']}")
        print(f"Three-revert violations: {stats['total_three_revert_violations']}")
        print(f"Average reverts per article: {stats['avg_reverts_per_article']:.2f}")
    
    if report['protection_analysis']:
        protection = report['protection_analysis']
        print(f"\nProtection Analysis:")
        print(f"Protected articles: {protection['protected_articles']}")
        print(f"Protection rate: {protection['protection_rate']:.1f}%")
    
    if report['talk_page_correlation']:
        talk = report['talk_page_correlation']
        print(f"\nTalk Page Correlation:")
        print(f"Articles with talk activity: {talk['articles_with_talk_activity']}")
        print(f"Talk activity rate: {talk['talk_activity_rate']:.1f}%")
    
    print(f"\nDetailed report saved to: {filename}")
    print("Visualizations saved to: edit_war_analysis/")

if __name__ == "__main__":
    main() 