#!/usr/bin/env python3
"""
Wikipedia Edit War Visualizations
=================================

Advanced visualizations for edit war analysis:
- Heatmap of revert frequency over time per page
- Network graph of editor interactions
- Timeline of edit war escalations and resolutions
"""

import requests
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import re
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EditWarVisualizer:
    """Advanced visualization tool for edit war analysis"""
    
    def __init__(self, language='en'):
        self.language = language
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EditWarVisualizer/1.0 (Educational Research Project)'
        })
        
        # Known controversial pages for analysis
        self.controversial_pages = [
            "Donald Trump", "Barack Obama", "Israel", "Palestine", 
            "Climate change", "Vaccine", "COVID-19", "Evolution", 
            "Creationism", "Abortion", "Gun control", "Brexit", 
            "Vladimir Putin", "China", "Russia"
        ]
    
    def get_page_revisions(self, page_title: str, limit: int = 1000):
        """Get detailed page revisions"""
        logger.info(f"Fetching revisions for: {page_title}")
        
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
                        return page_data['revisions']
        except Exception as e:
            logger.error(f"Error fetching revisions for {page_title}: {e}")
        
        return []
    
    def detect_reverts(self, revisions):
        """Detect reverts in revision history"""
        reverts = []
        
        for i in range(1, len(revisions)):
            current_rev = revisions[i]
            previous_rev = revisions[i-1]
            
            # Check for revert indicators
            comment = current_rev.get('comment', '').lower()
            revert_indicators = ['revert', 'undo', 'rv', 'rollback', 'restore', 'reverted']
            
            if any(indicator in comment for indicator in revert_indicators):
                reverts.append({
                    'timestamp': current_rev['timestamp'],
                    'user': current_rev.get('user', 'Anonymous'),
                    'comment': current_rev.get('comment', ''),
                    'size': current_rev.get('size', 0),
                    'revid': current_rev.get('revid'),
                    'parentid': current_rev.get('parentid')
                })
        
        return reverts
    
    def create_revert_heatmap(self, page_title: str, output_dir: str = "edit_war_visualizations"):
        """Create heatmap of revert frequency over time"""
        logger.info(f"Creating revert heatmap for: {page_title}")
        
        revisions = self.get_page_revisions(page_title, limit=1000)
        if not revisions:
            return None
        
        reverts = self.detect_reverts(revisions)
        if len(reverts) < 3:
            return None
        
        # Convert timestamps to datetime objects
        revert_times = [datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')) for r in reverts]
        
        # Create time bins (daily)
        start_date = min(revert_times).date()
        end_date = max(revert_times).date()
        date_range = pd.date_range(start_date, end_date, freq='D')
        
        # Count reverts per day
        revert_counts = Counter([rt.date() for rt in revert_times])
        
        # Create heatmap data
        heatmap_data = []
        for date in date_range:
            count = revert_counts.get(date.date(), 0)
            heatmap_data.append({
                'date': date,
                'revert_count': count,
                'day_of_week': date.strftime('%A'),
                'week': date.isocalendar()[1]
            })
        
        df = pd.DataFrame(heatmap_data)
        
        # Create heatmap using plotly
        fig = go.Figure()
        
        # Pivot data for heatmap
        pivot_data = df.pivot_table(
            values='revert_count', 
            index='day_of_week', 
            columns='week', 
            fill_value=0
        )
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data = pivot_data.reindex(day_order)
        
        fig.add_trace(go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Revert Count")
        ))
        
        fig.update_layout(
            title=f"Revert Frequency Heatmap: {page_title}",
            xaxis_title="Week of Year",
            yaxis_title="Day of Week",
            height=500
        )
        
        # Save the plot
        import os
        os.makedirs(output_dir, exist_ok=True)
        fig.write_html(f"{output_dir}/revert_heatmap_{page_title.replace(' ', '_')}.html")
        fig.write_image(f"{output_dir}/revert_heatmap_{page_title.replace(' ', '_')}.png")
        
        logger.info(f"Revert heatmap saved for {page_title}")
        return fig
    
    def create_editor_network(self, page_title: str, output_dir: str = "edit_war_visualizations"):
        """Create network graph of editor interactions"""
        logger.info(f"Creating editor network for: {page_title}")
        
        revisions = self.get_page_revisions(page_title, limit=1000)
        if not revisions:
            return None
        
        reverts = self.detect_reverts(revisions)
        if len(reverts) < 3:
            return None
        
        # Create network graph
        G = nx.Graph()
        
        # Add nodes (editors)
        editors = set()
        for revert in reverts:
            editors.add(revert['user'])
        
        G.add_nodes_from(editors)
        
        # Add edges (interactions)
        for i in range(len(reverts) - 1):
            current_editor = reverts[i]['user']
            next_editor = reverts[i + 1]['user']
            
            if current_editor != next_editor:
                if G.has_edge(current_editor, next_editor):
                    G[current_editor][next_editor]['weight'] += 1
                else:
                    G.add_edge(current_editor, next_editor, weight=1)
        
        if len(G.edges()) == 0:
            return None
        
        # Calculate node sizes based on edit count
        editor_counts = Counter([r['user'] for r in reverts])
        node_sizes = [editor_counts.get(node, 1) * 100 for node in G.nodes()]
        
        # Calculate edge weights
        edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
        
        # Create network visualization using plotly
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Node positions
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        # Edge positions
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create the network plot
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='gray'),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=list(G.nodes()),
            textposition="middle center",
            marker=dict(
                size=node_sizes,
                color='lightblue',
                line=dict(width=2, color='darkblue')
            ),
            showlegend=False
        ))
        
        fig.update_layout(
            title=f"Editor Interaction Network: {page_title}",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )
        
        # Save the plot
        import os
        os.makedirs(output_dir, exist_ok=True)
        fig.write_html(f"{output_dir}/editor_network_{page_title.replace(' ', '_')}.html")
        fig.write_image(f"{output_dir}/editor_network_{page_title.replace(' ', '_')}.png")
        
        logger.info(f"Editor network saved for {page_title}")
        return fig
    
    def create_edit_war_timeline(self, page_title: str, output_dir: str = "edit_war_visualizations"):
        """Create timeline of edit war escalations and resolutions"""
        logger.info(f"Creating edit war timeline for: {page_title}")
        
        revisions = self.get_page_revisions(page_title, limit=1000)
        if not revisions:
            return None
        
        reverts = self.detect_reverts(revisions)
        if len(reverts) < 3:
            return None
        
        # Group reverts by time windows (24 hours)
        revert_times = [datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')) for r in reverts]
        revert_users = [r['user'] for r in reverts]
        
        # Group reverts within 24 hours
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
        
        # Create timeline data
        timeline_data = []
        for i, group in enumerate(revert_groups):
            start_time = datetime.fromisoformat(group[0]['timestamp'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(group[-1]['timestamp'].replace('Z', '+00:00'))
            duration = (end_time - start_time).total_seconds() / 3600
            
            users = list(set([r['user'] for r in group]))
            
            # Calculate escalation level based on revert count and speed
            escalation_level = len(group) * len(users) / max(duration, 1)
            
            timeline_data.append({
                'edit_war_id': i + 1,
                'start_time': start_time,
                'end_time': end_time,
                'duration_hours': duration,
                'revert_count': len(group),
                'unique_editors': len(users),
                'editors': users,
                'escalation_level': escalation_level,
                'status': 'Resolved' if duration < 72 else 'Ongoing'
            })
        
        # Create timeline visualization
        fig = go.Figure()
        
        # Add timeline bars
        for war in timeline_data:
            color = 'red' if war['escalation_level'] > 10 else 'orange' if war['escalation_level'] > 5 else 'yellow'
            
            fig.add_trace(go.Bar(
                x=[war['duration_hours']],
                y=[f"Edit War {war['edit_war_id']}"],
                orientation='h',
                marker_color=color,
                name=f"War {war['edit_war_id']}",
                text=f"Reverts: {war['revert_count']}<br>Editors: {war['unique_editors']}<br>Duration: {war['duration_hours']:.1f}h",
                hoverinfo='text',
                showlegend=False
            ))
        
        fig.update_layout(
            title=f"Edit War Timeline: {page_title}",
            xaxis_title="Duration (hours)",
            yaxis_title="Edit Wars",
            height=400,
            barmode='overlay'
        )
        
        # Create detailed timeline with individual reverts
        fig2 = go.Figure()
        
        # Add individual revert points
        for i, revert in enumerate(reverts):
            revert_time = datetime.fromisoformat(revert['timestamp'].replace('Z', '+00:00'))
            
            fig2.add_trace(go.Scatter(
                x=[revert_time],
                y=[1],
                mode='markers',
                marker=dict(size=10, color='red'),
                name=f"Revert {i+1}",
                text=f"User: {revert['user']}<br>Time: {revert_time.strftime('%Y-%m-%d %H:%M')}",
                hoverinfo='text',
                showlegend=False
            ))
        
        fig2.update_layout(
            title=f"Individual Revert Timeline: {page_title}",
            xaxis_title="Time",
            yaxis_title="Reverts",
            height=300,
            yaxis=dict(showticklabels=False)
        )
        
        # Save the plots
        import os
        os.makedirs(output_dir, exist_ok=True)
        fig.write_html(f"{output_dir}/edit_war_timeline_{page_title.replace(' ', '_')}.html")
        fig.write_image(f"{output_dir}/edit_war_timeline_{page_title.replace(' ', '_')}.png")
        fig2.write_html(f"{output_dir}/revert_timeline_{page_title.replace(' ', '_')}.html")
        fig2.write_image(f"{output_dir}/revert_timeline_{page_title.replace(' ', '_')}.png")
        
        logger.info(f"Edit war timeline saved for {page_title}")
        return fig, fig2
    
    def create_comprehensive_dashboard(self, output_dir: str = "edit_war_visualizations"):
        """Create comprehensive dashboard with all visualizations"""
        logger.info("Creating comprehensive edit war dashboard")
        
        # Analyze multiple pages
        dashboard_data = []
        
        for page in self.controversial_pages[:5]:  # Limit to 5 for performance
            logger.info(f"Analyzing {page} for dashboard")
            
            revisions = self.get_page_revisions(page, limit=500)
            if not revisions:
                continue
            
            reverts = self.detect_reverts(revisions)
            if len(reverts) < 3:
                continue
            
            # Calculate metrics
            revert_rate = len(reverts) / len(revisions)
            unique_editors = len(set([r['user'] for r in reverts]))
            
            dashboard_data.append({
                'page': page,
                'revert_count': len(reverts),
                'revert_rate': revert_rate,
                'unique_editors': unique_editors,
                'total_revisions': len(revisions)
            })
            
            time.sleep(0.1)  # Be respectful to the API
        
        if not dashboard_data:
            logger.warning("No data available for dashboard")
            return
        
        # Create dashboard
        df = pd.DataFrame(dashboard_data)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revert Count by Page', 'Revert Rate by Page', 
                          'Editor Participation', 'Revert Rate vs Editor Count'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # 1. Revert count bar chart
        fig.add_trace(
            go.Bar(x=df['page'], y=df['revert_count'], name='Revert Count'),
            row=1, col=1
        )
        
        # 2. Revert rate bar chart
        fig.add_trace(
            go.Bar(x=df['page'], y=df['revert_rate'], name='Revert Rate'),
            row=1, col=2
        )
        
        # 3. Editor participation scatter
        fig.add_trace(
            go.Scatter(x=df['page'], y=df['unique_editors'], 
                      mode='markers+text', text=df['unique_editors'],
                      name='Unique Editors'),
            row=2, col=1
        )
        
        # 4. Correlation scatter
        fig.add_trace(
            go.Scatter(x=df['revert_rate'], y=df['unique_editors'],
                      mode='markers+text', text=df['page'],
                      name='Correlation'),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Wikipedia Edit War Analysis Dashboard",
            height=800,
            showlegend=False
        )
        
        # Save dashboard
        import os
        os.makedirs(output_dir, exist_ok=True)
        fig.write_html(f"{output_dir}/edit_war_dashboard.html")
        fig.write_image(f"{output_dir}/edit_war_dashboard.png")
        
        logger.info("Comprehensive dashboard created")
        return fig
    
    def generate_all_visualizations(self, pages: List[str] = None, output_dir: str = "edit_war_visualizations"):
        """Generate all visualizations for specified pages"""
        if pages is None:
            pages = self.controversial_pages[:5]  # Default to first 5 controversial pages
        
        logger.info(f"Generating visualizations for {len(pages)} pages")
        
        results = {}
        
        for page in pages:
            logger.info(f"Processing visualizations for: {page}")
            
            # Create heatmap
            heatmap = self.create_revert_heatmap(page, output_dir)
            
            # Create network
            network = self.create_editor_network(page, output_dir)
            
            # Create timeline
            timeline = self.create_edit_war_timeline(page, output_dir)
            
            results[page] = {
                'heatmap': heatmap,
                'network': network,
                'timeline': timeline
            }
            
            time.sleep(0.1)  # Be respectful to the API
        
        # Create comprehensive dashboard
        dashboard = self.create_comprehensive_dashboard(output_dir)
        results['dashboard'] = dashboard
        
        logger.info("All visualizations generated successfully")
        return results

def main():
    """Main function to generate all visualizations"""
    print("Wikipedia Edit War Visualization Generator")
    print("=" * 50)
    
    # Initialize visualizer
    visualizer = EditWarVisualizer()
    
    # Generate visualizations for top controversial pages
    pages_to_analyze = ["Gun control", "Palestine", "Vaccine", "Donald Trump", "Israel"]
    
    print(f"\nGenerating visualizations for: {', '.join(pages_to_analyze)}")
    
    results = visualizer.generate_all_visualizations(pages_to_analyze)
    
    print("\nVisualization Summary:")
    print("-" * 30)
    print("Generated visualizations:")
    print("1. Revert frequency heatmaps")
    print("2. Editor interaction networks")
    print("3. Edit war escalation timelines")
    print("4. Comprehensive dashboard")
    print("\nFiles saved to: edit_war_visualizations/")
    print("- HTML files for interactive viewing")
    print("- PNG files for static images")
    
    print(f"\nAnalysis complete! Check the edit_war_visualizations/ directory for all charts.")

if __name__ == "__main__":
    main() 