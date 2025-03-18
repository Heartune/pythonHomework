"""
Data visualization utilities for the Library Management System.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns
from io import BytesIO
from datetime import datetime, timedelta
from .logger import get_logger

logger = get_logger(__name__)

# Set the style for all plots
plt.style.use('seaborn-v0_8-darkgrid')

def create_bar_chart(x, y, title='Bar Chart', xlabel='X', ylabel='Y', figsize=(10, 6), color='skyblue'):
    """
    Create a bar chart.
    
    Args:
        x (list): X-axis categories.
        y (list): Y-axis values.
        title (str): Chart title.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        figsize (tuple): Figure size.
        color (str): Bar color.
        
    Returns:
        tuple: Figure and axes objects.
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(x, y, color=color)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig, ax

def create_pie_chart(labels, values, title='Pie Chart', figsize=(10, 6)):
    """
    Create a pie chart.
    
    Args:
        labels (list): Slice labels.
        values (list): Slice values.
        title (str): Chart title.
        figsize (tuple): Figure size.
        
    Returns:
        tuple: Figure and axes objects.
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title(title)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.tight_layout()
    return fig, ax

def create_line_chart(data, title='Line Chart', xlabel='X', ylabel='Y', figsize=(10, 6)):
    """
    Create a line chart.
    
    Args:
        data (pandas.Series): Time series data.
        title (str): Chart title.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        figsize (tuple): Figure size.
        
    Returns:
        tuple: Figure and axes objects.
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(data.index, data.values)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    return fig, ax

def create_scatter_plot(x, y, title='Scatter Plot', xlabel='X', ylabel='Y', figsize=(10, 6)):
    """
    Create a scatter plot.
    
    Args:
        x (list): X-axis values.
        y (list): Y-axis values.
        title (str): Chart title.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        figsize (tuple): Figure size.
        
    Returns:
        tuple: Figure and axes objects.
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(x, y)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    return fig, ax

def create_heatmap(data, title='Heatmap', xlabel='X', ylabel='Y', figsize=(10, 8), cmap='viridis', annot=True, fmt='.1f'):
    """
    Create a heatmap.
    
    Args:
        data (pandas.DataFrame): Data matrix.
        title (str): Chart title.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        figsize (tuple): Figure size.
        cmap (str): Colormap name.
        annot (bool): Whether to annotate cells with values.
        fmt (str): Format string for annotations.
        
    Returns:
        tuple: Figure and axes objects.
    """
    fig, ax = plt.subplots(figsize=figsize)
    heatmap = sns.heatmap(data, annot=annot, fmt=fmt, cmap=cmap, ax=ax)
    # Force the creation of the colorbar/image
    fig.canvas.draw_idle()
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    return fig, ax

def create_histogram(data, title='Histogram', xlabel='Value', ylabel='Frequency', bins=10, figsize=(10, 6)):
    """
    Create a histogram.
    
    Args:
        data (list): Data values.
        title (str): Chart title.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        bins (int): Number of bins.
        figsize (tuple): Figure size.
        
    Returns:
        tuple: Figure and axes objects.
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(data, bins=bins)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    return fig, ax

def create_boxplot(data, title='Box Plot', xlabel='Category', ylabel='Value', figsize=(10, 6)):
    """
    Create a box plot.
    
    Args:
        data (dict): Dictionary with labels as keys and lists of values as values.
        title (str): Chart title.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        figsize (tuple): Figure size.
        
    Returns:
        tuple: Figure and axes objects.
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.boxplot(list(data.values()), labels=list(data.keys()))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    return fig, ax

def create_dashboard(visualizations, title='Dashboard', figsize=(12, 10)):
    """
    Create a dashboard with multiple visualizations.
    
    Args:
        visualizations (list): List of tuples (chart_type, chart_params).
        title (str): Dashboard title.
        figsize (tuple): Figure size.
        
    Returns:
        matplotlib.figure.Figure: Dashboard figure.
    """
    n = len(visualizations)
    rows = int(np.ceil(n / 2))
    
    fig = plt.figure(figsize=figsize)
    fig.suptitle(title, fontsize=16)
    
    for i, (chart_type, params) in enumerate(visualizations):
        ax = fig.add_subplot(rows, 2, i+1)
        
        if chart_type == 'bar':
            ax.bar(params.get('x', []), params.get('y', []))
            ax.set_title(params.get('title', f'Chart {i+1}'))
            ax.set_xlabel(params.get('xlabel', 'X'))
            ax.set_ylabel(params.get('ylabel', 'Y'))
            
        elif chart_type == 'pie':
            ax.pie(params.get('values', []), labels=params.get('labels', []), autopct='%1.1f%%')
            ax.set_title(params.get('title', f'Chart {i+1}'))
            ax.axis('equal')
            
        elif chart_type == 'line':
            data = params.get('data', pd.Series())
            ax.plot(data.index, data.values)
            ax.set_title(params.get('title', f'Chart {i+1}'))
            ax.set_xlabel(params.get('xlabel', 'X'))
            ax.set_ylabel(params.get('ylabel', 'Y'))
            
        elif chart_type == 'scatter':
            ax.scatter(params.get('x', []), params.get('y', []))
            ax.set_title(params.get('title', f'Chart {i+1}'))
            ax.set_xlabel(params.get('xlabel', 'X'))
            ax.set_ylabel(params.get('ylabel', 'Y'))
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for the suptitle
    return fig

def save_visualization(fig, filepath):
    """
    Save a visualization to a file.
    
    Args:
        fig (matplotlib.figure.Figure): Figure to save.
        filepath (str): Path to save the figure to.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        return True
    except Exception as e:
        logger.error(f"Error saving visualization: {e}")
        return False

def create_bar_chart_buffer(data, title, xlabel, ylabel, figsize=(10, 6), color='skyblue', 
                     horizontal=False, sort_values=False, limit=None):
    """
    Create a bar chart and return it as a buffer.
    
    Args:
        data (dict): Dictionary with labels as keys and values as values.
        title (str): The chart title.
        xlabel (str): The x-axis label.
        ylabel (str): The y-axis label.
        figsize (tuple): The figure size (width, height) in inches.
        color (str): Color of the bars.
        horizontal (bool): Whether to create a horizontal bar chart.
        sort_values (bool): Whether to sort the data by values.
        limit (int): Limit the number of items to display.
        
    Returns:
        BytesIO: A bytes buffer containing the chart image.
    """
    try:
        # Convert data to pandas Series for easier manipulation
        data_series = pd.Series(data)
        
        # Sort if requested
        if sort_values:
            data_series = data_series.sort_values(ascending=False)
        
        # Limit if requested
        if limit and len(data_series) > limit:
            data_series = data_series.head(limit)
        
        # Create figure
        plt.figure(figsize=figsize)
        
        # Create horizontal or vertical bar chart
        if horizontal:
            plt.barh(data_series.index, data_series.values, color=color)
            plt.xlabel(ylabel)  # Swap labels for horizontal
            plt.ylabel(xlabel)
        else:
            plt.bar(data_series.index, data_series.values, color=color)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.xticks(rotation=45, ha='right')
        
        plt.title(title)
        plt.tight_layout()
        
        # Save the figure to a bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error creating bar chart: {e}")
        return None

def create_pie_chart_buffer(data, title, figsize=(10, 6), colors=None, explode=None, 
                     shadow=True, startangle=90, autopct='%1.1f%%'):
    """
    Create a pie chart and return it as a buffer.
    
    Args:
        data (dict): Dictionary with labels as keys and values as values.
        title (str): The chart title.
        figsize (tuple): The figure size (width, height) in inches.
        colors (list): List of colors for the pie slices.
        explode (list): List of values to "explode" slices away from center.
        shadow (bool): Whether to draw a shadow beneath the pie.
        startangle (int): Starting angle in degrees.
        autopct (str): Format string for values inside wedges.
        
    Returns:
        BytesIO: A bytes buffer containing the chart image.
    """
    try:
        # Convert data to pandas Series for easier manipulation
        data_series = pd.Series(data)
        
        # Sort data by values (descending)
        data_series = data_series.sort_values(ascending=False)
        
        # Create figure
        plt.figure(figsize=figsize)
        
        # Create pie chart
        wedges, texts, autotexts = plt.pie(
            data_series.values, 
            labels=data_series.index, 
            autopct=autopct,
            explode=explode,
            shadow=shadow,
            startangle=startangle,
            colors=colors
        )
        
        # Make text more readable
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color('white')
        
        plt.title(title)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Save the figure to a bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error creating pie chart: {e}")
        return None

def create_line_chart_buffer(data, title, xlabel, ylabel, figsize=(10, 6), color='royalblue', 
                      marker='o', linestyle='-', grid=True, date_format=None):
    """
    Create a line chart and return it as a buffer.
    
    Args:
        data (dict): Dictionary with x-values as keys and y-values as values.
        title (str): The chart title.
        xlabel (str): The x-axis label.
        ylabel (str): The y-axis label.
        figsize (tuple): The figure size (width, height) in inches.
        color (str): Line color.
        marker (str): Marker style.
        linestyle (str): Line style.
        grid (bool): Whether to show grid lines.
        date_format (str): Format string for date x-axis (e.g., '%Y-%m').
        
    Returns:
        BytesIO: A bytes buffer containing the chart image.
    """
    try:
        # Convert data to pandas Series for easier manipulation
        data_series = pd.Series(data)
        
        # Create figure
        plt.figure(figsize=figsize)
        
        # Create line chart
        plt.plot(
            data_series.index, 
            data_series.values, 
            marker=marker, 
            linestyle=linestyle, 
            color=color
        )
        
        # Format x-axis as dates if requested
        if date_format:
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            plt.gcf().autofmt_xdate()
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(grid)
        plt.tight_layout()
        
        # Save the figure to a bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error creating line chart: {e}")
        return None

def create_multi_line_chart(data_dict, title, xlabel, ylabel, figsize=(10, 6), 
                           grid=True, legend_loc='best', date_format=None):
    """
    Create a line chart with multiple lines.
    
    Args:
        data_dict (dict): Dictionary with series names as keys and data dictionaries as values.
        title (str): The chart title.
        xlabel (str): The x-axis label.
        ylabel (str): The y-axis label.
        figsize (tuple): The figure size (width, height) in inches.
        grid (bool): Whether to show grid lines.
        legend_loc (str): Location of the legend.
        date_format (str): Format string for date x-axis (e.g., '%Y-%m').
        
    Returns:
        BytesIO: A bytes buffer containing the chart image.
    """
    try:
        # Create figure
        plt.figure(figsize=figsize)
        
        # Plot each line
        for label, data in data_dict.items():
            plt.plot(list(data.keys()), list(data.values()), label=label)
        
        # Format x-axis as dates if requested
        if date_format:
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            plt.gcf().autofmt_xdate()
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(grid)
        plt.legend(loc=legend_loc)
        plt.tight_layout()
        
        # Save the figure to a bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error creating multi-line chart: {e}")
        return None

def create_stacked_bar_chart(data_dict, title, xlabel, ylabel, figsize=(10, 6), 
                            colors=None, legend_loc='best'):
    """
    Create a stacked bar chart.
    
    Args:
        data_dict (dict): Dictionary with series names as keys and data dictionaries as values.
        title (str): The chart title.
        xlabel (str): The x-axis label.
        ylabel (str): The y-axis label.
        figsize (tuple): The figure size (width, height) in inches.
        colors (list): List of colors for the bars.
        legend_loc (str): Location of the legend.
        
    Returns:
        BytesIO: A bytes buffer containing the chart image.
    """
    try:
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data_dict)
        
        # Create figure
        plt.figure(figsize=figsize)
        
        # Create stacked bar chart
        df.plot(kind='bar', stacked=True, ax=plt.gca(), color=colors)
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend(loc=legend_loc)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save the figure to a bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error creating stacked bar chart: {e}")
        return None

def create_heatmap_buffer(data_matrix, title, xlabel, ylabel, figsize=(10, 8), 
                  cmap='viridis', annot=True, fmt='.1f'):
    """
    Create a heatmap and return it as a buffer.
    
    Args:
        data_matrix (pandas.DataFrame): DataFrame containing the data matrix.
        title (str): The chart title.
        xlabel (str): The x-axis label.
        ylabel (str): The y-axis label.
        figsize (tuple): The figure size (width, height) in inches.
        cmap (str): Colormap name.
        annot (bool): Whether to annotate cells with values.
        fmt (str): Format string for annotations.
        
    Returns:
        BytesIO: A bytes buffer containing the chart image.
    """
    try:
        # Create figure
        plt.figure(figsize=figsize)
        
        # Create heatmap
        sns.heatmap(data_matrix, annot=annot, fmt=fmt, cmap=cmap)
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        
        # Save the figure to a bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error creating heatmap: {e}")
        return None

def create_scatter_plot_buffer(x_data, y_data, title, xlabel, ylabel, figsize=(10, 6), 
                       color='royalblue', alpha=0.7, size=50, grid=True):
    """
    Create a scatter plot and return it as a buffer.
    
    Args:
        x_data (list): List of x-values.
        y_data (list): List of y-values.
        title (str): The chart title.
        xlabel (str): The x-axis label.
        ylabel (str): The y-axis label.
        figsize (tuple): The figure size (width, height) in inches.
        color (str): Marker color.
        alpha (float): Transparency level.
        size (int): Marker size.
        grid (bool): Whether to show grid lines.
        
    Returns:
        BytesIO: A bytes buffer containing the chart image.
    """
    try:
        # Create figure
        plt.figure(figsize=figsize)
        
        # Create scatter plot
        plt.scatter(x_data, y_data, color=color, alpha=alpha, s=size)
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(grid)
        plt.tight_layout()
        
        # Save the figure to a bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error creating scatter plot: {e}")
        return None

def create_histogram_buffer(data, title, xlabel, ylabel, figsize=(10, 6), bins=20, 
                    color='skyblue', edgecolor='black', grid=True):
    """
    Create a histogram and return it as a buffer.
    
    Args:
        data (list): List of values.
        title (str): The chart title.
        xlabel (str): The x-axis label.
        ylabel (str): The y-axis label.
        figsize (tuple): The figure size (width, height) in inches.
        bins (int): Number of bins.
        color (str): Bar color.
        edgecolor (str): Edge color.
        grid (bool): Whether to show grid lines.
        
    Returns:
        BytesIO: A bytes buffer containing the chart image.
    """
    try:
        # Create figure
        plt.figure(figsize=figsize)
        
        # Create histogram
        plt.hist(data, bins=bins, color=color, edgecolor=edgecolor)
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(grid)
        plt.tight_layout()
        
        # Save the figure to a bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error creating histogram: {e}")
        return None

def create_boxplot_buffer(data_dict, title, xlabel, ylabel, figsize=(10, 6), 
                  vert=True, grid=True, notch=False):
    """
    Create a box plot and return it as a buffer.
    
    Args:
        data_dict (dict): Dictionary with labels as keys and lists of values as values.
        title (str): The chart title.
        xlabel (str): The x-axis label.
        ylabel (str): The y-axis label.
        figsize (tuple): The figure size (width, height) in inches.
        vert (bool): Whether to create a vertical box plot.
        grid (bool): Whether to show grid lines.
        notch (bool): Whether to create notched box plots.
        
    Returns:
        BytesIO: A bytes buffer containing the chart image.
    """
    try:
        # Create figure
        plt.figure(figsize=figsize)
        
        # Create box plot
        plt.boxplot(
            list(data_dict.values()), 
            labels=list(data_dict.keys()), 
            vert=vert, 
            notch=notch, 
            patch_artist=True
        )
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(grid)
        plt.tight_layout()
        
        # Save the figure to a bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error creating box plot: {e}")
        return None
