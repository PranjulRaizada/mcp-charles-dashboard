# Charles Log Dashboard

A modern, interactive dashboard for visualizing and analyzing Charles Proxy log files.

## Features

- **Interactive Charts**: Uses Chart.js to visualize status codes, request methods, top hosts, and timing metrics
- **Responsive Design**: Works well on different screen sizes
- **Clean UI**: Modern look and feel with proper spacing and organization
- **Detailed Tables**: Shows detailed breakdowns with counts and percentages
- **Streamlit Dashboard**: Additional Streamlit-based dashboard for advanced data exploration

## Directory Structure

```
dashboard/
├── __init__.py         # Package initialization
├── dashboard.py        # Streamlit dashboard
├── static/
│   ├── css/
│   │   └── dashboard.css
│   └── js/
│       └── dashboard.js
├── templates/
│   └── dashboard.html
└── requirements.txt
```

## Requirements

The dashboard requires the following dependencies:

### Core Dependencies
- Chart.js (>=3.7.0)
- Jinja2 (>=3.0.0)
- Flask (>=2.0.1)

### Data Processing
- Pandas (>=1.3.0)
- NumPy (>=1.24.0)

### Additional Visualization (Optional)
- Plotly (>=5.5.0)
- Dash (>=2.0.0)
- Streamlit (for the Streamlit dashboard)

## Installation

To install the required dependencies:

```bash
pip install -r dashboard/requirements.txt
```

## Usage

### HTML Dashboard

The HTML dashboard is automatically loaded when running the `view_charles_log_dashboard` tool in the main application.

### Streamlit Dashboard

To run the Streamlit dashboard:

```bash
# On Linux/Mac
./run_dashboard.sh

# On Windows
run_dashboard.bat
```

## Visualizations

The dashboard provides the following visualizations:

1. **Status Code Distribution**: Bar chart showing the distribution of HTTP status codes
2. **Request Methods**: Doughnut chart showing the proportion of different HTTP methods
3. **Top 10 Hosts**: Horizontal bar chart of the most frequently accessed hosts
4. **Request Duration**: Comparison of minimum, average, and maximum response times
5. **Duration Distribution** (when available): Histogram of request durations across different time ranges

## Customization

You can customize the dashboard by modifying the following files:
- `dashboard.css`: To change the styling and appearance
- `dashboard.js`: To modify chart behaviors or add new visualizations
- `dashboard.html`: To change the layout or add new elements
- `dashboard.py`: To modify the Streamlit dashboard

## Development

To contribute to the dashboard development:

1. Make sure all frontend files are placed in the appropriate directories
2. Test with different types of Charles log files to ensure compatibility
3. Follow the established code style for consistency 