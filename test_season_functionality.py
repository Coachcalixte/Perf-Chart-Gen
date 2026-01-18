#!/usr/bin/env python
"""
Test script for season selection functionality.
Validates OFF Season and IN Season workflows programmatically.
"""

import pandas as pd
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from athlete_report import (
    create_sprint_chart,
    create_sprint_30m_chart,
    create_jump_chart,
    create_wattbike_chart
)

from athlete_report_streamlit import SEASON_CONFIG

def test_season_config():
    """Test that SEASON_CONFIG is properly defined."""
    print("=" * 60)
    print("TEST 1: Season Configuration")
    print("=" * 60)

    assert "OFF Season" in SEASON_CONFIG, "OFF Season not in config"
    assert "IN Season" in SEASON_CONFIG, "IN Season not in config"

    # OFF Season validation
    off_config = SEASON_CONFIG["OFF Season"]
    assert set(off_config["required_columns"]) == {
        'Name', 'Weight', 'Height', 'Sprint', 'Sprint_30m', 'CMJ'
    }, "OFF Season columns incorrect"

    # IN Season validation
    in_config = SEASON_CONFIG["IN Season"]
    assert set(in_config["required_columns"]) == {
        'Name', 'Weight', 'Height', 'CMJ', 'Wattbike_6s'
    }, "IN Season columns incorrect"

    print("✅ Season configuration valid")
    print()


def test_off_season_csv():
    """Test OFF Season CSV loading."""
    print("=" * 60)
    print("TEST 2: OFF Season CSV")
    print("=" * 60)

    csv_path = Path(__file__).parent / "sample_athletes.csv"
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} athletes from OFF Season CSV")
    print(f"Columns: {list(df.columns)}")

    # Check required columns
    required = SEASON_CONFIG["OFF Season"]["required_columns"]
    for col in required:
        assert col in df.columns, f"Missing column: {col}"

    print("✅ OFF Season CSV valid")
    print()

    return df


def test_in_season_csv():
    """Test IN Season CSV loading."""
    print("=" * 60)
    print("TEST 3: IN Season CSV")
    print("=" * 60)

    csv_path = Path(__file__).parent / "sample_athletes_in_season.csv"
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} athletes from IN Season CSV")
    print(f"Columns: {list(df.columns)}")

    # Check required columns
    required = SEASON_CONFIG["IN Season"]["required_columns"]
    for col in required:
        assert col in df.columns, f"Missing column: {col}"

    print("✅ IN Season CSV valid")
    print()

    return df


def test_off_season_charts(df):
    """Test OFF Season chart generation."""
    print("=" * 60)
    print("TEST 4: OFF Season Chart Generation")
    print("=" * 60)

    athlete = df.iloc[0]
    print(f"Testing with athlete: {athlete['Name']}")

    # Test 10m Sprint chart
    sprint_img = create_sprint_chart(float(athlete['Sprint']))
    assert sprint_img is not None, "10m Sprint chart failed"
    print(f"✅ 10m Sprint chart: {athlete['Sprint']}s")

    # Test 30m Sprint chart
    sprint_30m_img = create_sprint_30m_chart(float(athlete['Sprint_30m']))
    assert sprint_30m_img is not None, "30m Sprint chart failed"
    print(f"✅ 30m Sprint chart: {athlete['Sprint_30m']}s")

    # Test CMJ chart
    cmj_img = create_jump_chart(float(athlete['CMJ']))
    assert cmj_img is not None, "CMJ chart failed"
    print(f"✅ CMJ chart: {athlete['CMJ']}cm")

    print("✅ All OFF Season charts generated successfully")
    print()


def test_in_season_charts(df):
    """Test IN Season chart generation."""
    print("=" * 60)
    print("TEST 5: IN Season Chart Generation")
    print("=" * 60)

    athlete = df.iloc[0]
    print(f"Testing with athlete: {athlete['Name']}")

    # Test CMJ chart
    cmj_img = create_jump_chart(float(athlete['CMJ']))
    assert cmj_img is not None, "CMJ chart failed"
    print(f"✅ CMJ chart: {athlete['CMJ']}cm")

    # Test Wattbike chart
    power_per_kg = float(athlete['Wattbike_6s']) / float(athlete['Weight'])
    wattbike_img = create_wattbike_chart(power_per_kg)
    assert wattbike_img is not None, "Wattbike chart failed"
    print(f"✅ Wattbike chart: {power_per_kg:.2f} W/kg")

    print("✅ All IN Season charts generated successfully")
    print()


def test_wattbike_calculations():
    """Test Wattbike W/kg calculations for all IN Season athletes."""
    print("=" * 60)
    print("TEST 6: Wattbike W/kg Calculations")
    print("=" * 60)

    csv_path = Path(__file__).parent / "sample_athletes_in_season.csv"
    df = pd.read_csv(csv_path)

    expected_zones = {
        "John Doe": ("Good", 22.5),
        "Jane Smith": ("Good", 20.0),
        "Mike Johnson": ("Good", 24.4),
        "Sarah Williams": ("Good", 21.4),
        "Tom Brown": ("Good", 22.0)
    }

    for _, athlete in df.iterrows():
        name = athlete['Name']
        power_per_kg = float(athlete['Wattbike_6s']) / float(athlete['Weight'])

        # Determine zone
        if power_per_kg < 15:
            zone = "Need to work"
        elif power_per_kg < 20:
            zone = "Average"
        elif power_per_kg < 25:
            zone = "Good"
        else:
            zone = "WOW"

        expected_zone, expected_value = expected_zones[name]

        print(f"{name:20s} {power_per_kg:6.2f} W/kg → {zone:15s} ", end="")

        # Validate
        assert abs(power_per_kg - expected_value) < 0.1, f"Calculation error for {name}"
        assert zone == expected_zone, f"Zone mismatch for {name}"

        print("✅")

    print("✅ All Wattbike calculations correct")
    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "SEASON SELECTION FUNCTIONALITY TEST" + " " * 12 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    try:
        # Test 1: Configuration
        test_season_config()

        # Test 2-4: OFF Season
        off_df = test_off_season_csv()
        test_off_season_charts(off_df)

        # Test 5-6: IN Season
        in_df = test_in_season_csv()
        test_in_season_charts(in_df)
        test_wattbike_calculations()

        # Summary
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("Summary:")
        print("  ✅ Season configuration valid")
        print("  ✅ OFF Season CSV loads correctly")
        print("  ✅ IN Season CSV loads correctly")
        print("  ✅ OFF Season charts generate (10m, 30m, CMJ)")
        print("  ✅ IN Season charts generate (CMJ, Wattbike)")
        print("  ✅ Wattbike W/kg calculations correct")
        print()
        print("🎉 Ready for deployment!")
        print()

        return 0

    except AssertionError as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        return 1

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ UNEXPECTED ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
