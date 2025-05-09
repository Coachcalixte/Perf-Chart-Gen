# Athlete Performance Report Generator

This package generates professional PDF performance reports for athletes based on their sprint and jump test results, with color-coded performance indicators.

## Features

- Generate individual athlete reports with personal information and performance metrics
- Process entire team data from CSV files
- Color-coded performance indicators for sprint and jump tests
- Professional PDF reports with clear visualization

## Installation

### Requirements

```
matplotlib
reportlab
```

Install dependencies:

```bash
pip install matplotlib reportlab
```

## Usage

### 1. Generate a report for a single athlete

```python
from athlete_report import create_athlete_report

create_athlete_report(
    athlete_name="John Doe",
    weight=80.0,  # kg
    height=185.0,  # cm
    sprint_time=1.82,  # seconds
    sprint_30m_time=4.52,  # seconds
    jump_height=51.5,  # cm
)
```

### 2. Generate reports for an entire team from a CSV file

```bash
python team_report_generator.py path/to/athlete_data.csv [output_directory]
```

By default, reports are saved to a `team_reports` directory.

### CSV File Format

The CSV file should have the following columns:
- Name
- Weight (kg)
- Height (cm)
- 10m Sprint (seconds)
- 30m Sprint (seconds)
- CMJ (cm)

Example:
```
Name,Weight,Height,Sprint,Sprint_30m,CMJ
John Doe,80,185,1.82,4.29,51.5
Jane Smith,65,170,1.9,4.32,48.2
```

## Performance Categories

### 10m Sprint (seconds)
- Excellent: < 1.80s
- Good: 1.80s - 1.84s
- Average: 1.85s - 1.90s
- Poor: > 1.91s

### 30m Sprint (seconds)
- Excellent: < 4.17s
- Good: 4.17s - 4.30s
- Average: 4.30s - 4.45s
- Poor: > 4.45s

### CMJ - Counter Movement Jump (cm)
- Excellent: > 52cm
- Good: 45cm - 52cm
- Average: 38cm - 44cm
- Poor: < 38cm

## Project Structure

- `athlete_report.py`: Core module for generating individual athlete reports
- `team_report_generator.py`: Script for processing team CSV files
- `sample_athletes.csv`: Example CSV file with athlete data

## Customization

You can customize the performance thresholds by modifying the color ranges in the chart creation functions.