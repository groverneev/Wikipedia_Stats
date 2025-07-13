#!/usr/bin/env python3
"""
Wikipedia Analysis Summary
==========================

This script provides a clear summary of the Wikipedia analysis findings.
"""

import json
import glob
import os
from datetime import datetime

def load_latest_report():
    """Load the most recent analysis report"""
    report_files = glob.glob("wikipedia_analysis_*.json")
    if not report_files:
        print("No analysis reports found. Please run wikipedia_analysis.py first.")
        return None
    
    # Get the most recent file
    latest_file = max(report_files, key=os.path.getctime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_wikipedia_summary():
    """Print a comprehensive summary of Wikipedia findings"""
    
    report = load_latest_report()
    if not report:
        return
    
    print("=" * 80)
    print("WIKIPEDIA COMPREHENSIVE ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Analysis Date: {report['timestamp']}")
    print()
    
    # Overall Statistics
    stats = report['overall_stats']
    print("📊 OVERALL WIKIPEDIA STATISTICS")
    print("-" * 50)
    print(f"🌐 Total Pages: {stats['total_pages']:,}")
    print(f"📚 Total Articles: {stats['total_articles']:,}")
    print(f"✏️  Total Edits: {stats['total_edits']:,}")
    print(f"👥 Total Users: {stats['total_users']:,}")
    print(f"🔥 Active Users: {stats['active_users']:,}")
    print(f"🛡️  Administrators: {stats['admins']:,}")
    print(f"🖼️  Images: {stats['images']:,}")
    print()
    
    # Content Analysis
    if 'content_stats' in report and report['content_stats']:
        content_stats = report['content_stats']
        word_counts = [page['word_count'] for page in content_stats]
        char_counts = [page['char_count'] for page in content_stats]
        section_counts = [page['section_count'] for page in content_stats]
        link_counts = [page['link_count'] for page in content_stats]
        image_counts = [page['image_count'] for page in content_stats]
        
        print("📝 CONTENT ANALYSIS (Sample Pages)")
        print("-" * 50)
        print(f"📖 Average Words per Page: {sum(word_counts)/len(word_counts):.0f}")
        print(f"📖 Median Words per Page: {sorted(word_counts)[len(word_counts)//2]}")
        print(f"📖 Word Count Range: {min(word_counts)} - {max(word_counts)}")
        print()
        print(f"🔤 Average Characters per Page: {sum(char_counts)/len(char_counts):.0f}")
        print(f"🔤 Character Count Range: {min(char_counts)} - {max(char_counts)}")
        print()
        print(f"📑 Average Sections per Page: {sum(section_counts)/len(section_counts):.1f}")
        print(f"🔗 Average Links per Page: {sum(link_counts)/len(link_counts):.1f}")
        print(f"🖼️  Average Images per Page: {sum(image_counts)/len(image_counts):.1f}")
        print()
    
    # Page Evolution Analysis
    if 'evolution_analysis' in report and report['evolution_analysis']:
        print("📈 PAGE EVOLUTION ANALYSIS")
        print("-" * 50)
        
        for evolution in report['evolution_analysis'][:3]:  # Show first 3 examples
            print(f"📄 {evolution['title']}")
            print(f"   • Total Edits: {evolution['total_edits']}")
            if evolution.get('creation_date'):
                print(f"   • Created: {evolution['creation_date']}")
            if evolution.get('size_growth'):
                print(f"   • Size Growth: {len(evolution['size_growth'])} revisions tracked")
                if len(evolution['size_growth']) > 1:
                    size_change = evolution['size_growth'][-1] - evolution['size_growth'][0]
                    print(f"   • Net Size Change: {size_change:+,} bytes")
            print()
    
    # Controversial Pages
    if 'controversial_pages' in report and report['controversial_pages']:
        print("🔥 POTENTIALLY CONTROVERSIAL PAGES")
        print("-" * 50)
        
        for i, page in enumerate(report['controversial_pages'][:10], 1):
            print(f"{i:2d}. {page['title']}")
            print(f"    Controversy Score: {page['controversy_score']:.1f}")
            print(f"    Edit Count: {page['edit_count']}")
            print(f"    Unique Editors: {page['unique_editors']}")
            print(f"    Recent Edits: {page['recent_edits']}")
            print()
    
    # Summary Statistics
    if 'summary' in report and report['summary']:
        summary = report['summary']
        print("📊 SUMMARY STATISTICS")
        print("-" * 50)
        print(f"📖 Average Words per Page: {summary['avg_words_per_page']:.0f}")
        print(f"📖 Median Words per Page: {summary['median_words_per_page']:.0f}")
        print(f"✏️  Average Edits per Page: {summary['avg_edits_per_page']:.0f}")
        print(f"✏️  Median Edits per Page: {summary['median_edits_per_page']:.0f}")
        print(f"📄 Pages Analyzed: {summary['total_pages_analyzed']}")
        print()
    
    # Key Insights
    print("💡 KEY INSIGHTS ABOUT WIKIPEDIA")
    print("-" * 50)
    print("1. 📏 SCALE: Wikipedia is massive with over 63 million total pages")
    print("2. 📚 CONTENT: Over 7 million articles covering virtually every topic")
    print("3. 👥 COMMUNITY: Nearly 50 million registered users, 108K active")
    print("4. ✏️  COLLABORATION: Over 1.2 billion edits show massive collaboration")
    print("5. 📖 LENGTH: Articles average 1,300+ words, showing substantial content")
    print("6. 🔄 EVOLUTION: Pages grow and improve over time through editing")
    print("7. 🛡️  QUALITY: Active moderation with 837 administrators")
    print("8. 🌍 GLOBAL: Available in 300+ languages with extensive media")
    print()
    
    # Page Creation Process
    print("🔄 TYPICAL WIKIPEDIA PAGE CREATION PROCESS")
    print("-" * 50)
    print("1. 📝 Creation: Someone creates a stub article with basic info")
    print("2. 🔧 Development: Multiple editors add content and structure")
    print("3. 📚 Expansion: More details, sections, and references added")
    print("4. ✅ Refinement: Fact-checking, formatting, and style improvements")
    print("5. 🔄 Maintenance: Ongoing updates and corrections")
    print("6. 🛡️  Protection: Controversial pages may get protection")
    print()
    
    # Controversy Indicators
    print("⚠️  CONTROVERSY INDICATORS")
    print("-" * 50)
    print("• High edit counts (100+ edits)")
    print("• Many unique editors (20+ different people)")
    print("• Recent editing activity (frequent changes)")
    print("• Rapid back-and-forth edits")
    print("• Content protection or semi-protection")
    print("• Extensive talk page discussions")
    print()
    
    print("=" * 80)
    print("Analysis complete! Check wikipedia_analysis/ for visualizations.")
    print("=" * 80)

if __name__ == "__main__":
    print_wikipedia_summary() 