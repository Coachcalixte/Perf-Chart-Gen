# 🏃‍♂️ Athlete Performance Report Generator

A Streamlit web application that helps coaches and sports professionals generate comprehensive performance reports for athletes. The application visualizes key athletic metrics and creates downloadable PDF reports for individuals or teams.

![Streamlit App Screenshot](https://placehold.co/800x450/24a3f7/ffffff.png?text=Athlete+Performance+Report+Generator)

## Features

- **Upload CSV Data**: Easily upload athlete performance data in CSV format
- **Interactive Visualizations**: View color-coded performance charts for key metrics
- **Individual Reports**: Generate detailed PDF reports for individual athletes
- **Team Reports**: Batch generate reports for the entire team in a ZIP archive
- **Responsive Interface**: User-friendly interface that works on desktop and mobile devices

## Performance Metrics

The application currently supports the following athletic performance metrics:

- **10m Sprint Time**: Measures acceleration capability (seconds)
- **30m Sprint Time**: Measures top-end speed capability (seconds)
- **Counter Movement Jump (CMJ)**: Measures lower body power (centimeters)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Pip package manager

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/athlete-performance-reports.git
   cd athlete-performance-reports
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run athlete_report_streamlit.py
   ```

### CSV Format

Your CSV file should have the following columns:
- `Name`: Athlete's full name
- `Weight`: Weight in kilograms
- `Height`: Height in centimeters
- `Sprint`: 10m sprint time in seconds
- `Sprint_30m`: 30m sprint time in seconds
- `CMJ`: Counter Movement Jump height in centimeters

Example:
```csv
Name,Weight,Height,Sprint,Sprint_30m,CMJ
John Doe,80,185,1.82,4.29,51.5
Jane Smith,65,170,1.9,4.32,48.2
```

## Performance Categories

The application uses the following classifications for performance metrics:

### 10m Sprint (seconds)
- **Excellent**: < 1.80s
- **Good**: 1.80s - 1.85s
- **Average**: 1.85s - 1.91s
- **Poor**: > 1.91s

### 30m Sprint (seconds)
- **Excellent**: < 4.17s
- **Good**: 4.17s - 4.30s
- **Average**: 4.30s - 4.45s
- **Poor**: > 4.45s

### Counter Movement Jump (centimeters)
- **Excellent**: > 52cm
- **Good**: 45cm - 52cm
- **Average**: 38cm - 45cm
- **Poor**: < 38cm

## Deployment

### Deploying to Streamlit Cloud

1. Create a GitHub repository with all the necessary files:
   - `athlete_report_streamlit.py`
   - `athlete_report.py`
   - `team_report_generator.py`
   - `requirements.txt`

2. Visit [Streamlit Cloud](https://streamlit.io/cloud) and sign in with your GitHub account

3. Deploy your app by selecting your repository and the main file (`athlete_report_streamlit.py`)

4. Configure your privacy settings to make the app public or private

## File Structure

- `athlete_report_streamlit.py`: Main Streamlit application file
- `athlete_report.py`: Module for creating visualizations and PDF reports
- `team_report_generator.py`: Script for batch generating team reports
- `requirements.txt`: Required Python dependencies

## Privacy and Security

Data uploaded through the web interface is:
- Processed in-memory only, not saved to persistent storage
- Available only during your active session
- Not accessible to other users
- Automatically cleared when sessions end or the app restarts

## Contributing

Contributions to improve the application are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the web app framework
- [ReportLab](https://www.reportlab.com/) for PDF generation
- [Matplotlib](https://matplotlib.org/) for visualization capabilities