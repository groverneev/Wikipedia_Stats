#!/usr/bin/env python3
"""
Quick Edit War Statistics
=========================

This script provides quick insights into Wikipedia edit wars:
- Edit war frequency
- Most contested articles
- Revert patterns
- Editor behavior
- 3-revert rule violations
"""

import requests
import json
import time
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re

def get_page_revisions_quick(page_title: str, limit: int = 200):
    """Get recent revisions for a page"""
    api_url = "https://en.wikipedia.org/w/api.php"
    
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'revisions',
        'titles': page_title,
        'rvprop': 'timestamp|user|comment|size',
        'rvlimit': min(limit, 500),
        'rvdir': 'newer'
    }
    
    try:
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if 'query' in data and 'pages' in data['query']:
            page_id = list(data['query']['pages'].keys())[0]
            if page_id != '-1':
                page_data = data['query']['pages'][page_id]
                if 'revisions' in page_data:
                    return page_data['revisions']
    except Exception as e:
        print(f"Error fetching revisions for {page_title}: {e}")
    
    return []

def detect_reverts_quick(revisions):
    """Quick revert detection"""
    reverts = []
    
    for i in range(1, len(revisions)):
        current_rev = revisions[i]
        previous_rev = revisions[i-1]
        
        # Check for revert indicators in comment
        comment = current_rev.get('comment', '').lower()
        revert_indicators = ['revert', 'undo', 'rv', 'rollback', 'restore', 'reverted']
        
        if any(indicator in comment for indicator in revert_indicators):
            reverts.append({
                'timestamp': current_rev['timestamp'],
                'user': current_rev.get('user', 'Anonymous'),
                'comment': current_rev.get('comment', ''),
                'size': current_rev.get('size', 0)
            })
    
    return reverts

def analyze_edit_war_patterns_quick(page_title: str):
    """Quick edit war analysis for a single page"""
    print(f"Analyzing: {page_title}")
    
    revisions = get_page_revisions_quick(page_title, limit=200)
    if not revisions:
        return None
    
    reverts = detect_reverts_quick(revisions)
    
    if len(reverts) < 3:
        return None
    
    # Analyze revert patterns
    revert_times = [datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')) for r in reverts]
    revert_users = [r['user'] for r in reverts]
    
    # Group reverts by time windows (24 hours)
    revert_groups = []
    current_group = [reverts[0]]
    
    for i in range(1, len(reverts)):
        time_diff = (revert_times[i] - revert_times[i-1]).total_seconds() / 3600
        if time_diff <= 24:
            current_group.append(reverts[i])
        else:
            if len(current_group) >= 3:
                revert_groups.append(current_group)
            current_group = [reverts[i]]
    
    if len(current_group) >= 3:
        revert_groups.append(current_group)
    
    if not revert_groups:
        return None
    
    # Analyze each edit war group
    edit_wars = []
    for group in revert_groups:
        start_time = datetime.fromisoformat(group[0]['timestamp'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(group[-1]['timestamp'].replace('Z', '+00:00'))
        duration = (end_time - start_time).total_seconds() / 3600
        
        users = list(set([r['user'] for r in group]))
        
        # Calculate intervals
        intervals = []
        for i in range(1, len(group)):
            current_time = datetime.fromisoformat(group[i]['timestamp'].replace('Z', '+00:00'))
            prev_time = datetime.fromisoformat(group[i-1]['timestamp'].replace('Z', '+00:00'))
            interval = (current_time - prev_time).total_seconds() / 60
            intervals.append(interval)
        
        edit_wars.append({
            'revert_count': len(group),
            'duration_hours': duration,
            'unique_editors': len(users),
            'editors': users,
            'avg_interval_minutes': sum(intervals) / len(intervals) if intervals else 0,
            'start_time': group[0]['timestamp'],
            'end_time': group[-1]['timestamp']
        })
    
    return {
        'title': page_title,
        'total_revisions': len(revisions),
        'total_reverts': len(reverts),
        'revert_rate': len(reverts) / len(revisions),
        'edit_wars': edit_wars,
        'unique_editors': len(set(revert_users))
    }

def find_contested_articles_quick(limit: int = 30):
    """Find articles with potential edit wars"""
    print(f"Searching for contested articles...")
    
    api_url = "https://en.wikipedia.org/w/api.php"
    contested_articles = []
    
    # Get random pages
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'random',
        'rnnamespace': 0,
        'rnlimit': min(limit, 500),
        'rnfilterredir': 'nonredirects'
    }
    
    try:
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if 'query' in data and 'random' in data['query']:
            pages = data['query']['random']
            
            for page in pages:
                title = page['title']
                analysis = analyze_edit_war_patterns_quick(title)
                
                if analysis and analysis['edit_wars']:
                    contested_articles.append(analysis)
                
                time.sleep(0.1)  # Be respectful to the API
                
                if len(contested_articles) >= 10:  # Limit to 10 for quick analysis
                    break
    
    except Exception as e:
        print(f"Error finding contested articles: {e}")
    
    # Sort by revert rate
    contested_articles.sort(key=lambda x: x['revert_rate'], reverse=True)
    return contested_articles

def analyze_editor_behavior_quick(contested_articles):
    """Quick analysis of editor behavior patterns"""
    all_editors = []
    editor_reverts = Counter()
    
    for article in contested_articles:
        for war in article['edit_wars']:
            all_editors.extend(war['editors'])
            for editor in war['editors']:
                editor_reverts[editor] += 1
    
    # Analyze editor experience (simplified)
    editor_counts = Counter(all_editors)
    
    new_editors = len([e for e in editor_counts.values() if e == 1])
    repeat_editors = len([e for e in editor_counts.values() if e > 1])
    
    return {
        'total_unique_editors': len(editor_counts),
        'new_editors': new_editors,
        'repeat_editors': repeat_editors,
        'most_active_editors': dict(editor_counts.most_common(5)),
        'editor_revert_counts': dict(editor_reverts.most_common(5))
    }

def detect_three_revert_violations_quick(contested_articles):
    """Quick detection of 3-revert rule violations"""
    violations = []
    
    for article in contested_articles:
        for war in article['edit_wars']:
            # Check if any editor made 3+ reverts in 24 hours
            editor_revert_counts = Counter(war['editors'])
            for editor, count in editor_revert_counts.items():
                if count >= 3:
                    violations.append({
                        'article': article['title'],
                        'editor': editor,
                        'revert_count': count,
                        'time_window': war['duration_hours']
                    })
    
    return violations

def main():
    """Main function for quick edit war analysis"""
    print("Quick Wikipedia Edit War Analysis")
    print("=" * 50)
    
    # Find contested articles
    contested_articles = find_contested_articles_quick(limit=30)
    
    if not contested_articles:
        print("No edit wars found in the sample.")
        return
    
    print(f"\n=== EDIT WAR ANALYSIS SUMMARY ===")
    print(f"Articles analyzed: 30")
    print(f"Articles with edit wars: {len(contested_articles)}")
    print(f"Edit war frequency: {(len(contested_articles) / 30) * 100:.1f}%")
    
    # Overall statistics
    total_edit_wars = sum(len(article['edit_wars']) for article in contested_articles)
    total_reverts = sum(article['total_reverts'] for article in contested_articles)
    
    print(f"\nTotal edit wars found: {total_edit_wars}")
    print(f"Total reverts: {total_reverts}")
    print(f"Average reverts per article: {total_reverts / len(contested_articles):.1f}")
    
    # Most contested articles
    print(f"\n=== MOST CONTESTED ARTICLES ===")
    for i, article in enumerate(contested_articles[:5], 1):
        print(f"{i}. {article['title']}")
        print(f"   Revert rate: {article['revert_rate']:.3f}")
        print(f"   Total reverts: {article['total_reverts']}")
        print(f"   Edit wars: {len(article['edit_wars'])}")
        print(f"   Unique editors: {article['unique_editors']}")
    
    # Edit war characteristics
    print(f"\n=== EDIT WAR CHARACTERISTICS ===")
    all_durations = []
    all_intervals = []
    all_editor_counts = []
    
    for article in contested_articles:
        for war in article['edit_wars']:
            all_durations.append(war['duration_hours'])
            all_intervals.append(war['avg_interval_minutes'])
            all_editor_counts.append(war['unique_editors'])
    
    if all_durations:
        print(f"Average edit war duration: {sum(all_durations) / len(all_durations):.1f} hours")
        print(f"Median edit war duration: {sorted(all_durations)[len(all_durations)//2]:.1f} hours")
    
    if all_intervals:
        print(f"Average revert interval: {sum(all_intervals) / len(all_intervals):.1f} minutes")
        print(f"Median revert interval: {sorted(all_intervals)[len(all_intervals)//2]:.1f} minutes")
    
    if all_editor_counts:
        print(f"Average editors per edit war: {sum(all_editor_counts) / len(all_editor_counts):.1f}")
        print(f"Median editors per edit war: {sorted(all_editor_counts)[len(all_editor_counts)//2]}")
    
    # Editor behavior analysis
    print(f"\n=== EDITOR BEHAVIOR PATTERNS ===")
    editor_behavior = analyze_editor_behavior_quick(contested_articles)
    
    print(f"Total unique editors: {editor_behavior['total_unique_editors']}")
    print(f"New editors (single edit war): {editor_behavior['new_editors']}")
    print(f"Repeat editors (multiple edit wars): {editor_behavior['repeat_editors']}")
    
    print(f"\nMost active editors:")
    for editor, count in editor_behavior['most_active_editors'].items():
        print(f"  {editor}: {count} edit wars")
    
    # 3-revert rule violations
    print(f"\n=== THREE-REVERT RULE VIOLATIONS ===")
    violations = detect_three_revert_violations_quick(contested_articles)
    
    if violations:
        print(f"Found {len(violations)} potential violations:")
        for violation in violations[:5]:
            print(f"  {violation['editor']} on {violation['article']}: {violation['revert_count']} reverts")
    else:
        print("No clear 3-revert rule violations detected in this sample.")
    
    # Detailed edit war examples
    print(f"\n=== DETAILED EDIT WAR EXAMPLES ===")
    for i, article in enumerate(contested_articles[:3], 1):
        print(f"\n{i}. {article['title']}")
        for j, war in enumerate(article['edit_wars'], 1):
            print(f"   Edit war {j}:")
            print(f"     Duration: {war['duration_hours']:.1f} hours")
            print(f"     Reverts: {war['revert_count']}")
            print(f"     Editors: {', '.join(war['editors'])}")
            print(f"     Avg interval: {war['avg_interval_minutes']:.1f} minutes")
    
    print(f"\n" + "=" * 50)
    print("Quick analysis complete!")
    print("For detailed analysis, run: python edit_war_analyzer.py")

if __name__ == "__main__":
    main() 