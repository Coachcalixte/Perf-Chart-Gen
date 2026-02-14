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
    create_wattbike_chart,
    create_yoyo_chart,
    create_stop_go_chart,
    create_broad_jump_chart
)

# Import security module
from security import (
    validate_csv_security,
    validate_email,
    check_upload_limit,
    check_pdf_limit,
    check_team_report_limit,
    record_upload,
    record_pdf,
    record_team_report,
    log_upload,
    log_pdf_generation,
    log_team_report,
    log_error,
    save_email,
    get_session_id
)

# Season configuration
SEASON_CONFIG = {
    "OFF Season": {
        "required_columns": ['Name'],  # ONLY Name is required
        "optional_columns": {
            # Anthropometric
            "Weight": {"numeric": True, "unit": "kg"},
            "Height": {"numeric": True, "unit": "cm"},
            # Performance tests
            "Sprint": {"numeric": True, "unit": "s", "chart": "sprint_10m"},
            "Sprint_30m": {"numeric": True, "unit": "s", "chart": "sprint_30m"},
            "CMJ": {"numeric": True, "unit": "cm", "chart": "cmj"},
            "BroadJump": {"numeric": True, "unit": "cm", "chart": "broad_jump"},
            "Yoyo": {"numeric": True, "unit": "level", "chart": "yoyo"},
            "StopGo": {"numeric": True, "unit": "s", "chart": "stop_go"}
        },
        "description": "Performance assessment with all tests optional"
    },
    "IN Season": {
        "required_columns": ['Name'],  # ONLY Name is required
        "optional_columns": {
            # Anthropometric
            "Weight": {"numeric": True, "unit": "kg"},
            "Height": {"numeric": True, "unit": "cm"},
            # Performance tests
            "CMJ": {"numeric": True, "unit": "cm", "chart": "cmj"},
            "Wattbike_6s": {"numeric": True, "unit": "W", "chart": "wattbike"}
        },
        "description": "In-season monitoring with all tests optional"
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

def build_pdf_story(athlete, season_type, available_columns):
    """
    Build ReportLab story elements for PDF based on season type and available data.

    Args:
        athlete (dict): Athlete data
        season_type (str): "OFF Season" or "IN Season"
        available_columns (dict): Which columns are available

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

    # Build dynamic athlete info table
    athlete_data = [["Name:", str(athlete['Name'])]]

    if available_columns.get('Weight', False):
        athlete_data.append(["Weight:", f"{athlete['Weight']} kg"])

    if available_columns.get('Height', False):
        athlete_data.append(["Height:", f"{athlete['Height']} cm"])

    # Add BMI if both Weight and Height available
    if available_columns.get('Weight', False) and available_columns.get('Height', False):
        height_m = float(athlete['Height']) / 100
        bmi = float(athlete['Weight']) / (height_m ** 2)
        athlete_data.append(["BMI:", f"{bmi:.1f}"])

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

    # Track if any charts were added
    charts_added = False

    # Add charts based on season and available data
    if season_type == "OFF Season":
        # 10m Sprint
        if available_columns.get('Sprint', False):
            sprint_img_data = create_sprint_chart(float(athlete['Sprint']))
            sprint_img = Image(sprint_img_data, width=5*inch, height=3.5*inch)
            story.append(sprint_img)
            story.append(Spacer(1, 0.3*inch))
            charts_added = True

        # 30m Sprint
        if available_columns.get('Sprint_30m', False):
            sprint_30m_img_data = create_sprint_30m_chart(float(athlete['Sprint_30m']))
            sprint_30m_img = Image(sprint_30m_img_data, width=5*inch, height=3.5*inch)
            story.append(sprint_30m_img)
            story.append(Spacer(1, 0.3*inch))
            charts_added = True

        # CMJ
        if available_columns.get('CMJ', False):
            jump_img_data = create_jump_chart(float(athlete['CMJ']))
            jump_img = Image(jump_img_data, width=5*inch, height=3.5*inch)
            story.append(jump_img)
            story.append(Spacer(1, 0.3*inch))
            charts_added = True

        # Broad Jump
        if available_columns.get('BroadJump', False):
            broad_jump_img_data = create_broad_jump_chart(float(athlete['BroadJump']))
            broad_jump_img = Image(broad_jump_img_data, width=5*inch, height=3.5*inch)
            story.append(broad_jump_img)
            story.append(Spacer(1, 0.3*inch))
            charts_added = True

        # Yoyo Test
        if available_columns.get('Yoyo', False):
            yoyo_img_data = create_yoyo_chart(float(athlete['Yoyo']))
            yoyo_img = Image(yoyo_img_data, width=5*inch, height=3.5*inch)
            story.append(yoyo_img)
            story.append(Spacer(1, 0.3*inch))
            charts_added = True

        # Stop & Go Test
        if available_columns.get('StopGo', False):
            stopgo_img_data = create_stop_go_chart(float(athlete['StopGo']))
            stopgo_img = Image(stopgo_img_data, width=5*inch, height=3.5*inch)
            story.append(stopgo_img)
            charts_added = True

    else:  # IN Season
        # CMJ
        if available_columns.get('CMJ', False):
            jump_img_data = create_jump_chart(float(athlete['CMJ']))
            jump_img = Image(jump_img_data, width=5*inch, height=3.5*inch)
            story.append(jump_img)
            story.append(Spacer(1, 0.3*inch))
            charts_added = True

        # Wattbike (requires both Wattbike_6s and Weight)
        if available_columns.get('Wattbike_6s', False) and available_columns.get('Weight', False):
            power_per_kg = float(athlete['Wattbike_6s']) / float(athlete['Weight'])
            wattbike_img_data = create_wattbike_chart(power_per_kg)
            wattbike_img = Image(wattbike_img_data, width=5*inch, height=3.5*inch)
            story.append(wattbike_img)
            charts_added = True

    # Add note if no charts available
    if not charts_added:
        note_style = ParagraphStyle(
            'Note',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            alignment=1
        )
        note = Paragraph("No performance test data available for this athlete", note_style)
        story.append(note)

    return story

def display_preview_charts(athlete, season_type, available_columns):
    """
    Display charts dynamically based on available data.

    Args:
        athlete (dict): Athlete data
        season_type (str): Season type
        available_columns (dict): Which columns are available
    """
    # Determine which charts to show
    charts_to_show = []
    chart_functions = {}

    if season_type == "OFF Season":
        # Map column to chart function
        if available_columns.get('Sprint', False):
            charts_to_show.append('Sprint')
            chart_functions['Sprint'] = (create_sprint_chart, float(athlete['Sprint']), "10m Sprint")

        if available_columns.get('Sprint_30m', False):
            charts_to_show.append('Sprint_30m')
            chart_functions['Sprint_30m'] = (create_sprint_30m_chart, float(athlete['Sprint_30m']), "30m Sprint")

        if available_columns.get('CMJ', False):
            charts_to_show.append('CMJ')
            chart_functions['CMJ'] = (create_jump_chart, float(athlete['CMJ']), "CMJ")

        if available_columns.get('BroadJump', False):
            charts_to_show.append('BroadJump')
            chart_functions['BroadJump'] = (create_broad_jump_chart, float(athlete['BroadJump']), "Broad Jump")

        if available_columns.get('Yoyo', False):
            charts_to_show.append('Yoyo')
            chart_functions['Yoyo'] = (create_yoyo_chart, float(athlete['Yoyo']), "Yoyo Test")

        if available_columns.get('StopGo', False):
            charts_to_show.append('StopGo')
            chart_functions['StopGo'] = (create_stop_go_chart, float(athlete['StopGo']), "Stop & Go")

    else:  # IN Season
        if available_columns.get('CMJ', False):
            charts_to_show.append('CMJ')
            chart_functions['CMJ'] = (create_jump_chart, float(athlete['CMJ']), "CMJ")

        if available_columns.get('Wattbike_6s', False) and available_columns.get('Weight', False):
            power_per_kg = float(athlete['Wattbike_6s']) / float(athlete['Weight'])
            charts_to_show.append('Wattbike')
            chart_functions['Wattbike'] = (create_wattbike_chart, power_per_kg, "Wattbike 6s")

    # If no charts available, show message
    if not charts_to_show:
        st.warning("⚠️ No performance test data available for this athlete")
        return

    # Create dynamic column layout
    cols = st.columns(len(charts_to_show))

    # Display charts
    for idx, chart_name in enumerate(charts_to_show):
        with cols[idx]:
            chart_func, value, caption = chart_functions[chart_name]
            img = chart_func(value)
            st.image(img, caption=f"{caption} Performance")

def generate_pdf_report(athlete, season_type, available_columns):
    """
    Generate PDF report for an athlete based on season type and available data.

    Args:
        athlete (dict): Athlete data
        season_type (str): "OFF Season" or "IN Season"
        available_columns (dict): Which columns are available

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
            story = build_pdf_story(athlete, season_type, available_columns)

            # Generate PDF
            doc.build(story)
            pdf_buffer.seek(0)

            return pdf_buffer

        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            return None

def normalize_column_name(col_name):
    """
    Normalize column name for flexible matching.
    Removes special characters, extra spaces, and converts to lowercase.
    """
    import re
    # Convert to lowercase
    normalized = col_name.lower()
    # Remove content in parentheses (units, etc.)
    normalized = re.sub(r'\([^)]*\)', '', normalized)
    # Remove special characters but keep spaces
    normalized = re.sub(r'[^\w\s]', '', normalized)
    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized)
    # Remove leading/trailing spaces
    normalized = normalized.strip()
    # Replace spaces with underscores for multi-word fields
    normalized = normalized.replace(' ', '_')
    return normalized

def find_matching_column(target_field, df_columns):
    """
    Find a column that matches the target field, handling common variations.

    Args:
        target_field (str): The field we're looking for (e.g., 'Sprint_30m')
        df_columns (list): List of column names from the CSV

    Returns:
        str or None: The actual column name from CSV, or None if not found
    """
    # Normalize target field
    target_normalized = normalize_column_name(target_field)

    # Also try common variations
    variations = [target_normalized]

    # Handle specific common variations
    if target_field == 'Sprint_30m':
        variations.extend(['sprint_30m', 'sprint30m', 'sprint_30'])
    elif target_field == 'StopGo':
        variations.extend(['stopgo', 'stop_go', 'stop_and_go', 'stop__go'])
    elif target_field == 'Yoyo':
        variations.extend(['yoyo', 'yo_yo', 'yoyo_test'])
    elif target_field == 'BroadJump':
        variations.extend(['broadjump', 'broad_jump', 'long_jump', 'longjump'])

    # Check each column in the dataframe
    for col in df_columns:
        col_normalized = normalize_column_name(col)
        if col_normalized in variations:
            return col

    return None

def process_csv(df, season_type):
    """
    Process CSV with fully optional columns (only Name required).
    Handles flexible column name matching (e.g., "Weight (kg)" matches "Weight").

    Args:
        df (pd.DataFrame): Raw uploaded DataFrame
        season_type (str): "OFF Season" or "IN Season"

    Returns:
        tuple: (processed_df, available_columns_dict) or (None, None) if validation fails
        available_columns_dict: {'Weight': True, 'Sprint': True, 'Yoyo': False, ...}
    """
    config = SEASON_CONFIG[season_type]
    required_fields = config["required_columns"]  # Just ['Name']
    optional_fields_config = config["optional_columns"]

    column_mapping = {}
    missing_required = []
    available_columns = {}

    # Check REQUIRED columns (only Name)
    for field in required_fields:
        matched_col = find_matching_column(field, df.columns)
        if matched_col:
            column_mapping[matched_col] = field
        else:
            missing_required.append(field)

    # FAIL if Name is missing
    if missing_required:
        st.error(f"❌ Missing required column: Name")
        return None, None

    # Detect OPTIONAL columns with flexible matching
    for field, metadata in optional_fields_config.items():
        matched_col = find_matching_column(field, df.columns)
        if matched_col:
            column_mapping[matched_col] = field
            available_columns[field] = True
        else:
            available_columns[field] = False

    # Info message for available tests
    available_tests = [col for col, avail in available_columns.items()
                       if avail and optional_fields_config[col].get("chart")]
    if available_tests:
        st.info(f"📊 Available tests: {', '.join(available_tests)}")
    else:
        st.warning("⚠️ No performance test data found in CSV. Only athlete names will be displayed.")

    # Rename columns
    df = df.rename(columns=column_mapping)

    # Select only columns that exist
    existing_columns = ['Name'] + [col for col, avail in available_columns.items() if avail]
    df = df[existing_columns]

    # Convert numeric columns (only those that exist and are marked numeric)
    numeric_cols = [col for col, avail in available_columns.items()
                    if avail and optional_fields_config[col].get("numeric")]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with invalid numeric data
    if numeric_cols:
        invalid_rows = df[df[numeric_cols].isna().any(axis=1)]
        if len(invalid_rows) > 0:
            st.warning(f"⚠️ Removed {len(invalid_rows)} rows with invalid data")

        df = df.dropna(subset=numeric_cols)

    # Validation
    if len(df) == 0:
        st.error("❌ No valid athlete rows found")
        return None, None

    st.success(f"✅ Loaded {len(df)} athlete(s) for {season_type}")

    return df, available_columns

def generate_team_reports(df, season_type, available_columns):
    """
    Generate ZIP file containing PDF reports for all athletes.

    Args:
        df (pd.DataFrame): Athlete data
        season_type (str): "OFF Season" or "IN Season"
        available_columns (dict): Which columns are available

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
                story = build_pdf_story(athlete_dict, season_type, available_columns)

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

    # Initialize session ID for tracking
    get_session_id(st.session_state)

    # === SIDEBAR: Optional Email Collection ===
    with st.sidebar:
        st.header("Stay Updated")

        # Check if email already submitted this session
        if st.session_state.get('email_submitted', False):
            st.success("Thanks for subscribing!")
        else:
            st.write("Get notified about new features and performance tips.")

            with st.form("email_form"):
                email = st.text_input("Email address (optional)", placeholder="your@email.com")
                consent = st.checkbox("I agree to receive occasional updates", value=True)
                submitted = st.form_submit_button("Subscribe")

                if submitted and email:
                    is_valid, error_msg = validate_email(email)
                    if is_valid:
                        if save_email(email, st.session_state, consent):
                            st.session_state['email_submitted'] = True
                            st.success("Thanks! You're subscribed.")
                            st.rerun()
                        else:
                            st.error("Could not save email. Please try again.")
                    else:
                        st.error(error_msg)

        st.divider()
        st.caption("Your data is processed securely and never shared.")

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
        st.write(f"**Description:** {config['description']}")
        st.write("")

        # Show required columns
        st.write("**Required Columns:**")
        st.write(f"• {', '.join(config['required_columns'])}")

        # Show optional columns if they exist
        optional_cols = config.get('optional_columns', {})
        if optional_cols:
            st.write("")
            st.write("**Optional Columns:**")

            # Separate anthropometric data from test data
            anthropometric = []
            tests = []

            for col_name, col_metadata in optional_cols.items():
                chart_name = col_metadata.get('chart', '')
                if chart_name:
                    # This is a test that generates a chart
                    chart_display = chart_name.replace('_', ' ').title()
                    tests.append(f"• {col_name} → {chart_display} chart")
                else:
                    # This is anthropometric data
                    unit = col_metadata.get('unit', '')
                    if unit:
                        anthropometric.append(f"• {col_name} ({unit})")
                    else:
                        anthropometric.append(f"• {col_name}")

            # Display anthropometric data first
            if anthropometric:
                for item in anthropometric:
                    st.write(item)

            # Then display tests
            if tests:
                if anthropometric:
                    st.write("")
                    st.write("**Optional Performance Tests:**")
                for item in tests:
                    st.write(item)

    st.divider()

    # === STEP 2: File Upload ===
    st.subheader("2️⃣ Upload Athlete Data")

    # Check rate limit before showing uploader
    upload_allowed, upload_error = check_upload_limit(st.session_state)
    if not upload_allowed:
        st.error(f"⏱️ {upload_error}")
        st.stop()

    uploaded_file = st.file_uploader(
        f"Upload CSV file for {season_type}",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            # Get file size for security validation
            file_size = uploaded_file.size

            # Parse CSV
            df = pd.read_csv(uploaded_file)

            # Security validation
            is_valid, security_error, df = validate_csv_security(df, file_size)
            if not is_valid:
                st.error(f"🔒 Security check failed: {security_error}")
                log_error(st.session_state, "csv_security", security_error)
                st.stop()

            # Record the upload for rate limiting
            record_upload(st.session_state)

            processed_df, available_columns = process_csv(df, season_type)

            if processed_df is not None and available_columns is not None:
                # Store in session state
                st.session_state['season_type'] = season_type
                st.session_state['processed_df'] = processed_df
                st.session_state['available_columns'] = available_columns

                # Log the successful upload
                available_tests = [col for col, avail in available_columns.items() if avail]
                log_upload(st.session_state, season_type, len(processed_df), available_tests)

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

                    # Display athlete info (conditionally based on available data)
                    metrics_to_show = []

                    if available_columns.get('Weight', False):
                        metrics_to_show.append(("Weight", f"{athlete['Weight']} kg"))

                    if available_columns.get('Height', False):
                        metrics_to_show.append(("Height", f"{athlete['Height']} cm"))

                    # Calculate BMI if both Weight and Height available
                    if available_columns.get('Weight', False) and available_columns.get('Height', False):
                        height_m = float(athlete['Height']) / 100
                        bmi = float(athlete['Weight']) / (height_m ** 2)
                        metrics_to_show.append(("BMI", f"{bmi:.1f}"))

                    # Display metrics dynamically
                    if metrics_to_show:
                        cols = st.columns(len(metrics_to_show))
                        for idx, (label, value) in enumerate(metrics_to_show):
                            cols[idx].metric(label, value)

                    st.divider()

                    # Display charts
                    st.subheader("Performance Charts")
                    display_preview_charts(athlete, season_type, available_columns)

                    st.divider()

                    # Generate PDF button
                    pdf_allowed, pdf_error = check_pdf_limit(st.session_state)
                    if not pdf_allowed:
                        st.warning(f"⏱️ {pdf_error}")
                    elif st.button("📄 Generate PDF Report", type="primary"):
                        record_pdf(st.session_state)
                        pdf_buffer = generate_pdf_report(athlete, season_type, available_columns)

                        if pdf_buffer is not None:
                            log_pdf_generation(st.session_state, athlete['Name'], season_type)
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

                    team_allowed, team_error = check_team_report_limit(st.session_state)
                    if not team_allowed:
                        st.warning(f"⏱️ {team_error}")
                    elif st.button("📦 Generate All Reports", type="primary"):
                        record_team_report(st.session_state)
                        zip_buffer = generate_team_reports(processed_df, season_type, available_columns)

                        log_team_report(st.session_state, len(processed_df), season_type)
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