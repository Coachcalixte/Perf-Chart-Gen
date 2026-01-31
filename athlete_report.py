# athlete_report.py
"""
Module for creating athlete performance reports with visualizations.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def create_sprint_chart(time_value, test_name="10m Sprint", unit="s"):
    """
    Create a bar chart for sprint time with color-coded background.
    
    Parameters:
    time_value (float): Time value in seconds
    test_name (str): Name of the sprint test
    unit (str): Unit of measurement
    
    Returns:
    BytesIO: Image data in BytesIO buffer
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Set up the color regions based on performance
    colors = [(0, 0.8, 0), (0.9, 0.9, 0), (1, 0.5, 0), (0.8, 0, 0)]  # green, yellow, orange, red
    positions = [1.65, 1.80, 1.85, 1.91, 2.0]  # Performance thresholds
    
    # Create a rectangle for each color region
    for i in range(len(colors)):
        height = positions[i+1] - positions[i]
        rect = Rectangle((0, positions[i]), 1, height, color=colors[i], alpha=0.3)
        ax.add_patch(rect)
    
    # Create a bar chart for the performance
    bar_width = 0.5
    ax.bar(0.5, time_value, width=bar_width, color='blue', edgecolor='black')
    
    # Set chart limits and labels
    ax.set_xlim(0, 1)
    ax.set_ylim(positions[0], positions[-1])
    ax.set_ylabel(f"Time ({unit})")
    ax.set_title(f"{test_name} Performance")
    
    # Remove x-axis ticks, only show test name
    ax.set_xticks([0.5])
    ax.set_xticklabels([test_name])
    
    # Add performance value on top of the bar
    ax.text(0.5, time_value + 0.01, f"{time_value}", ha='center', fontweight='bold')
    
    # Add performance categories as annotations
    ax.text(0.90, 1.77, "Excellent", fontsize=9, ha='right')
    ax.text(0.90, 1.82, "Good", fontsize=9, ha='right')
    ax.text(0.90, 1.88, "Average", fontsize=9, ha='right')
    ax.text(0.90, 1.95, "Poor", fontsize=9, ha='right')
    
    plt.tight_layout()
    
    # Save to BytesIO object instead of file
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=150, bbox_inches="tight")
    img_data.seek(0)  # Move to the beginning of BytesIO
    plt.close(fig)  # Close the figure to free memory
    
    return img_data


def create_sprint_30m_chart(time_value, test_name="30m Sprint", unit="s"):
    """
    Create a bar chart for sprint time with color-coded background.
    
    Parameters:
    time_value (float): Time value in seconds
    test_name (str): Name of the sprint test
    unit (str): Unit of measurement
    
    Returns:
    BytesIO: Image data in BytesIO buffer
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Set up the color regions based on performance
    colors = [(0, 0.8, 0), (0.9, 0.9, 0), (1, 0.5, 0), (0.8, 0, 0)]  # green, yellow, orange, red
    positions = [4.00, 4.17, 4.30, 4.45, 5.00]  # Performance thresholds
    
    # Create a rectangle for each color region
    for i in range(len(colors)):
        height = positions[i+1] - positions[i]
        rect = Rectangle((0, positions[i]), 1, height, color=colors[i], alpha=0.3)
        ax.add_patch(rect)
    
    # Create a bar chart for the performance
    bar_width = 0.5
    ax.bar(0.5, time_value, width=bar_width, color='blue', edgecolor='black')
    
    # Set chart limits and labels
    ax.set_xlim(0, 1)
    ax.set_ylim(positions[0], positions[-1])
    ax.set_ylabel(f"Time ({unit})")
    ax.set_title(f"{test_name} Performance")
    
    # Remove x-axis ticks, only show test name
    ax.set_xticks([0.5])
    ax.set_xticklabels([test_name])
    
    # Add performance value on top of the bar
    ax.text(0.5, time_value + 0.01, f"{time_value}", ha='center', fontweight='bold')
    
    # Add performance categories as annotations
    ax.text(0.90, 4.08, "Excellent", fontsize=9, ha='right')
    ax.text(0.90, 4.21, "Good", fontsize=9, ha='right')
    ax.text(0.90, 4.38, "Average", fontsize=9, ha='right')
    ax.text(0.90, 4.52, "Poor", fontsize=9, ha='right')
    
    plt.tight_layout()
    
    # Save to BytesIO object instead of file
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=150, bbox_inches="tight")
    img_data.seek(0)  # Move to the beginning of BytesIO
    plt.close(fig)  # Close the figure to free memory
    
    return img_data

def create_jump_chart(height_value, test_name="CMJ", unit="cm"):
    """
    Create a bar chart for jump height with color-coded background.
    
    Parameters:
    height_value (float): Height value in cm
    test_name (str): Name of the jump test
    unit (str): Unit of measurement
    
    Returns:
    BytesIO: Image data in BytesIO buffer
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Set up the color regions based on performance
    colors = [(0.8, 0, 0), (1, 0.5, 0), (0.9, 0.9, 0), (0, 0.8, 0)]  # red, orange, yellow, green
    positions = [30, 38, 45, 52, 60]  # Performance thresholds
    
    # Create a rectangle for each color region
    for i in range(len(colors)):
        height = positions[i+1] - positions[i]
        rect = Rectangle((0, positions[i]), 1, height, color=colors[i], alpha=0.3)
        ax.add_patch(rect)
    
    # Create a bar chart for the performance
    bar_width = 0.5
    ax.bar(0.5, height_value, width=bar_width, color='blue', edgecolor='black')
    
    # Set chart limits and labels
    ax.set_xlim(0, 1)
    ax.set_ylim(positions[0], positions[-1])
    ax.set_ylabel(f"Height ({unit})")
    ax.set_title(f"{test_name} Performance")
    
    # Remove x-axis ticks, only show test name
    ax.set_xticks([0.5])
    ax.set_xticklabels([test_name])
    
    # Add performance value on top of the bar
    ax.text(0.5, height_value + 0.5, f"{height_value}", ha='center', fontweight='bold')
    
    # Add performance categories as annotations
    ax.text(0.90, 34, "Poor", fontsize=9, ha='right')
    ax.text(0.90, 42, "Average", fontsize=9, ha='right')
    ax.text(0.90, 48, "Good", fontsize=9, ha='right')
    ax.text(0.90, 56, "Excellent", fontsize=9, ha='right')
    
    plt.tight_layout()
    
    # Save to BytesIO object instead of file
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=150, bbox_inches="tight")
    img_data.seek(0)  # Move to the beginning of BytesIO
    plt.close(fig)  # Close the figure to free memory
    
    return img_data

def create_wattbike_chart(power_per_kg, test_name="Wattbike 6s", unit="W/kg"):
    """
    Create a Wattbike power output chart with performance zones.

    Args:
        power_per_kg (float): Power output in watts per kilogram
        test_name (str): Name of the test for the chart title
        unit (str): Unit of measurement for axis labels

    Returns:
        BytesIO: Image buffer containing the chart
    """
    fig, ax = plt.subplots(figsize=(6, 4))

    # Define performance zones (W/kg)
    # Colors: Red (Need work) → Orange (Average) → Yellow (Good) → Green (WOW)
    colors = [(0.8, 0, 0), (1, 0.5, 0), (0.9, 0.9, 0), (0, 0.8, 0)]
    positions = [0, 15, 20, 25, 35]  # Zone boundaries

    # Draw color-coded background zones
    for i in range(len(colors)):
        height = positions[i+1] - positions[i]
        rect = Rectangle((0, positions[i]), 1, height, color=colors[i], alpha=0.3)
        ax.add_patch(rect)

    # Add zone labels
    ax.text(0.90, 10, "Need to work", fontsize=9, ha='right', va='center')
    ax.text(0.90, 17.5, "Average", fontsize=9, ha='right', va='center')
    ax.text(0.90, 22.5, "Good", fontsize=9, ha='right', va='center')
    ax.text(0.90, 30, "WOW", fontsize=9, ha='right', va='center')

    # Draw athlete's performance bar
    bar_width = 0.5
    ax.bar(0.5, power_per_kg, width=bar_width, color='blue', edgecolor='black', linewidth=2)

    # Add value label on bar
    ax.text(0.5, power_per_kg + 1, f"{power_per_kg:.1f}",
            ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Configure axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 35)
    ax.set_ylabel(f'{test_name} ({unit})', fontsize=10)
    ax.set_title(f'{test_name} Performance', fontsize=12, fontweight='bold')
    ax.set_xticks([])  # Hide x-axis
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    # Save to BytesIO object instead of file
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=150, bbox_inches="tight")
    img_data.seek(0)  # Move to the beginning of BytesIO
    plt.close(fig)  # Close the figure to free memory

    return img_data

def create_yoyo_chart(level_value, test_name="Yoyo Test", unit="level"):
    """
    Yoyo test chart (higher is better).

    Performance zones:
    - Below 17.0: Below Average (Red)
    - 17.1-18.0: Average (Orange)
    - 18.1-19.0: Good (Yellow)
    - 19.1+: Excellent (Green)

    Args:
        level_value (float): Yoyo test level reached
        test_name (str): Name for chart title
        unit (str): Unit label

    Returns:
        BytesIO: Image buffer
    """
    fig, ax = plt.subplots(figsize=(6, 4))

    # Higher is better → red bottom, green top (like CMJ)
    colors = [(0.8, 0, 0), (1, 0.5, 0), (0.9, 0.9, 0), (0, 0.8, 0)]
    positions = [15.0, 17.0, 18.0, 19.0, 21.0]

    # Draw zones
    for i in range(len(colors)):
        height = positions[i+1] - positions[i]
        rect = Rectangle((0, positions[i]), 1, height, color=colors[i], alpha=0.3)
        ax.add_patch(rect)

    # Performance bar
    bar_width = 0.5
    ax.bar(0.5, level_value, width=bar_width, color='blue', edgecolor='black')

    # Configuration
    ax.set_xlim(0, 1)
    ax.set_ylim(positions[0], positions[-1])
    ax.set_ylabel(f"Level ({unit})")
    ax.set_title(f"{test_name} Performance")
    ax.set_xticks([0.5])
    ax.set_xticklabels([test_name])

    # Value label
    ax.text(0.5, level_value + 0.1, f"{level_value:.1f}", ha='center', fontweight='bold')

    # Zone labels (Poor to Excellent, bottom to top)
    ax.text(0.90, 16.0, "Below Average", fontsize=9, ha='right')
    ax.text(0.90, 17.5, "Average", fontsize=9, ha='right')
    ax.text(0.90, 18.5, "Good", fontsize=9, ha='right')
    ax.text(0.90, 20.0, "Excellent", fontsize=9, ha='right')

    plt.tight_layout()

    # Save to BytesIO
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=150, bbox_inches="tight")
    img_data.seek(0)
    plt.close(fig)

    return img_data

def create_stop_go_chart(time_value, test_name="Stop & Go", unit="s"):
    """
    Stop & Go test chart (lower is better).

    Performance zones:
    - ≤4.54s: Excellent (Green)
    - 4.55-4.65: Good (Yellow)
    - 4.66-4.79: Average (Orange)
    - ≥4.80s: Below Average (Red)

    Args:
        time_value (float): Stop & Go time in seconds
        test_name (str): Name for chart title
        unit (str): Unit label

    Returns:
        BytesIO: Image buffer
    """
    fig, ax = plt.subplots(figsize=(6, 4))

    # Lower is better → green bottom, red top (like Sprint)
    colors = [(0, 0.8, 0), (0.9, 0.9, 0), (1, 0.5, 0), (0.8, 0, 0)]
    positions = [4.40, 4.54, 4.65, 4.79, 5.00]

    # Draw zones
    for i in range(len(colors)):
        height = positions[i+1] - positions[i]
        rect = Rectangle((0, positions[i]), 1, height, color=colors[i], alpha=0.3)
        ax.add_patch(rect)

    # Performance bar
    bar_width = 0.5
    ax.bar(0.5, time_value, width=bar_width, color='blue', edgecolor='black')

    # Configuration
    ax.set_xlim(0, 1)
    ax.set_ylim(positions[0], positions[-1])
    ax.set_ylabel(f"Time ({unit})")
    ax.set_title(f"{test_name} Performance")
    ax.set_xticks([0.5])
    ax.set_xticklabels([test_name])

    # Value label
    ax.text(0.5, time_value + 0.02, f"{time_value:.2f}", ha='center', fontweight='bold')

    # Zone labels (Excellent to Poor, bottom to top)
    ax.text(0.90, 4.47, "Excellent", fontsize=9, ha='right')
    ax.text(0.90, 4.60, "Good", fontsize=9, ha='right')
    ax.text(0.90, 4.72, "Average", fontsize=9, ha='right')
    ax.text(0.90, 4.89, "Below Average", fontsize=9, ha='right')

    plt.tight_layout()

    # Save to BytesIO
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=150, bbox_inches="tight")
    img_data.seek(0)
    plt.close(fig)

    return img_data

def create_broad_jump_chart(distance_value, test_name="Broad Jump", unit="cm"):
    """
    Broad Jump test chart (higher is better).

    Performance zones:
    - <250cm: Below Average (Red)
    - 250-259cm: Average (Orange)
    - 260-269cm: Good (Yellow)
    - ≥270cm: Excellent (Green)

    Args:
        distance_value (float): Broad jump distance in centimeters
        test_name (str): Name for chart title
        unit (str): Unit label

    Returns:
        BytesIO: Image buffer
    """
    fig, ax = plt.subplots(figsize=(6, 4))

    # Higher is better → red bottom, green top (like CMJ)
    colors = [(0.8, 0, 0), (1, 0.5, 0), (0.9, 0.9, 0), (0, 0.8, 0)]
    positions = [230, 250, 260, 270, 290]

    # Draw zones
    for i in range(len(colors)):
        height = positions[i+1] - positions[i]
        rect = Rectangle((0, positions[i]), 1, height, color=colors[i], alpha=0.3)
        ax.add_patch(rect)

    # Performance bar
    bar_width = 0.5
    ax.bar(0.5, distance_value, width=bar_width, color='blue', edgecolor='black')

    # Configuration
    ax.set_xlim(0, 1)
    ax.set_ylim(positions[0], positions[-1])
    ax.set_ylabel(f"Distance ({unit})")
    ax.set_title(f"{test_name} Performance")
    ax.set_xticks([0.5])
    ax.set_xticklabels([test_name])

    # Value label
    ax.text(0.5, distance_value + 2, f"{distance_value:.1f}", ha='center', fontweight='bold')

    # Zone labels (Poor to Excellent, bottom to top)
    ax.text(0.90, 240, "Below Average", fontsize=9, ha='right')
    ax.text(0.90, 255, "Average", fontsize=9, ha='right')
    ax.text(0.90, 265, "Good", fontsize=9, ha='right')
    ax.text(0.90, 280, "Excellent", fontsize=9, ha='right')

    plt.tight_layout()

    # Save to BytesIO
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=150, bbox_inches="tight")
    img_data.seek(0)
    plt.close(fig)

    return img_data

def create_athlete_report(athlete_name, weight, height, sprint_time, sprint_30m_time, jump_height, output_filename=None, output_dir=None):
    """
    Create a comprehensive PDF report for an athlete with personal info and performance charts
    
    Parameters:
    athlete_name (str): Name of the athlete
    weight (float): Weight in kg
    height (float): Height in cm
    sprint_time (float): 10m sprint time in seconds
    jump_height (float): CMJ height in cm
    output_filename (str, optional): Name for the output PDF file. If None, will use {athlete_name}_performance_report.pdf
    output_dir (str, optional): Directory to save the report in. If None, uses current directory.
    """
    # Generate filename based on athlete name if not provided
    if output_filename is None:
        # Replace spaces with underscores and ensure valid filename
        safe_name = athlete_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        output_filename = f"{safe_name}_performance_report.pdf"
    
    # Handle output directory
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
    else:
        output_path = output_filename
    
    # Create the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []  # Container for elements to add to the document
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=12
    )
    
    # Add report title
    title = Paragraph("Athlete Performance Report", title_style)
    story.append(title)
    story.append(Spacer(1, 0.25*inch))
    
    # Add athlete information section
    story.append(Paragraph("Athlete Information", subtitle_style))
    
    # Create a table for athlete information
    athlete_data = [
        ["Name:", athlete_name],
        ["Weight:", f"{weight} kg"],
        ["Height:", f"{height} cm"]
    ]
    
    athlete_table = Table(athlete_data, colWidths=[1.5*inch, 4*inch])
    athlete_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(athlete_table)
    story.append(Spacer(1, 0.5*inch))
    
    # Add performance section title
    story.append(Paragraph("Performance Metrics", subtitle_style))
    
    # Create and add sprint chart
    sprint_img_data = create_sprint_chart(sprint_time)
    sprint_img = Image(sprint_img_data, width=5*inch, height=3.5*inch)
    story.append(sprint_img)
    story.append(Spacer(1, 0.25*inch))

    # Create and add sprint 30m chart
    sprint_img_data = create_sprint_30m_chart(sprint_30m_time)
    sprint_img = Image(sprint_img_data, width=5*inch, height=3.5*inch)
    story.append(sprint_img)
    story.append(Spacer(1, 0.25*inch))
    
    # Create and add jump chart
    jump_img_data = create_jump_chart(jump_height)
    jump_img = Image(jump_img_data, width=5*inch, height=3.5*inch)
    story.append(jump_img)
    
    # Generate the PDF
    doc.build(story)
    print(f"Report generated: {output_path}")
    
    return output_path