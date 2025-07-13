# Wikipedia Comprehensive Analysis Tool

This project provides tools to analyze various aspects of Wikipedia, including page statistics, content analysis, edit patterns, and controversial page identification.

## What This Tool Analyzes

### 1. Basic Wikipedia Statistics
- **Total number of pages**: How many pages exist on Wikipedia
- **Total articles**: Number of actual articles (excluding talk pages, user pages, etc.)
- **Total edits**: Cumulative number of edits across all pages
- **User statistics**: Total users, active users, administrators
- **Media**: Number of images and other media files

### 2. Content Analysis
- **Words per page**: Average, median, and distribution of word counts
- **Page structure**: Number of sections, links, images per page
- **Content quality indicators**: Reference counts, external links

### 3. Edit Patterns and Page Evolution
- **Edit frequency**: How often pages are edited
- **Page growth**: How page size changes over time
- **Editor diversity**: How many different people edit each page
- **Major changes**: Identification of significant content additions/removals

### 4. Controversial Page Analysis
- **Controversy indicators**: High edit counts, frequent recent edits, diverse editors
- **Controversy scoring**: Algorithm to identify potentially controversial topics
- **Edit war detection**: Pages with rapid back-and-forth edits

## Files in This Project

### `quick_wikipedia_stats.py`
A lightweight script that provides immediate answers to basic Wikipedia questions:
- How many pages are there?
- Average words per page
- Basic statistics
- Quick controversial page identification

**Usage:**
```bash
python quick_wikipedia_stats.py
```

### `wikipedia_analysis.py`
A comprehensive analysis tool that provides detailed insights:
- Full statistical analysis
- Page evolution tracking
- Detailed controversial page analysis
- Data visualization
- JSON report generation

**Usage:**
```bash
python wikipedia_analysis.py
```

### `requirements.txt`
Python dependencies needed to run the analysis tools.

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the quick analysis:**
```bash
python quick_wikipedia_stats.py
```

3. **For detailed analysis:**
```bash
python wikipedia_analysis.py
```

## What You'll Learn About Wikipedia

### Page Statistics
- **Total pages**: Currently over 6 million pages on English Wikipedia
- **Articles**: Approximately 6.7 million articles
- **Edits**: Over 1 billion total edits
- **Active users**: Around 120,000 active editors

### Content Patterns
- **Average words per page**: Typically 500-1000 words for most articles
- **Edit patterns**: Most pages have 10-50 edits, but some have thousands
- **Page evolution**: Articles typically start small and grow over time
- **Editor participation**: Most articles have 5-20 different editors

### Controversial Topics
Common controversial Wikipedia pages include:
- Political figures and events
- Religious topics
- Scientific controversies
- Current events
- Biographical articles of living people

## Key Insights About Wikipedia

### 1. Scale and Growth
- Wikipedia is massive: over 6 million articles in English alone
- Constant growth: thousands of new articles created daily
- Global reach: available in over 300 languages

### 2. Content Quality
- **Collaborative editing**: Multiple editors improve content quality
- **Citation requirements**: Articles need reliable sources
- **Neutral point of view**: Content must be balanced
- **Verifiability**: Information must be verifiable

### 3. Edit Dynamics
- **Edit wars**: Rapid back-and-forth edits on controversial topics
- **Vandalism**: Deliberate misinformation (quickly reverted)
- **Stable articles**: Most articles reach a stable state after initial development
- **Expert contributions**: Subject matter experts often contribute to their fields

### 4. Controversy Patterns
- **High-edit pages**: Often indicate controversy or importance
- **Recent activity**: Current events drive rapid editing
- **Editor diversity**: Controversial topics attract more diverse editors
- **Protection levels**: Highly controversial pages may be protected from editing

## Understanding Page Creation and Evolution

### Typical Page Lifecycle
1. **Creation**: Someone creates a stub article
2. **Initial development**: Basic information added
3. **Expansion**: More details, sections, and references added
4. **Refinement**: Fact-checking, formatting, and style improvements
5. **Maintenance**: Ongoing updates and corrections

### Edit Patterns
- **Early stages**: Many small edits as content is developed
- **Mature articles**: Fewer, larger edits for major updates
- **Controversial topics**: Frequent edits from multiple perspectives
- **Stable articles**: Occasional maintenance edits

## Research Applications

This tool can be used for:
- **Academic research**: Studying collaborative knowledge creation
- **Content analysis**: Understanding information patterns
- **Social media research**: Analyzing online collaboration
- **Education**: Teaching about information literacy and source evaluation
- **Data science**: Large-scale text and network analysis

## API Usage and Ethics

- **Respectful usage**: The tool includes delays to avoid overwhelming Wikipedia's servers
- **Educational purpose**: Designed for research and learning
- **Data attribution**: All data comes from Wikipedia's public API
- **Privacy**: Only analyzes publicly available information

## Limitations

- **API rate limits**: Wikipedia has usage limits to prevent server overload
- **Sample size**: Full analysis of all pages would take months
- **Controversy detection**: Algorithm-based identification has limitations
- **Language**: Currently focused on English Wikipedia

## Future Enhancements

Potential improvements could include:
- Multi-language analysis
- Historical trend analysis
- Network analysis of editor relationships
- Content quality scoring
- Real-time monitoring of controversial topics

## Contributing

This is an educational research tool. Feel free to:
- Modify the analysis parameters
- Add new metrics
- Improve the controversy detection algorithm
- Extend to other Wikimedia projects

## License

This project is for educational and research purposes. Please respect Wikipedia's terms of service and API usage guidelines. 