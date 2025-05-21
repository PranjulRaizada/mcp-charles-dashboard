# MCP-Charles Flow Diagram

This document describes the data flow in the MCP-Charles system, from traffic capture to analysis.

## Diagram

```mermaid
graph TB
    A[Mobile App] --> B[Charles Proxy]
    B -- Intercepts --> C[HTTP/HTTPS Traffic]
    C --> D[Save as .chlsj/.chls File]
    
    D --> E[Log Parser]
    E -- JSON Conversion --> F[Structured Data]
    
    F --> G[Dashboard]
    G --> H1[Status Code Analysis]
    G --> H2[Network Timing]
    G --> H3[Host Distribution]
    G --> H4[Request/Response Bodies]
    
    H1 --> I[Interactive Visualizations]
    H2 --> I
    H3 --> I
    H4 --> I
    
    I --> J[Troubleshooting & Debugging]
    J --> K[Performance Optimization]
    J --> L[API Analysis]
    
    class A,B,C networkCapture;
    class D,E,F dataProcessing;
    class G,H1,H2,H3,H4,I visualization;
    class J,K,L analysis;
    
    classDef networkCapture fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef dataProcessing fill:#eeeeee,stroke:#333,stroke-width:1px;
    classDef visualization fill:#d5f9e5,stroke:#333,stroke-width:1px;
    classDef analysis fill:#e5d5f9,stroke:#333,stroke-width:1px;
```

## Flow Description

The MCP-Charles workflow consists of several stages:

### 1. Data Capture
- **Mobile App**: The source of network traffic
- **Charles Proxy**: Intercepts HTTP/HTTPS traffic from the mobile app
- **Traffic Capture**: Records all requests and responses passing through the proxy

### 2. Log Generation
- Traffic is saved as `.chls` (Charles Session) or `.chlsj` (Charles Session JSON) files
- These files contain detailed information about requests and responses including:
  - URLs
  - Headers
  - Request bodies
  - Response bodies
  - Timing information

### 3. Data Processing
- **Log Parser**: Processes the raw log files 
- **JSON Conversion**: Transforms the data into a structured, standardized JSON format
- **Data Preparation**: Organizes and optimizes data for visualization and analysis

### 4. Visualization
- **Dashboard**: Presents the data in an interactive interface
- **Analysis Categories**:
  - Status Code Analysis: Distribution of HTTP status codes (200, 404, 500, etc.)
  - Network Timing: Request duration, time to first byte, etc.
  - Host Distribution: Top domains and endpoints
  - Request/Response Bodies: Detailed view of payloads

### 5. Analysis
- **Interactive Visualizations**: Allow filtering, sorting, and detailed inspection of data
- **Troubleshooting & Debugging**: Identify errors and unexpected behavior
- **Performance Optimization**: Analyze response times and identify bottlenecks
- **API Analysis**: Understand API structure, parameters, and behavior

## Usage Scenarios

1. **Mobile App Development**:
   - Debug network issues
   - Validate API requests and responses
   - Optimize network calls

2. **QA Testing**:
   - Verify correct data flow
   - Test error handling
   - Document API behavior

3. **Performance Analysis**:
   - Identify slow requests
   - Find opportunities for caching
   - Analyze payload sizes

4. **Security Testing**:
   - Inspect authentication flows
   - Review data being transmitted
   - Check for sensitive information in requests/responses 