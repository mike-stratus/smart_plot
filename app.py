import panel as pn
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import numpy as np

pn.extension('plotly', 'tabulator')

class TableauLikeApp:
    """A Tableau-like data visualization app built with Panel"""

    def __init__(self):
        # Initialize data storage
        self.df = None
        self.filtered_df = None

        # Initialize filter tracking (support up to 4 filters)
        self.num_filters = 4
        self.filter_slots = []

        # Create widgets
        self._create_widgets()

        # Create layout
        self.layout = self._create_layout()

    def _create_widgets(self):
        """Create all UI widgets"""
        # File upload
        self.file_input = pn.widgets.FileInput(
            accept='.csv,.parquet',
            name='Upload CSV or Parquet File',
            sizing_mode='stretch_width'
        )
        self.file_input.param.watch(self._on_file_upload, 'value')

        # Data info panel
        self.info_pane = pn.pane.Markdown("### No data loaded\nPlease upload a CSV or Parquet file.")

        # Chart type selector
        self.chart_type = pn.widgets.Select(
            name='Chart Type',
            options=['Bar', 'Line', 'Scatter', 'Box', 'Histogram', 'Violin', 'Heatmap', 'Pie'],
            value='Bar',
            sizing_mode='stretch_width'
        )
        self.chart_type.param.watch(self._update_plot, 'value')

        # Column selectors
        self.x_axis = pn.widgets.Select(
            name='X-Axis',
            options=[],
            sizing_mode='stretch_width'
        )
        self.x_axis.param.watch(self._update_plot, 'value')

        self.y_axis = pn.widgets.Select(
            name='Y-Axis',
            options=[],
            sizing_mode='stretch_width'
        )
        self.y_axis.param.watch(self._update_plot, 'value')

        self.color_by = pn.widgets.Select(
            name='Color By (Optional)',
            options=['None'],
            value='None',
            sizing_mode='stretch_width'
        )
        self.color_by.param.watch(self._update_plot, 'value')

        self.size_by = pn.widgets.Select(
            name='Size By (Optional)',
            options=['None'],
            value='None',
            sizing_mode='stretch_width'
        )
        self.size_by.param.watch(self._update_plot, 'value')

        # Aggregation options
        self.agg_func = pn.widgets.Select(
            name='Aggregation',
            options=['None', 'Sum', 'Mean', 'Median', 'Count', 'Min', 'Max', 'Std'],
            value='None',
            sizing_mode='stretch_width'
        )
        self.agg_func.param.watch(self._update_plot, 'value')

        # Filter section - Create up to 4 filter slots
        self._create_filter_slots()

        # Apply filter button
        self.apply_filter_btn = pn.widgets.Button(
            name='Apply Filters',
            button_type='primary',
            sizing_mode='stretch_width'
        )
        self.apply_filter_btn.on_click(self._apply_filters)

        # Reset filter button
        self.reset_filter_btn = pn.widgets.Button(
            name='Reset All Filters',
            button_type='warning',
            sizing_mode='stretch_width'
        )
        self.reset_filter_btn.on_click(self._reset_filters)

        # Data preview table
        self.data_table = pn.widgets.Tabulator(
            pd.DataFrame(),
            pagination='remote',
            page_size=10,
            sizing_mode='stretch_both',
            height=300
        )

        # Plot pane
        self.plot_pane = pn.pane.Plotly(
            sizing_mode='stretch_both',
            height=600
        )

    def _create_filter_slots(self):
        """Create up to 4 filter slots"""
        for i in range(self.num_filters):
            filter_slot = {
                'index': i,
                'column_selector': pn.widgets.Select(
                    name=f'Filter {i+1} Column',
                    options=['None'],
                    value='None',
                    sizing_mode='stretch_width'
                ),
                'widget_container': pn.Column(sizing_mode='stretch_width'),
                'clear_button': pn.widgets.Button(
                    name=f'Clear Filter {i+1}',
                    button_type='light',
                    sizing_mode='stretch_width',
                    visible=False
                )
            }

            # Set up callback for column selector
            filter_slot['column_selector'].param.watch(
                lambda event, idx=i: self._on_filter_column_change(event, idx),
                'value'
            )

            # Set up callback for clear button
            filter_slot['clear_button'].on_click(
                lambda event, idx=i: self._clear_filter_slot(idx)
            )

            self.filter_slots.append(filter_slot)

    def _on_file_upload(self, event):
        """Handle file upload"""
        if event.new is None:
            return

        try:
            # Read file
            file_bytes = BytesIO(event.new)
            filename = self.file_input.filename

            if filename.endswith('.csv'):
                self.df = pd.read_csv(file_bytes)
            elif filename.endswith('.parquet'):
                self.df = pd.read_parquet(file_bytes)
            else:
                self.info_pane.object = "### Error\nUnsupported file format. Please upload CSV or Parquet."
                return

            self.filtered_df = self.df.copy()

            # Update UI
            self._update_column_options()
            self._update_data_preview()
            self._update_info()
            self._update_plot()

        except Exception as e:
            self.info_pane.object = f"### Error\nFailed to load file: {str(e)}"

    def _update_column_options(self):
        """Update column options in selectors"""
        if self.df is None:
            return

        columns = list(self.df.columns)
        numeric_columns = list(self.df.select_dtypes(include=[np.number]).columns)
        categorical_columns = list(self.df.select_dtypes(include=['object', 'category']).columns)

        # Update selectors
        self.x_axis.options = columns
        self.x_axis.value = columns[0] if columns else None

        self.y_axis.options = columns
        self.y_axis.value = numeric_columns[0] if numeric_columns else (columns[1] if len(columns) > 1 else columns[0])

        self.color_by.options = ['None'] + columns
        self.color_by.value = 'None'

        self.size_by.options = ['None'] + numeric_columns
        self.size_by.value = 'None'

        # Update all filter slot column selectors
        for filter_slot in self.filter_slots:
            filter_slot['column_selector'].options = ['None'] + columns
            if filter_slot['column_selector'].value not in ['None'] + columns:
                filter_slot['column_selector'].value = 'None'

    def _update_data_preview(self):
        """Update data preview table"""
        if self.filtered_df is not None:
            self.data_table.value = self.filtered_df

    def _update_info(self):
        """Update data info panel"""
        if self.df is None:
            return

        rows, cols = self.df.shape
        filtered_rows = len(self.filtered_df) if self.filtered_df is not None else rows

        info_text = f"""### Data Info
- **Total Rows:** {rows:,}
- **Filtered Rows:** {filtered_rows:,}
- **Columns:** {cols}
- **Memory Usage:** {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB
"""
        self.info_pane.object = info_text

    def _on_filter_column_change(self, event, filter_index):
        """Handle filter column change for a specific filter slot"""
        if event.new == 'None' or self.df is None:
            filter_slot = self.filter_slots[filter_index]
            filter_slot['widget_container'].clear()
            filter_slot['clear_button'].visible = False
            return

        filter_slot = self.filter_slots[filter_index]
        column = event.new
        dtype = self.df[column].dtype

        # Create appropriate filter widget based on data type
        if pd.api.types.is_numeric_dtype(dtype):
            min_val = float(self.df[column].min())
            max_val = float(self.df[column].max())

            filter_widget = pn.widgets.RangeSlider(
                name=f'{column} Range',
                start=min_val,
                end=max_val,
                value=(min_val, max_val),
                step=(max_val - min_val) / 100 if max_val != min_val else 1,
                sizing_mode='stretch_width'
            )
        else:
            unique_values = sorted(self.df[column].dropna().unique().tolist())
            filter_widget = pn.widgets.MultiChoice(
                name=f'{column} Values',
                options=unique_values,
                value=unique_values[:min(10, len(unique_values))],
                sizing_mode='stretch_width',
                max_items=20
            )

        filter_slot['widget_container'].clear()
        filter_slot['widget_container'].append(filter_widget)
        filter_slot['clear_button'].visible = True

    def _clear_filter_slot(self, filter_index):
        """Clear a specific filter slot"""
        filter_slot = self.filter_slots[filter_index]
        filter_slot['column_selector'].value = 'None'
        filter_slot['widget_container'].clear()
        filter_slot['clear_button'].visible = False

    def _apply_filters(self, event=None):
        """Apply all active filters to data"""
        if self.df is None:
            return

        self.filtered_df = self.df.copy()

        # Apply each filter slot sequentially
        for filter_slot in self.filter_slots:
            column = filter_slot['column_selector'].value

            if column != 'None' and len(filter_slot['widget_container']) > 0:
                filter_widget = filter_slot['widget_container'][0]

                if isinstance(filter_widget, pn.widgets.RangeSlider):
                    min_val, max_val = filter_widget.value
                    self.filtered_df = self.filtered_df[
                        (self.filtered_df[column] >= min_val) &
                        (self.filtered_df[column] <= max_val)
                    ]
                elif isinstance(filter_widget, pn.widgets.MultiChoice):
                    selected_values = filter_widget.value
                    if selected_values:
                        self.filtered_df = self.filtered_df[
                            self.filtered_df[column].isin(selected_values)
                        ]

        self._update_data_preview()
        self._update_info()
        self._update_plot()

    def _reset_filters(self, event=None):
        """Reset all filters"""
        if self.df is None:
            return

        self.filtered_df = self.df.copy()

        # Clear all filter slots
        for filter_slot in self.filter_slots:
            filter_slot['column_selector'].value = 'None'
            filter_slot['widget_container'].clear()
            filter_slot['clear_button'].visible = False

        self._update_data_preview()
        self._update_info()
        self._update_plot()

    def _update_plot(self, event=None):
        """Update the plot based on current selections"""
        if self.filtered_df is None or self.x_axis.value is None or self.y_axis.value is None:
            return

        try:
            df = self.filtered_df.copy()
            chart_type = self.chart_type.value
            x_col = self.x_axis.value
            y_col = self.y_axis.value
            color_col = self.color_by.value if self.color_by.value != 'None' else None
            size_col = self.size_by.value if self.size_by.value != 'None' else None
            agg = self.agg_func.value

            # Apply aggregation if needed
            if agg != 'None' and chart_type in ['Bar', 'Line']:
                agg_func_map = {
                    'Sum': 'sum',
                    'Mean': 'mean',
                    'Median': 'median',
                    'Count': 'count',
                    'Min': 'min',
                    'Max': 'max',
                    'Std': 'std'
                }

                groupby_cols = [x_col]
                if color_col:
                    groupby_cols.append(color_col)

                df = df.groupby(groupby_cols, as_index=False)[y_col].agg(agg_func_map[agg])

            # Create plot based on chart type
            fig = None

            if chart_type == 'Bar':
                fig = px.bar(df, x=x_col, y=y_col, color=color_col,
                            title=f'{chart_type} Chart',
                            template='plotly_white')

            elif chart_type == 'Line':
                fig = px.line(df, x=x_col, y=y_col, color=color_col,
                             title=f'{chart_type} Chart',
                             template='plotly_white')

            elif chart_type == 'Scatter':
                fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col,
                                title=f'{chart_type} Chart',
                                template='plotly_white')

            elif chart_type == 'Box':
                fig = px.box(df, x=x_col, y=y_col, color=color_col,
                            title=f'{chart_type} Chart',
                            template='plotly_white')

            elif chart_type == 'Histogram':
                fig = px.histogram(df, x=x_col, color=color_col,
                                  title=f'{chart_type} Chart',
                                  template='plotly_white')

            elif chart_type == 'Violin':
                fig = px.violin(df, x=x_col, y=y_col, color=color_col,
                               title=f'{chart_type} Chart',
                               template='plotly_white')

            elif chart_type == 'Heatmap':
                # For heatmap, pivot the data
                if color_col:
                    pivot_df = df.pivot_table(values=y_col, index=x_col, columns=color_col, aggfunc='mean')
                    fig = px.imshow(pivot_df,
                                   title=f'{chart_type} Chart',
                                   template='plotly_white',
                                   aspect='auto')
                else:
                    # Create correlation heatmap for numeric columns
                    numeric_df = df.select_dtypes(include=[np.number])
                    corr = numeric_df.corr()
                    fig = px.imshow(corr,
                                   title='Correlation Heatmap',
                                   template='plotly_white',
                                   aspect='auto',
                                   color_continuous_scale='RdBu_r')

            elif chart_type == 'Pie':
                # Aggregate data for pie chart
                pie_data = df.groupby(x_col)[y_col].sum().reset_index()
                fig = px.pie(pie_data, values=y_col, names=x_col,
                            title=f'{chart_type} Chart',
                            template='plotly_white')

            if fig:
                fig.update_layout(
                    height=600,
                    hovermode='closest',
                    showlegend=True
                )
                self.plot_pane.object = fig

        except Exception as e:
            self.plot_pane.object = go.Figure().add_annotation(
                text=f"Error creating plot: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="red")
            )

    def _create_layout(self):
        """Create the app layout"""
        # Build filter UI components
        filter_components = [pn.pane.Markdown("### Filters (Up to 4)")]

        for i, filter_slot in enumerate(self.filter_slots):
            filter_components.extend([
                pn.pane.Markdown(f"**Filter {i+1}**", margin=(10, 5, 5, 5)),
                filter_slot['column_selector'],
                filter_slot['widget_container'],
                filter_slot['clear_button']
            ])

        filter_components.extend([
            pn.layout.Divider(),
            pn.Row(self.apply_filter_btn, self.reset_filter_btn)
        ])

        # Sidebar with controls
        sidebar = pn.Column(
            pn.pane.Markdown("# 📊 Smart Plot"),
            pn.pane.Markdown("### Data Source"),
            self.file_input,
            self.info_pane,
            pn.layout.Divider(),
            pn.pane.Markdown("### Visualization Controls"),
            self.chart_type,
            self.x_axis,
            self.y_axis,
            self.color_by,
            self.size_by,
            self.agg_func,
            pn.layout.Divider(),
            *filter_components,
            sizing_mode='stretch_width',
            width=350,
            scroll=True
        )

        # Main content area
        main_content = pn.Column(
            pn.pane.Markdown("## Interactive Visualization"),
            self.plot_pane,
            pn.layout.Divider(),
            pn.pane.Markdown("## Data Preview"),
            self.data_table,
            sizing_mode='stretch_both'
        )

        # Complete layout
        template = pn.template.FastListTemplate(
            title='Smart Plot - Tableau-like Data Visualization',
            sidebar=[sidebar],
            main=[main_content],
            theme='default',
            theme_toggle=False,
            header_background='#2196F3'
        )

        return template

# Create and serve the app
app = TableauLikeApp()
app.layout.servable()
