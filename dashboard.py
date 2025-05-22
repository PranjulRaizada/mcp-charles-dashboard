#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

def load_data(file_path: str) -> Dict:
    """Load JSON data from file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return {}

def create_entries_dataframe(data: Dict) -> pd.DataFrame:
    """Create a DataFrame from log entries"""
    # Handle different data formats
    entries = []
    
    if "entries" in data:
        # Detailed or raw format
        entries = data.get("entries", [])
    elif isinstance(data, dict) and "total_entries" in data:
        # Summary format - no entries to display
        st.info("This is a summary file. It contains statistics but no detailed entries.")
        return pd.DataFrame()
    elif isinstance(data, list):
        # Direct list of entries
        entries = data
    
    if not entries:
        return pd.DataFrame()
    
    # Convert entries to DataFrame
    df = pd.DataFrame(entries)
    
    # Ensure required columns exist
    for col in ["host", "status", "duration"]:
        if col not in df.columns:
            df[col] = None
    
    # If duration is present, add duration categories
    if "duration" in df.columns:
        df["duration_ms"] = pd.to_numeric(df["duration"], errors="coerce")
        # Create duration categories
        bins = [0, 100, 500, 1000, 5000, float('inf')]
        labels = ['<100ms', '100-500ms', '500ms-1s', '1s-5s', '>5s']
        df["duration_category"] = pd.cut(df["duration_ms"], bins=bins, labels=labels)
    
    return df

def plot_status_codes(df: pd.DataFrame) -> None:
    """Plot status code distribution"""
    if df.empty or "status" not in df.columns:
        st.warning("No status code data available")
        return
    
    # Filter out None/NaN values
    filtered_df = df[df["status"].notna()]
    if filtered_df.empty:
        st.warning("No valid status codes found")
        return
    
    # Convert status to string if it's not already
    filtered_df["status"] = filtered_df["status"].astype(str)
    
    # Count status codes
    status_counts = filtered_df["status"].value_counts().reset_index()
    status_counts.columns = ["Status Code", "Count"]
    
    # Create color map
    def get_status_color(status_str):
        if pd.isna(status_str) or not status_str.isdigit():
            return "gray"
        status = int(status_str)
        if 200 <= status < 300:
            return "green"
        elif 300 <= status < 400:
            return "blue"
        elif 400 <= status < 500:
            return "orange"
        elif 500 <= status < 600:
            return "red"
        else:
            return "gray"
    
    status_counts["Color"] = status_counts["Status Code"].apply(get_status_color)
    
    # Create bar chart
    fig = px.bar(
        status_counts, 
        x="Status Code", 
        y="Count",
        color="Color",
        color_discrete_map="identity",
        title="Status Code Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_duration_distribution(df: pd.DataFrame) -> None:
    """Plot request duration distribution"""
    if df.empty or "duration_ms" not in df.columns:
        st.warning("No duration data available")
        return
    
    # Filter out None/NaN values
    filtered_df = df[df["duration_ms"].notna()]
    if filtered_df.empty:
        st.warning("No valid duration data found")
        return
    
    # Plot histogram of durations
    fig = px.histogram(
        filtered_df, 
        x="duration_ms",
        nbins=50,
        title="Request Duration Distribution (ms)",
        labels={"duration_ms": "Duration (ms)"}
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Plot duration categories
    if "duration_category" in filtered_df.columns:
        cat_counts = filtered_df["duration_category"].value_counts().reset_index()
        cat_counts.columns = ["Duration", "Count"]
        cat_counts = cat_counts.sort_values("Duration")
        
        fig = px.bar(
            cat_counts,
            x="Duration",
            y="Count",
            title="Request Duration Categories"
        )
        st.plotly_chart(fig, use_container_width=True)

def plot_top_hosts(df: pd.DataFrame, top_n: int = 10) -> None:
    """Plot top hosts by request count"""
    if df.empty or "host" not in df.columns:
        st.warning("No host data available")
        return
    
    # Filter out None/NaN values
    filtered_df = df[df["host"].notna()]
    if filtered_df.empty:
        st.warning("No valid host data found")
        return
    
    # Count hosts
    host_counts = filtered_df["host"].value_counts().reset_index()
    host_counts.columns = ["Host", "Count"]
    
    # Get top N hosts
    top_hosts = host_counts.head(top_n)
    
    # Create horizontal bar chart
    fig = px.bar(
        top_hosts, 
        y="Host", 
        x="Count",
        orientation="h",
        title=f"Top {top_n} Hosts by Request Count"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_host_status_heatmap(df: pd.DataFrame, top_n: int = 10) -> None:
    """Plot heatmap of hosts vs status codes"""
    if df.empty or "host" not in df.columns or "status" not in df.columns:
        st.warning("No host or status data available")
        return
    
    # Filter out None/NaN values for both host and status
    filtered_df = df[df["host"].notna() & df["status"].notna()]
    if filtered_df.empty:
        st.warning("No valid host and status data found")
        return
    
    # Convert status to string if it's not already
    filtered_df["status"] = filtered_df["status"].astype(str)
    
    # Get top hosts
    top_hosts = filtered_df["host"].value_counts().head(top_n).index.tolist()
    if not top_hosts:
        st.warning("No host data available for heatmap")
        return
    
    # Filter for top hosts
    filtered_df = filtered_df[filtered_df["host"].isin(top_hosts)]
    
    try:
        # Create crosstab of hosts vs status codes
        crosstab = pd.crosstab(filtered_df["host"], filtered_df["status"])
        
        # Create heatmap
        fig = px.imshow(
            crosstab,
            labels=dict(x="Status Code", y="Host", color="Count"),
            title=f"Status Codes by Top {top_n} Hosts",
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Error creating host-status heatmap: {str(e)}")

def main():
    try:
        st.set_page_config(
            page_title="Charles Log Viewer",
            page_icon="🌐",
            layout="wide"
        )
        
        st.title("Charles Proxy Log Analyzer Dashboard")
        
        # Output directory selection - use environment variable or default to a common location
        default_output_dir = os.environ.get(
            "CHARLES_OUTPUT_DIR",
            os.path.join(os.path.expanduser("~"), "charles_output")
        )
        
        # If shared folder exists in parent directory, use that as default
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        shared_path = os.path.join(parent_dir, "mcp-charles-shared", "output")
        if os.path.exists(shared_path):
            default_output_dir = shared_path
        
        output_dir = st.sidebar.text_input("Output Directory", value=default_output_dir)
        
        # File selector
        try:
            json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        except FileNotFoundError:
            st.error(f"Directory '{output_dir}' not found")
            st.info("Please enter a valid directory path or create the directory")
            if not os.path.exists(output_dir):
                create_dir = st.button("Create Directory")
                if create_dir:
                    try:
                        os.makedirs(output_dir, exist_ok=True)
                        st.success(f"Created directory: {output_dir}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to create directory: {str(e)}")
            return
            
        if not json_files:
            st.error(f"No JSON files found in '{output_dir}'")
            st.info("Please run the parser first to generate JSON files, e.g.:\n\n```\npython client.py /path/to/your-file.chlsj --format detailed --save --output-dir={output_dir}\n```")
            return
        
        selected_file = st.selectbox("Select a parsed Charles log file:", json_files)
        full_path = os.path.join(output_dir, selected_file)
        
        # Load data
        data = load_data(full_path)
        if not data:
            return
        
        # Create DataFrame
        df = create_entries_dataframe(data)
        
        # Display summary info
        st.header("Log Summary")
        
        if "entries" in data:
            col1, col2 = st.columns(2)
            with col1:
                total_entries = len(data.get("entries", []))
                st.metric("Total Entries", total_entries)
        elif "total_entries" in data:
            # Summary format
            st.metric("Total Entries", data.get("total_entries", 0))
            
            # Display summary stats
            col1, col2 = st.columns(2)
            
            with col1:
                if "request_methods" in data:
                    st.subheader("Request Methods")
                    methods_df = pd.DataFrame(
                        {"Method": list(data["request_methods"].keys()), 
                        "Count": list(data["request_methods"].values())}
                    )
                    st.dataframe(methods_df, use_container_width=True)
                
                if "hosts" in data:
                    st.subheader("Top Hosts")
                    hosts_df = pd.DataFrame(
                        {"Host": list(data["hosts"].keys()), 
                        "Count": list(data["hosts"].values())}
                    ).sort_values("Count", ascending=False).head(10)
                    st.dataframe(hosts_df, use_container_width=True)
            
            with col2:
                if "status_codes" in data:
                    st.subheader("Status Codes")
                    status_df = pd.DataFrame(
                        {"Status": list(data["status_codes"].keys()), 
                        "Count": list(data["status_codes"].values())}
                    )
                    st.dataframe(status_df, use_container_width=True)
                
                if "timing" in data:
                    st.subheader("Timing (ms)")
                    timing = data["timing"]
                    st.metric("Min", timing.get("min", 0))
                    st.metric("Max", timing.get("max", 0))
                    st.metric("Average", timing.get("avg", 0))
            
            # No detailed data to display
            return
        
        if df.empty:
            st.warning("No entries found in the log file or unsupported format")
            return
        
        # Add filters
        st.header("Filters")
        
        # Get unique non-null values
        hosts = df["host"].dropna().unique().tolist()
        statuses = df["status"].dropna().unique().tolist()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Host filter
            hosts = ["All"] + sorted(hosts)
            selected_host = st.selectbox("Host:", hosts)
        
        with col2:
            # Status code filter
            statuses = ["All"] + sorted([str(s) for s in statuses if pd.notna(s)])
            selected_status = st.selectbox("Status Code:", statuses)
        
        with col3:
            # Duration filter
            if "duration_category" in df.columns:
                durations = ["All"] + sorted(df["duration_category"].dropna().unique().tolist())
                selected_duration = st.selectbox("Duration:", durations)
            else:
                selected_duration = "All"
                st.text("No duration data available")
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_host != "All":
            filtered_df = filtered_df[filtered_df["host"] == selected_host]
        
        if selected_status != "All":
            filtered_df = filtered_df[filtered_df["status"].astype(str) == selected_status]
        
        if selected_duration != "All" and "duration_category" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["duration_category"] == selected_duration]
        
        # Display filter summary
        st.metric("Filtered Entries", len(filtered_df))
        
        # Visualizations
        st.header("Visualizations")
        
        # Status code distribution
        plot_status_codes(filtered_df)
        
        # Top hosts
        col1, col2 = st.columns(2)
        
        with col1:
            plot_top_hosts(filtered_df)
        
        with col2:
            plot_host_status_heatmap(filtered_df)
        
        # Duration distribution
        plot_duration_distribution(filtered_df)
        
        # Data table
        st.header("Data Explorer")
        
        # Drop duration calculation columns for display
        display_df = filtered_df.drop(columns=["duration_ms", "duration_category"], errors="ignore")
        
        # Function to recursively parse and prettify nested JSON strings
        def deep_parse_json(content, max_depth=3, current_depth=0):
            """Recursively parse nested JSON strings in a value with depth limit"""
            # Check recursion depth to prevent infinite recursion or stack overflow
            if current_depth >= max_depth:
                return content
                
            try:
                if isinstance(content, dict):
                    # Handle dictionaries - recursively process each value
                    result = {}
                    for key, value in content.items():
                        result[key] = deep_parse_json(value, max_depth, current_depth + 1)
                    return result
                elif isinstance(content, list):
                    # Handle lists - recursively process each item
                    return [deep_parse_json(item, max_depth, current_depth + 1) for item in content]
                elif isinstance(content, str):
                    # See if this string is a JSON string itself
                    try:
                        if (content.strip().startswith('{') and content.strip().endswith('}')) or \
                           (content.strip().startswith('[') and content.strip().endswith(']')):
                            # Try to parse as JSON
                            parsed = json.loads(content)
                            # Recursively process this parsed JSON
                            return deep_parse_json(parsed, max_depth, current_depth + 1)
                    except json.JSONDecodeError:
                        # Not a JSON string, return as is
                        pass
                    except RecursionError:
                        st.warning("Recursion limit reached while processing nested JSON.")
                        return content
                # For any other type, return as is
                return content
            except Exception as e:
                # Catch any other exceptions to prevent dashboard crashes
                st.warning(f"Error processing JSON data: {str(e)}")
                return content

        # Function to safely process potentially large JSON data
        def safely_process_json(process_func, content, *args, **kwargs):
            """Wrapper to catch and handle errors when processing JSON data"""
            try:
                return process_func(content, *args, **kwargs)
            except RecursionError:
                st.warning("Recursion limit reached while processing JSON data.")
                return str(content)
            except MemoryError:
                st.warning("Out of memory while processing large JSON data.")
                return "Error: Data too large to process"
            except Exception as e:
                st.warning(f"Error processing JSON data: {str(e)}")
                return str(content)

        # Function to prettify and truncate JSON content
        def prettify_and_truncate(content, max_length=100):
            if pd.isna(content) or content is None:
                return ""
            
            # Convert to string if it's not already
            if not isinstance(content, str):
                try:
                    if isinstance(content, (dict, list)):
                        content = json.dumps(content, indent=2)
                    else:
                        content = str(content)
                except Exception:
                    content = str(content)
            
            # Try to parse and prettify JSON
            try:
                # Check if it looks like JSON
                if (content.strip().startswith('{') and content.strip().endswith('}')) or \
                   (content.strip().startswith('[') and content.strip().endswith(']')):
                    # Parse the JSON (this will handle escaped characters)
                    parsed = json.loads(content)
                    # Handle any nested JSON strings
                    deep_parsed = safely_process_json(deep_parse_json, parsed)
                    # Re-serialize with nice formatting but without escaping unicode or special chars
                    content = json.dumps(deep_parsed, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                # Not valid JSON, keep as is
                pass
            
            # Truncate if needed
            if len(content) > max_length:
                # Try to find a reasonable place to cut (like end of a line)
                cut_at = content.rfind('\n', 0, max_length)
                if cut_at > 0:
                    return content[:cut_at] + "\n..."
                else:
                    return content[:max_length] + "..."
            return content

        # Function to prettify JSON for full display
        def prettify_json(content):
            if pd.isna(content) or content is None:
                return ""
            
            # Convert to string if it's not already
            if not isinstance(content, str):
                try:
                    if isinstance(content, (dict, list)):
                        # Handle any nested JSON strings
                        deep_parsed = safely_process_json(deep_parse_json, content)
                        return json.dumps(deep_parsed, indent=2, ensure_ascii=False)
                    else:
                        content = str(content)
                except Exception:
                    return str(content)
            
            # Try to parse and prettify JSON
            try:
                # Check if it looks like JSON
                if (content.strip().startswith('{') and content.strip().endswith('}')) or \
                   (content.strip().startswith('[') and content.strip().endswith(']')):
                    # Parse the JSON (this will handle escaped characters)
                    parsed = json.loads(content)
                    # Handle any nested JSON strings
                    deep_parsed = safely_process_json(deep_parse_json, parsed)
                    # Re-serialize with nice formatting but without escaping unicode or special chars
                    return json.dumps(deep_parsed, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                # Not valid JSON, keep as is
                pass
                
            return content
        
        # Create a display-friendly version of the dataframe
        display_friendly_df = display_df.copy()
        
        # Add progress indicator for processing large datasets
        if len(display_df) > 100 and ('request_body' in display_df.columns or 'response_body' in display_df.columns):
            progress_bar = st.progress(0)
            st.info("Processing large dataset...")
            
        # Process columns safely
        for col in ['request_body', 'response_body']:
            if col in display_friendly_df.columns:
                # Process rows in chunks to avoid memory issues
                chunk_size = 50
                num_chunks = (len(display_friendly_df) + chunk_size - 1) // chunk_size
                
                for i in range(num_chunks):
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, len(display_friendly_df))
                    
                    # Process this chunk
                    for idx in range(start_idx, end_idx):
                        display_friendly_df.at[idx, col] = prettify_and_truncate(display_friendly_df.iloc[idx][col])
                    
                    # Update progress bar if shown
                    if len(display_df) > 100 and ('request_body' in display_df.columns or 'response_body' in display_df.columns):
                        progress_bar.progress((i + 1) / num_chunks)
                
        # Clear progress bar if shown
        if len(display_df) > 100 and ('request_body' in display_df.columns or 'response_body' in display_df.columns):
            st.success("Processing complete!")
            progress_bar.empty()
        
        # Data table section

        # Display data table (standard version without row selection)
        st.write("**Data Explorer:** Full request and response body data with proper JSON formatting.")
        
        # Create a display version with formatted JSON but without truncation
        display_friendly_no_truncate = display_df.copy()
        
        # Format JSON columns without truncation
        for col in ['request_body', 'response_body']:
            if col in display_friendly_no_truncate.columns:
                # Process rows for formatting
                for idx in range(len(display_friendly_no_truncate)):
                    content = display_friendly_no_truncate.iloc[idx][col]
                    if content and not pd.isna(content):
                        display_friendly_no_truncate.at[idx, col] = prettify_json(content)
        
        # Standard dataframe without selection
        st.dataframe(
            display_friendly_no_truncate,
            use_container_width=True,
            height=400
        )
        
        # Let user select row from dropdown
        st.write("### View Full Request/Response Data")
        row_indices = list(range(len(display_df)))
        if row_indices:
            selected_index = st.selectbox("Select a row to view details:", row_indices)
            selected_row = display_df.iloc[selected_index]
            
            # Show summary data for the row
            col1, col2, col3 = st.columns(3)
            if 'method' in selected_row:
                col1.metric("Method", selected_row.get('method', 'N/A'))
            if 'status' in selected_row:
                col2.metric("Status", selected_row.get('status', 'N/A'))
            if 'duration' in selected_row:
                col3.metric("Duration (ms)", selected_row.get('duration', 'N/A'))
            
            # Create tabs for request/response bodies
            if 'request_body' in selected_row and 'response_body' in selected_row:
                req_tab, resp_tab = st.tabs(["Request Body", "Response Body"])
                
                with req_tab:
                    if selected_row['request_body'] and not pd.isna(selected_row['request_body']):
                        # Prettify and display with syntax highlighting
                        pretty_req = prettify_json(selected_row['request_body'])
                        st.code(pretty_req, language="json")
                    else:
                        st.info("No request body data available.")
                        
                with resp_tab:
                    if selected_row['response_body'] and not pd.isna(selected_row['response_body']):
                        # Prettify and display with syntax highlighting
                        pretty_resp = prettify_json(selected_row['response_body'])
                        st.code(pretty_resp, language="json")
                    else:
                        st.info("No response body data available.")
            elif 'response_body' in selected_row:
                if selected_row['response_body'] and not pd.isna(selected_row['response_body']):
                    st.subheader("Response Body")
                    # Prettify and display with syntax highlighting
                    pretty_resp = prettify_json(selected_row['response_body'])
                    st.code(pretty_resp, language="json")
                else:
                    st.info("No response body data available.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.info("If this is a dependency issue, make sure you've installed all required packages with: `pip install -r dashboard_requirements.txt`")

if __name__ == "__main__":
    main() 