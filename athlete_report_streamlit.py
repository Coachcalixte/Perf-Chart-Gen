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
    create_jump_chart,
    create_wattbike_chart
)

# Season configuration
SEASON_CONFIG = {
    "OFF Season": {
        "required_columns": ['Name', 'Weight', 'Height', 'Sprint', 'Sprint_30m', 'CMJ'],
        "numeric_columns": ['Weight', 'Height', 'Sprint', 'Sprint_30m', 'CMJ'],
        "charts": ['sprint_10m', 'sprint_30m', 'cmj'],
        "description": "Complete performance assessment with sprints and jump testing"
    },
    "IN Season": {
        "required_columns": ['Name', 'Weight', 'Height', 'CMJ', 'Wattbike_6s'],
        "numeric_columns": ['Weight', 'Height', 'CMJ', 'Wattbike_6s'],
        "charts": ['cmj', 'wattbike'],
        "description": "In-season monitoring with jump and power testing"
    }
}

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

def build_pdf_story(athlete, season_type):
    """
    Build ReportLab story elements for PDF based on season type.

    Args:
        athlete (dict): Athlete data
        season_type (str): "OFF Season" or "IN Season"

    Returns:
        list: ReportLab story elements
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib import colors

    story = []
    styles = getSampleStyleSheet()

    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#007cba'),
        spaceAfter=30,
        alignment=1  # Center
    )

    # Add title
    title_text = f"{season_type} - Athlete Performance Report"
    title = Paragraph(title_text, title_style)
    story.append(title)
    story.append(Spacer(1, 0.3*inch))

    # Athlete info table
    athlete_data = [
        ["Name:", str(athlete['Name'])],
        ["Weight:", f"{athlete['Weight']} kg"],
        ["Height:", f"{athlete['Height']} cm"],
    ]

    athlete_table = Table(athlete_data, colWidths=[1.5*inch, 4*inch])
    athlete_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#32373c')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(athlete_table)
    story.append(Spacer(1, 0.5*inch))

    # Add charts based on season
    if season_type == "OFF Season":
        # 10m Sprint
        sprint_img_data = create_sprint_chart(float(athlete['Sprint']))
        sprint_img = Image(sprint_img_data, width=5*inch, height=3.5*inch)
        story.append(sprint_img)
        story.append(Spacer(1, 0.3*inch))

        # 30m Sprint
        sprint_30m_img_data = create_sprint_30m_chart(float(athlete['Sprint_30m']))
        sprint_30m_img = Image(sprint_30m_img_data, width=5*inch, height=3.5*inch)
        story.append(sprint_30m_img)
        story.append(Spacer(1, 0.3*inch))

        # CMJ
        jump_img_data = create_jump_chart(float(athlete['CMJ']))
        jump_img = Image(jump_img_data, width=5*inch, height=3.5*inch)
        story.append(jump_img)

    else:  # IN Season
        # CMJ
        jump_img_data = create_jump_chart(float(athlete['CMJ']))
        jump_img = Image(jump_img_data, width=5*inch, height=3.5*inch)
        story.append(jump_img)
        story.append(Spacer(1, 0.3*inch))

        # Wattbike
        power_per_kg = float(athlete['Wattbike_6s']) / float(athlete['Weight'])
        wattbike_img_data = create_wattbike_chart(power_per_kg)
        wattbike_img = Image(wattbike_img_data, width=5*inch, height=3.5*inch)
        story.append(wattbike_img)

    return story

def display_preview_charts(athlete, season_type):
    """
    Display preview charts for a selected athlete based on season.

    Args:
        athlete (dict): Athlete data with performance metrics
        season_type (str): "OFF Season" or "IN Season"
    """
    if season_type == "OFF Season":
        # 3-column layout for OFF Season
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

    else:  # IN Season
        # 2-column layout for IN Season
        cols = st.columns(2)

        with cols[0]:
            jump_img = create_jump_chart(float(athlete['CMJ']))
            st.image(jump_img, caption="CMJ Performance")

        with cols[1]:
            # Calculate W/kg from Wattbike_6s power and weight
            power_per_kg = float(athlete['Wattbike_6s']) / float(athlete['Weight'])
            wattbike_img = create_wattbike_chart(power_per_kg)
            st.image(wattbike_img, caption="Wattbike 6s Power Performance")

def generate_pdf_report(athlete, season_type):
    """
    Generate PDF report for an athlete based on season type.

    Args:
        athlete (dict): Athlete data
        season_type (str): "OFF Season" or "IN Season"

    Returns:
        BytesIO or None: PDF buffer or None if error
    """
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.pagesizes import letter

    with st.spinner('Generating PDF report...'):
        try:
            # Create PDF in memory
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

            # Build story using helper function
            story = build_pdf_story(athlete, season_type)

            # Generate PDF
            doc.build(story)
            pdf_buffer.seek(0)

            return pdf_buffer

        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            return None

def process_csv(df, season_type):
    """
    Process and standardize the CSV data based on season type.

    Args:
        df (pd.DataFrame): Raw uploaded DataFrame
        season_type (str): "OFF Season" or "IN Season"

    Returns:
        pd.DataFrame or None: Processed DataFrame or None if validation fails
    """
    config = SEASON_CONFIG[season_type]
    required_fields = config["required_columns"]
    numeric_cols = config["numeric_columns"]

    # Case-insensitive column matching
    df_columns_lower = [col.lower() for col in df.columns]

    # Map uploaded columns to expected names
    column_mapping = {}
    missing_columns = []

    for field in required_fields:
        try:
            idx = df_columns_lower.index(field.lower())
            column_mapping[df.columns[idx]] = field
        except ValueError:
            missing_columns.append(field)

    # Error handling: Missing columns
    if missing_columns:
        st.error(f"❌ Missing required columns for {season_type}: {', '.join(missing_columns)}")
        st.info(f"📋 Expected columns: {', '.join(required_fields)}")
        return None

    # Rename columns for consistency
    df = df.rename(columns=column_mapping)

    # Select only required columns (ignore extra columns)
    df = df[required_fields]

    # Convert numeric columns
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Count invalid rows before dropping
    invalid_rows = df[df[numeric_cols].isna().any(axis=1)]
    if len(invalid_rows) > 0:
        st.warning(f"⚠️ Removed {len(invalid_rows)} rows with invalid numeric data")

    # Drop rows with missing/invalid numeric data
    df = df.dropna(subset=numeric_cols)

    # Validate data ranges
    if len(df) == 0:
        st.error("❌ No valid data rows found after validation")
        return None

    # Success message
    st.success(f"✅ Successfully loaded {len(df)} athlete(s) for {season_type}")

    return df

def generate_team_reports(df, season_type):
    """
    Generate ZIP file containing PDF reports for all athletes.

    Args:
        df (pd.DataFrame): Athlete data
        season_type (str): "OFF Season" or "IN Season"

    Returns:
        BytesIO: ZIP file buffer
    """
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.pagesizes import letter
    import zipfile

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        total_athletes = len(df)

        for idx, (_, athlete) in enumerate(df.iterrows()):
            athlete_dict = athlete.to_dict()

            # Update progress
            progress = (idx + 1) / total_athletes
            progress_bar.progress(progress)
            status_text.text(f"Generating report {idx + 1}/{total_athletes}: {athlete_dict['Name']}")

            try:
                # Create PDF in memory
                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

                # Build story using helper function
                story = build_pdf_story(athlete_dict, season_type)

                # Generate PDF
                doc.build(story)

                # Add to ZIP
                report_filename = f"{athlete_dict['Name'].replace(' ', '_')}_performance_report.pdf"
                zipf.writestr(report_filename, pdf_buffer.getvalue())

            except Exception as e:
                st.warning(f"⚠️ Error generating report for {athlete_dict['Name']}: {str(e)}")
                continue

        # Complete
        progress_bar.progress(1.0)
        status_text.text(f"✅ Generated {total_athletes} reports")
        time.sleep(1)  # Brief pause to show completion
        progress_bar.empty()
        status_text.empty()
    
    # Reset zip buffer position
    zip_buffer.seek(0)
    return zip_buffer

# Main app layout
def main():
    # Title
    st.title("🏃‍♂️ Athlete Performance Reports")

    # === STEP 1: Season Selection ===
    st.subheader("1️⃣ Select Season Type")
    season_type = st.radio(
        "Choose the training season:",
        options=["OFF Season", "IN Season"],
        horizontal=True
    )

    # Display season requirements
    config = SEASON_CONFIG[season_type]
    with st.expander("ℹ️ Required CSV Format"):
        st.write(f"**Columns:** {', '.join(config['required_columns'])}")
        st.write(f"**Description:** {config['description']}")

    st.divider()

    # === STEP 2: File Upload ===
    st.subheader("2️⃣ Upload Athlete Data")
    uploaded_file = st.file_uploader(
        f"Upload CSV file for {season_type}",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            # Parse CSV
            df = pd.read_csv(uploaded_file)
            processed_df = process_csv(df, season_type)
            
            if processed_df is not None:
                # Store in session state
                st.session_state['season_type'] = season_type
                st.session_state['processed_df'] = processed_df

                st.divider()

                # === STEP 3: View Reports ===
                st.subheader("3️⃣ Generate Reports")

                # Create tabs for individual vs team reports
                tab1, tab2 = st.tabs(["Individual Reports", "Team Reports"])

                # --- Tab 1: Individual Reports ---
                with tab1:
                    st.header("Individual Athlete Reports")

                    # Athlete selection
                    selected_athlete_name = st.selectbox(
                        "Select an athlete:",
                        options=processed_df['Name'].tolist()
                    )

                    athlete = processed_df[processed_df['Name'] == selected_athlete_name].iloc[0].to_dict()

                    # Display athlete info
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Weight", f"{athlete['Weight']} kg")
                    col2.metric("Height", f"{athlete['Height']} cm")

                    # Calculate BMI
                    height_m = float(athlete['Height']) / 100
                    bmi = float(athlete['Weight']) / (height_m ** 2)
                    col3.metric("BMI", f"{bmi:.1f}")

                    st.divider()

                    # Display charts
                    st.subheader("Performance Charts")
                    display_preview_charts(athlete, season_type)

                    st.divider()

                    # Generate PDF button
                    if st.button("📄 Generate PDF Report", type="primary"):
                        pdf_buffer = generate_pdf_report(athlete, season_type)

                        if pdf_buffer is not None:
                            report_filename = f"{athlete['Name'].replace(' ', '_')}_performance_report.pdf"

                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=pdf_buffer,
                                file_name=report_filename,
                                mime="application/pdf"
                            )

                # --- Tab 2: Team Reports ---
                with tab2:
                    st.header("Team Reports")
                    st.write(f"Generate PDF reports for all {len(processed_df)} athletes")

                    if st.button("📦 Generate All Reports", type="primary"):
                        zip_buffer = generate_team_reports(processed_df, season_type)

                        st.download_button(
                            label="⬇️ Download All Reports (ZIP)",
                            data=zip_buffer,
                            file_name=f"{season_type.replace(' ', '_')}_team_reports.zip",
                            mime="application/zip"
                        )

        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

    else:
        st.info("👆 Please upload a CSV file to get started")

if __name__ == "__main__":
    main()