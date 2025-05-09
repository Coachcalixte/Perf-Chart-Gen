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
    ax.text(0.85, 1.77, "Excellent", fontsize=9, ha='right')
    ax.text(0.85, 1.82, "Good", fontsize=9, ha='right')
    ax.text(0.85, 1.88, "Average", fontsize=9, ha='right')
    ax.text(0.85, 1.95, "Poor", fontsize=9, ha='right')
    
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
    ax.text(0.85, 4.08, "Excellent", fontsize=9, ha='right')
    ax.text(0.85, 4.21, "Good", fontsize=9, ha='right')
    ax.text(0.85, 4.38, "Average", fontsize=9, ha='right')
    ax.text(0.85, 4.52, "Poor", fontsize=9, ha='right')
    
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
    ax.text(0.85, 34, "Poor", fontsize=9, ha='right')
    ax.text(0.85, 42, "Average", fontsize=9, ha='right')
    ax.text(0.85, 48, "Good", fontsize=9, ha='right')
    ax.text(0.85, 56, "Excellent", fontsize=9, ha='right')
    
    plt.tight_layout()
    
    # Save to BytesIO object instead of file
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=150, bbox_inches="tight")
    img_data.seek(0)  # Move to the beginning of BytesIO
    plt.close(fig)  # Close the figure to free memory
    
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