#!/usr/bin/env python3
import json
import os
import sys
from collections import Counter
import webbrowser
import tempfile
from datetime import datetime

def load_data(file_path):
    """Load JSON data from file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        return {}

def generate_html_report(data, output_file, input_file):
    """Generate a HTML report from the parsed data"""
    
    # Start with HTML header
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Charles Log Analysis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2, h3 { color: #333; }
        .container { display: flex; flex-wrap: wrap; }
        .chart { margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Charles Proxy Log Analysis</h1>
"""
    
    # Add timestamp and filename
    html += f"<p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n"
    html += f"<p>File: {os.path.basename(input_file)}</p>\n"
    
    # Handle summary format
    if isinstance(data, dict) and "total_entries" in data:
        html += "<h2>Summary</h2>\n"
        html += f"<p>Total Entries: {data.get('total_entries', 0)}</p>\n"
        
        # Request Methods
        if "request_methods" in data:
            html += "<h3>Request Methods</h3>\n"
            html += "<table>\n"
            html += "<tr><th>Method</th><th>Count</th></tr>\n"
            
            for method, count in sorted(data["request_methods"].items(), key=lambda x: x[1], reverse=True):
                html += f"<tr><td>{method}</td><td>{count}</td></tr>\n"
            
            html += "</table>\n"
        
        # Status Codes
        if "status_codes" in data:
            html += "<h3>Status Codes</h3>\n"
            html += "<table>\n"
            html += "<tr><th>Status</th><th>Count</th></tr>\n"
            
            for status, count in sorted(data["status_codes"].items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
                html += f"<tr><td>{status}</td><td>{count}</td></tr>\n"
            
            html += "</table>\n"
        
        # Hosts
        if "hosts" in data:
            html += "<h3>Top Hosts</h3>\n"
            html += "<table>\n"
            html += "<tr><th>Host</th><th>Count</th></tr>\n"
            
            for host, count in sorted(data["hosts"].items(), key=lambda x: x[1], reverse=True)[:20]:
                html += f"<tr><td>{host}</td><td>{count}</td></tr>\n"
            
            html += "</table>\n"
        
        # Timing
        if "timing" in data:
            html += "<h3>Timing (ms)</h3>\n"
            html += "<table>\n"
            html += "<tr><th>Metric</th><th>Value</th></tr>\n"
            html += f"<tr><td>Minimum</td><td>{data['timing'].get('min', 0)}</td></tr>\n"
            html += f"<tr><td>Maximum</td><td>{data['timing'].get('max', 0)}</td></tr>\n"
            html += f"<tr><td>Average</td><td>{data['timing'].get('avg', 0)}</td></tr>\n"
            html += f"<tr><td>Total</td><td>{data['timing'].get('total', 0)}</td></tr>\n"
            html += "</table>\n"
    
    # Handle detailed format
    elif "entries" in data:
        entries = data["entries"]
        html += "<h2>Detailed Report</h2>\n"
        html += f"<p>Total Entries: {len(entries)}</p>\n"
        
        # Count status codes
        status_counts = Counter()
        host_counts = Counter()
        methods = Counter()
        durations = []
        
        for entry in entries:
            # Status codes
            status = str(entry.get("status", "Unknown"))
            status_counts[status] += 1
            
            # Hosts
            host = entry.get("host", "Unknown")
            host_counts[host] += 1
            
            # Methods
            method = entry.get("method", "Unknown")
            methods[method] += 1
            
            # Durations
            if "duration" in entry:
                try:
                    duration = float(entry["duration"])
                    durations.append(duration)
                except (ValueError, TypeError):
                    pass
        
        # Status Codes
        html += "<h3>Status Codes</h3>\n"
        html += "<table>\n"
        html += "<tr><th>Status</th><th>Count</th></tr>\n"
        
        for status, count in sorted(status_counts.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
            html += f"<tr><td>{status}</td><td>{count}</td></tr>\n"
        
        html += "</table>\n"
        
        # Top Hosts
        html += "<h3>Top Hosts</h3>\n"
        html += "<table>\n"
        html += "<tr><th>Host</th><th>Count</th></tr>\n"
        
        for host, count in host_counts.most_common(20):
            html += f"<tr><td>{host}</td><td>{count}</td></tr>\n"
        
        html += "</table>\n"
        
        # Request Methods
        html += "<h3>Request Methods</h3>\n"
        html += "<table>\n"
        html += "<tr><th>Method</th><th>Count</th></tr>\n"
        
        for method, count in methods.most_common():
            html += f"<tr><td>{method}</td><td>{count}</td></tr>\n"
        
        html += "</table>\n"
        
        # Timing
        if durations:
            html += "<h3>Timing (ms)</h3>\n"
            html += "<table>\n"
            html += "<tr><th>Metric</th><th>Value</th></tr>\n"
            html += f"<tr><td>Minimum</td><td>{min(durations)}</td></tr>\n"
            html += f"<tr><td>Maximum</td><td>{max(durations)}</td></tr>\n"
            html += f"<tr><td>Average</td><td>{sum(durations) / len(durations):.2f}</td></tr>\n"
            html += f"<tr><td>Total</td><td>{sum(durations)}</td></tr>\n"
            html += "</table>\n"
    
    # Close HTML
    html += """</body>
</html>
"""
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(html)
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_dashboard.py <json_file>")
        return
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
    
    print(f"Loading data from {file_path}...")
    data = load_data(file_path)
    
    if not data:
        print("Error: No data found or invalid JSON format.")
        return
    
    # Create output HTML file
    output_file = os.path.join(tempfile.gettempdir(), "charles_log_report.html")
    
    # Generate report
    try:
        report_path = generate_html_report(data, output_file, file_path)
        print(f"Report generated at: {report_path}")
        print("Opening in browser...")
        
        # Open in browser
        webbrowser.open('file://' + os.path.abspath(report_path))
    except Exception as e:
        print(f"Error generating report: {str(e)}")

if __name__ == "__main__":
    main() 