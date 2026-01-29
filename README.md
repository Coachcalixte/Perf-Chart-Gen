# 🏃‍♂️ Athlete Performance Report Generator

A Streamlit web application that helps coaches and sports professionals generate comprehensive performance reports for athletes. The application visualizes key athletic metrics and creates downloadable PDF reports for individuals or teams.

![Streamlit App Screenshot](https://placehold.co/800x450/24a3f7/ffffff.png?text=Athlete+Performance+Report+Generator)

## Features

- **Season Selection**: Choose between OFF Season and IN Season testing protocols
- **Upload CSV Data**: Easily upload athlete performance data in CSV format with flexible column name recognition
- **Fully Optional Tests**: Only athlete name is required - all tests are optional and handled gracefully
- **Interactive Visualizations**: View color-coded performance charts for key metrics
- **Dynamic Chart Generation**: Charts appear automatically based on available data (0-5 charts for OFF Season)
- **Individual Reports**: Generate detailed PDF reports for individual athletes
- **Team Reports**: Batch generate reports for the entire team in a ZIP archive
- **Responsive Interface**: User-friendly interface that works on desktop and mobile devices
- **Flexible CSV Format**: Automatically recognizes column names with units (e.g., "Weight (Kg)", "Sprint 30m (sec)")

## Performance Metrics

### OFF Season Testing
The application supports comprehensive performance assessment with the following metrics:

**Required:**
- **Name**: Athlete's full name (only required field)

**Optional Anthropometric Data:**
- **Weight**: Body weight in kilograms
- **Height**: Height in centimeters

**Optional Performance Tests:**
- **10m Sprint Time**: Measures acceleration capability (seconds)
- **30m Sprint Time**: Measures top-end speed capability (seconds)
- **Counter Movement Jump (CMJ)**: Measures lower body power (centimeters)
- **Yoyo Test**: Measures aerobic endurance (level reached, typically 17.0-21.0+)
- **Stop & Go Test**: Measures change of direction speed (seconds)

### IN Season Testing
Focused monitoring with fewer tests:
- **Counter Movement Jump (CMJ)**: Monitors lower body power maintenance
- **Wattbike 6s Power**: Measures anaerobic power output (Watts per kilogram)

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

#### Flexible Column Recognition
The app automatically recognizes column names with various formats:
- Column names with units in parentheses: `Weight (Kg)`, `Height (cm)`, `Sprint (sec)`
- Special characters and spaces: `Sprint 30m (sec)`, `Stop & Go (5-10-5) (sec)`
- Different spellings: `Yo-Yo test (level)` matches `Yoyo`

#### Required Columns
Only one column is required:
- `Name` (or variations like `Athlete Name`, `Player Name`)

#### Optional Columns (OFF Season)
All other columns are optional. Include only the tests your athletes completed:
- `Weight` - in kilograms (e.g., `Weight (Kg)`)
- `Height` - in centimeters (e.g., `Height (cm)`)
- `Sprint` - 10m sprint time in seconds (e.g., `Sprint (sec)`)
- `Sprint_30m` - 30m sprint time in seconds (e.g., `Sprint 30m (sec)`)
- `CMJ` - Counter Movement Jump in centimeters (e.g., `CMJ (cm)`)
- `Yoyo` - Yoyo test level (e.g., `Yo-Yo test (level)`)
- `StopGo` - Stop & Go test in seconds (e.g., `Stop & Go (5-10-5) (sec)`)

#### Optional Columns (IN Season)
- `Weight` - in kilograms
- `Height` - in centimeters
- `CMJ` - Counter Movement Jump in centimeters
- `Wattbike_6s` - Wattbike 6-second power output in Watts (e.g., `Watt Bike 30" Avg. Power (Watt)`)

#### Example CSV Files

**Full OFF Season Data:**
```csv
Name,Weight (Kg),Height (cm),Sprint (sec),Sprint 30m (sec),CMJ (cm),Yo-Yo test (level),Stop & Go (sec)
John Doe,80,185,1.82,4.30,51.5,19.2,4.52
Jane Smith,65,170,1.90,5.00,48.2,17.5,4.68
```

**Partial OFF Season Data (missing some tests):**
```csv
Name,Weight (Kg),Sprint (sec),CMJ (cm),Yo-Yo test (level)
John Doe,80,1.82,51.5,19.2
Jane Smith,65,1.90,48.2,17.5
```

**Minimal Data (name only):**
```csv
Name
John Doe
Jane Smith
```

The app will display charts only for available tests and show informative messages about missing data.

## Performance Categories

The application uses color-coded performance zones for all metrics:

### 10m Sprint (seconds) - Lower is Better
- **Excellent** (Green): < 1.80s
- **Good** (Yellow): 1.80s - 1.85s
- **Average** (Orange): 1.85s - 1.91s
- **Below Average** (Red): > 1.91s

### 30m Sprint (seconds) - Lower is Better
- **Excellent** (Green): < 4.17s
- **Good** (Yellow): 4.17s - 4.30s
- **Average** (Orange): 4.30s - 4.45s
- **Below Average** (Red): > 4.45s

### Counter Movement Jump (centimeters) - Higher is Better
- **Excellent** (Green): > 52cm
- **Good** (Yellow): 45cm - 52cm
- **Average** (Orange): 38cm - 45cm
- **Below Average** (Red): < 38cm

### Yoyo Test (level) - Higher is Better
- **Excellent** (Green): 19.1+
- **Good** (Yellow): 18.1 - 19.0
- **Average** (Orange): 17.1 - 18.0
- **Below Average** (Red): < 17.0

### Stop & Go Test (seconds) - Lower is Better
- **Excellent** (Green): ≤ 4.54s
- **Good** (Yellow): 4.55s - 4.65s
- **Average** (Orange): 4.66s - 4.79s
- **Below Average** (Red): ≥ 4.80s

### Wattbike 6s Power (W/kg) - Higher is Better
- **WOW** (Green): > 25 W/kg
- **Good** (Yellow): 20-25 W/kg
- **Average** (Orange): 15-20 W/kg
- **Need to Work** (Red): < 15 W/kg

## Deployment

### Docker Deployment (Recommended)

The application includes Docker support for easy deployment:

```bash
# Build the Docker image
docker build -t perf-chart-gen:latest .

# Run the container
docker run -p 8501:8501 perf-chart-gen:latest
```

Access the app at `http://localhost:8501`

### Deploying to Coolify or Similar Platforms

1. Connect your GitHub repository to your deployment platform
2. Select the `main` branch for production or `feature/season-selection` for beta testing
3. The platform will automatically detect the Dockerfile and deploy
4. Configure your domain and SSL certificate
5. Set `server.enableCORS=false` and `server.enableXsrfProtection=false` for iframe embedding

### Deploying to Streamlit Cloud

1. Create a GitHub repository with all the necessary files
2. Visit [Streamlit Cloud](https://streamlit.io/cloud) and sign in with your GitHub account
3. Deploy your app by selecting your repository and the main file (`athlete_report_streamlit.py`)
4. Configure your privacy settings to make the app public or private

### WordPress Integration

The app is designed to work embedded in WordPress via iframe:
- Configure `.streamlit/config.toml` for iframe compatibility
- Set `toolbarMode = "minimal"` for cleaner embedding
- Use matching colors with your WordPress theme

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