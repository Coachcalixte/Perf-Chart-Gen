"""
Athlete Performance Report Streamlit App

This streamlined web application allows users to:
1. Upload CSV files with athlete data
2. View athletes' performance metrics with visualizations
3. Generate and download PDF reports

Instructions:
1. Install required packages: pip install streamlit pandas matplotlib reportlab
2. Run the app: streamlit run athlete_report_streamlit.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import base64
from PIL import Image
import tempfile
import sys
import time

# Add the directory of this file to path so we can import the athlete_report module
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Import the report generation functions
from athlete_report import (
    create_athlete_report, 
    create_sprint_chart, 
    create_sprint_30m_chart, 
    create_jump_chart
)

# Set page configuration
st.set_page_config(
    page_title="Athlete Performance Reports",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Custom CSS to hide Streamlit branding and match WordPress theme
st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Hide "Deploy" button */
    .stDeployButton {display: none;}

    /* Customize buttons to match WordPress theme */
    .stButton>button {
        background-color: #007cba;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1.5rem;
        border: none;
        font-weight: 500;
        transition: background-color 0.3s;
    }

    .stButton>button:hover {
        background-color: #005a87;
    }

    /* Customize file uploader */
    .stFileUploader label {
        color: #32373c;
        font-weight: 500;
    }

    /* Customize download buttons */
    .stDownloadButton>button {
        background-color: #007cba;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1.5rem;
        border: none;
        font-weight: 500;
    }

    .stDownloadButton>button:hover {
        background-color: #005a87;
    }

    /* Clean up spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Customize headings */
    h1, h2, h3 {
        color: #32373c;
        font-weight: 600;
    }

    /* Responsive design for mobile */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# No need for a temporary directory anymore as we're using in-memory buffers

def display_preview_charts(athlete):
    """Display preview charts for a selected athlete"""
    
    cols = st.columns(3)
    
    with cols[0]:
        sprint_img = create_sprint_chart(float(athlete['Sprint']))
        st.image(sprint_img, caption="10m Sprint Performance")
    
    with cols[1]:
        sprint_30m_img = create_sprint_30m_chart(float(athlete['Sprint_30m']))
        st.image(sprint_30m_img, caption="30m Sprint Performance")
    
    with cols[2]:
        jump_img = create_jump_chart(float(athlete['CMJ']))
        st.image(jump_img, caption="CMJ Performance")

def generate_pdf_report(athlete):
    """Generate PDF report for an athlete and provide download link"""
    
    with st.spinner('Generating PDF report...'):
        try:
            # Use BytesIO to store the PDF in memory instead of writing to disk
            pdf_buffer = io.BytesIO()
            
            # Modified create_athlete_report to write to buffer
            # We'll use a custom implementation here
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER
            
            # Create the PDF document in memory
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            story = []
            
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
                ["Name:", athlete['Name']],
                ["Weight:", f"{athlete['Weight']} kg"],
                ["Height:", f"{athlete['Height']} cm"]
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
            
            # Create sprint chart
            sprint_img_data = create_sprint_chart(float(athlete['Sprint']))
            sprint_img = Image(sprint_img_data, width=5*inch, height=3.5*inch)
            story.append(sprint_img)
            story.append(Spacer(1, 0.25*inch))

            # Create sprint 30m chart
            sprint_30m_img_data = create_sprint_30m_chart(float(athlete['Sprint_30m']))
            sprint_30m_img = Image(sprint_30m_img_data, width=5*inch, height=3.5*inch)
            story.append(sprint_30m_img)
            story.append(Spacer(1, 0.25*inch))
            
            # Create jump chart
            jump_img_data = create_jump_chart(float(athlete['CMJ']))
            jump_img = Image(jump_img_data, width=5*inch, height=3.5*inch)
            story.append(jump_img)
            
            # Generate the PDF into our buffer
            doc.build(story)
            
            # Reset buffer position to beginning
            pdf_buffer.seek(0)
            
            # Generate filename
            report_filename = f"{athlete['Name'].replace(' ', '_')}_performance_report.pdf"
            
            # Provide download button that will save directly to user's downloads
            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer,
                file_name=report_filename,
                mime="application/pdf",
                key=f"download_{athlete['Name']}"
            )
            
            return True
        
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            return None

def process_csv(df):
    """Process and standardize the CSV data"""
    
    # Check required columns (case-insensitive)
    required_fields = ['Name', 'Weight', 'Height', 'Sprint', 'Sprint_30m', 'CMJ']
    df_columns_lower = [col.lower() for col in df.columns]
    
    # Map columns to expected names
    column_mapping = {}
    for field in required_fields:
        try:
            idx = df_columns_lower.index(field.lower())
            column_mapping[df.columns[idx]] = field
        except ValueError:
            st.error(f"Missing required column: {field}")
            return None
    
    # Rename columns for consistency
    df = df.rename(columns=column_mapping)
    
    # Convert numeric columns
    numeric_cols = ['Weight', 'Height', 'Sprint', 'Sprint_30m', 'CMJ']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Drop rows with missing data
    df = df.dropna(subset=numeric_cols)
    
    return df

def generate_team_reports(df):
    """Generate reports for all athletes in the dataframe directly to a ZIP file in memory"""
    import zipfile
    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER
    
    # Create a BytesIO object to hold our zip file in memory
    zip_buffer = io.BytesIO()
    
    # Create a zip file in memory
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        # Track progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (_, athlete) in enumerate(df.iterrows()):
            status_text.text(f"Generating report for {athlete['Name']}...")
            
            try:
                # Create a PDF in memory for this athlete
                pdf_buffer = io.BytesIO()
                
                # Create the PDF document
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
                story = []
                
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
                    ["Name:", athlete['Name']],
                    ["Weight:", f"{athlete['Weight']} kg"],
                    ["Height:", f"{athlete['Height']} cm"]
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
                
                # Create sprint chart
                sprint_img_data = create_sprint_chart(float(athlete['Sprint']))
                sprint_img = Image(sprint_img_data, width=5*inch, height=3.5*inch)
                story.append(sprint_img)
                story.append(Spacer(1, 0.25*inch))

                # Create sprint 30m chart
                sprint_30m_img_data = create_sprint_30m_chart(float(athlete['Sprint_30m']))
                sprint_30m_img = Image(sprint_30m_img_data, width=5*inch, height=3.5*inch)
                story.append(sprint_30m_img)
                story.append(Spacer(1, 0.25*inch))
                
                # Create jump chart
                jump_img_data = create_jump_chart(float(athlete['CMJ']))
                jump_img = Image(jump_img_data, width=5*inch, height=3.5*inch)
                story.append(jump_img)
                
                # Generate the PDF into buffer
                doc.build(story)
                
                # Reset buffer position
                pdf_buffer.seek(0)
                
                # Add PDF to zip file
                report_filename = f"{athlete['Name'].replace(' ', '_')}_performance_report.pdf"
                zipf.writestr(report_filename, pdf_buffer.getvalue())
                
            except Exception as e:
                st.error(f"Error generating report for {athlete['Name']}: {str(e)}")
            
            # Update progress
            progress = (i + 1) / len(df)
            progress_bar.progress(progress)
        
        status_text.text(f"Generated reports for {len(df)} athletes successfully!")
    
    # Reset zip buffer position
    zip_buffer.seek(0)
    return zip_buffer

# Main app layout
def main():
    st.title("🏃‍♂️ Athlete Performance Report Generator")
    
    st.write("""
    Upload a CSV file with athlete data to generate performance reports.
    
    **Required columns:**
    - Name
    - Weight (kg)
    - Height (cm)
    - Sprint (10m sprint time in seconds)
    - Sprint_30m (30m sprint time in seconds)
    - CMJ (Counter Movement Jump height in cm)
    """)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # Load and process data
            df = pd.read_csv(uploaded_file)
            processed_df = process_csv(df)
            
            if processed_df is not None and not processed_df.empty:
                st.success(f"Found {len(processed_df)} athletes in the CSV file!")
                
                # Create tabs for different views
                tab1, tab2 = st.tabs(["Individual Reports", "Team Reports"])
                
                # Tab 1: Individual athlete view
                with tab1:
                    st.header("Individual Athlete Reports")
                    
                    # Athlete selector
                    selected_athlete_name = st.selectbox(
                        "Select an athlete to view their metrics:", 
                        options=processed_df['Name'].tolist()
                    )
                    
                    # Display selected athlete
                    athlete = processed_df[processed_df['Name'] == selected_athlete_name].iloc[0].to_dict()
                    
                    # Display athlete info
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Weight", f"{athlete['Weight']} kg")
                    col2.metric("Height", f"{athlete['Height']} cm")
                    col3.metric("BMI", f"{athlete['Weight'] / ((athlete['Height']/100)**2):.1f}")
                    
                    # Display performance charts
                    display_preview_charts(athlete)
                    
                    # Generate PDF report
                    st.button("Generate PDF Report", on_click=lambda: generate_pdf_report(athlete))
                
                # Tab 2: Team report generation
                with tab2:
                    st.header("Team Reports")
                    st.write("Generate reports for all athletes in the team.")
                    
                    if st.button("Generate All Reports"):
                        # Generate reports for all athletes directly to a zip file in memory
                        zip_buffer = generate_team_reports(processed_df)
                        
                        if zip_buffer:
                            # Provide download link for the zip file
                            st.download_button(
                                label="Download All Reports (ZIP)",
                                data=zip_buffer,
                                file_name="team_reports.zip",
                                mime="application/zip"
                            )
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()