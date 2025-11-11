# Smart Plot - Tableau-like Data Visualization App

A powerful, interactive data visualization web application built with Python Panel that provides a Tableau-like interface for exploring and visualizing CSV and Parquet files.

## Features

- **📁 File Upload**: Support for CSV and Parquet file formats
- **📊 Multiple Chart Types**: Bar, Line, Scatter, Box, Histogram, Violin, Heatmap, and Pie charts
- **🎨 Interactive Controls**:
  - X-axis and Y-axis column selection
  - Color grouping by categorical or numeric columns
  - Continuous color scales for numeric columns (automatic)
  - Size mapping for scatter plots
  - Aggregation functions (Sum, Mean, Median, Count, Min, Max, Std)
- **🔍 Advanced Filtering**:
  - Support up to 4 simultaneous filters
  - Numeric columns: Range sliders
  - Categorical columns: Multi-select dropdowns
  - Individual filter clearing or reset all at once
- **📋 Data Preview**: Interactive table with pagination
- **📈 Real-time Updates**: All visualizations update instantly as you change settings
- **💾 Memory Efficient**: Handles large datasets with efficient pandas operations

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd smart_plot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Start the Panel server:

```bash
panel serve app.py --show
```

This will:
- Start a local web server (usually at `http://localhost:5006/app`)
- Automatically open the app in your default browser

For development with auto-reload:

```bash
panel serve app.py --show --autoreload
```

### Using the Interface

1. **Upload Data**
   - Click the "Upload CSV or Parquet File" button in the sidebar
   - Select your data file (.csv or .parquet)
   - The app will automatically load and display data info

2. **Configure Visualization**
   - **Chart Type**: Choose from 8 different chart types
   - **X-Axis**: Select the column for the horizontal axis
   - **Y-Axis**: Select the column for the vertical axis
   - **Color By**: Group data by any column (optional)
     - Categorical columns: Uses discrete color palette
     - Numeric columns: Automatically uses continuous color scale (Viridis)
     - For Box/Histogram/Violin with numeric colors: Values are binned into 5 ranges
   - **Size By**: Map point sizes to a numeric column (for scatter plots)
   - **Aggregation**: Apply aggregation functions for grouped data

3. **Apply Filters (Up to 4)**
   - The app supports up to 4 simultaneous filters
   - For each filter slot:
     - Select a column from the "Filter X Column" dropdown
     - Use the range slider (numeric) or multi-select (categorical) to set filter criteria
     - Click "Clear Filter X" to remove that specific filter
   - Click "Apply Filters" to update the visualization with all active filters
   - Click "Reset All Filters" to clear all filters at once
   - Filters are applied sequentially, allowing complex data filtering

4. **Explore Data**
   - View the interactive plot with hover tooltips
   - Scroll down to see the data preview table
   - Use pagination to navigate through rows

## Chart Types

### Bar Chart
- Great for comparing categories
- Supports aggregation and grouping
- Best with: Categorical X-axis, Numeric Y-axis

### Line Chart
- Perfect for time series and trends
- Supports multiple lines with color grouping
- Best with: Sequential X-axis, Numeric Y-axis

### Scatter Plot
- Explore relationships between variables
- Supports color and size mapping
- Best with: Numeric X and Y axes

### Box Plot
- Visualize distributions and outliers
- Compare distributions across categories
- Best with: Categorical X-axis, Numeric Y-axis

### Histogram
- Show frequency distributions
- Automatically bins numeric data
- Best with: Numeric X-axis

### Violin Plot
- Detailed distribution visualization
- Combines box plot and density plot
- Best with: Categorical X-axis, Numeric Y-axis

### Heatmap
- Show correlations or pivot table data
- Requires color grouping for pivot mode
- Best with: Numeric data

### Pie Chart
- Display proportions and percentages
- Shows composition of a whole
- Best with: Categorical X-axis, Numeric Y-axis

## Example Datasets

Test the app with these sample datasets:

1. **Sales Data** (CSV)
2. **Iris Dataset** (CSV)
3. **Financial Data** (Parquet)

## Technical Details

### Built With

- **Panel**: Interactive web app framework
- **Plotly**: Rich, interactive visualizations
- **Pandas**: Data manipulation and analysis
- **PyArrow**: Fast Parquet file reading

### Architecture

The app follows a reactive architecture:
- Widget changes trigger callbacks
- Callbacks update the internal state
- State changes automatically refresh visualizations
- All operations are performed on filtered data views

## Troubleshooting

### File Upload Issues
- Ensure file is valid CSV or Parquet format
- Check file size (large files may take longer to load)
- Verify column names don't contain special characters

### Visualization Errors
- Ensure selected columns are compatible with chart type
- Check for missing values in selected columns
- Try a different aggregation function if grouping fails

### Performance
- For large datasets (>1M rows), consider sampling
- Use Parquet format for better performance
- Apply filters to reduce data size before plotting

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License
