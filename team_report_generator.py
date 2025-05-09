# team_report_generator.py
"""
Script to generate performance reports for an entire team from a CSV file.
"""

import csv
import os
import sys
from athlete_report import create_athlete_report

def read_athlete_data(csv_file):
    """
    Read athlete data from a CSV file.
    
    Expected CSV format:
    Name,Weight,Height,Sprint,Sprint_30m,CMJ
    John Doe,80,185,1.82,4.29,51.5
    Jane Smith,65,170,1.9,4.32,48.2
    ...
    
    Parameters:
    csv_file (str): Path to the CSV file
    
    Returns:
    list: List of dictionaries containing athlete data
    """
    athletes = []
    
    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            
            # Validate headers
            required_fields = ['Name', 'Weight', 'Height', 'Sprint', 'Sprint_30m','CMJ']
            headers = reader.fieldnames
            
            # Case-insensitive check for required fields
            headers_lower = [h.lower() if h else '' for h in headers]
            missing_fields = [field for field in required_fields 
                             if field.lower() not in headers_lower]
            
            if missing_fields:
                print(f"Error: Missing required fields in CSV: {', '.join(missing_fields)}")
                print(f"Found headers: {', '.join(headers)}")
                return []
            
            # Map actual header names to expected fields (case insensitive)
            field_mapping = {}
            for required in required_fields:
                for i, header in enumerate(headers):
                    if header and header.lower() == required.lower():
                        field_mapping[required] = header
                        break
            
            # Read data
            for row in reader:
                try:
                    athlete = {
                        'name': row[field_mapping['Name']],
                        'weight': float(row[field_mapping['Weight']]),
                        'height': float(row[field_mapping['Height']]),
                        'sprint': float(row[field_mapping['Sprint']]),
                        'sprint_30m': float(row[field_mapping['Sprint_30m']]),
                        'jump': float(row[field_mapping['CMJ']])
                    }
                    athletes.append(athlete)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping row due to invalid data: {row}")
                    print(f"Error: {e}")
    
    except FileNotFoundError:
        print(f"Error: File not found: {csv_file}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    
    return athletes

def generate_team_reports(csv_file, output_dir="team_reports"):
    """
    Generate performance reports for all athletes in the CSV file.
    
    Parameters:
    csv_file (str): Path to the CSV file
    output_dir (str): Directory to save the reports
    
    Returns:
    int: Number of reports generated
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read athlete data
    athlete_data = read_athlete_data(csv_file)
    
    if not athlete_data:
        print("No valid athlete data found. Exiting.")
        return 0
    
    print(f"Found {len(athlete_data)} athletes in the CSV file.")
    
    # Generate report for each athlete
    report_count = 0
    for athlete in athlete_data:
        try:
            report_path = create_athlete_report(
                athlete_name=athlete['name'],
                weight=athlete['weight'],
                height=athlete['height'],
                sprint_time=athlete['sprint'],
                sprint_30m_time=athlete['sprint_30m'],
                jump_height=athlete['jump'],
                output_dir=output_dir
            )
            report_count += 1
        except Exception as e:
            print(f"Error generating report for {athlete['name']}: {e}")
    
    print(f"Generated {report_count} reports in {output_dir}")
    return report_count

def main():
    """
    Main function to run the team report generator.
    """
    if len(sys.argv) < 2:
        print("Usage: python team_report_generator.py path/to/athlete_data.csv [output_directory]")
        return
    
    csv_file = sys.argv[1]
    
    # Optional output directory
    output_dir = "team_reports"
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    generate_team_reports(csv_file, output_dir)

if __name__ == "__main__":
    main()