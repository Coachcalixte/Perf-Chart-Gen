# Lessons Learned: Athlete Performance Report Generator

## Project Overview
Development of a Streamlit web application for generating athlete performance reports with season-specific testing protocols, fully optional columns, and flexible CSV import.

**Duration**: Multi-phase development
**Technology Stack**: Python, Streamlit, Matplotlib, ReportLab, Pandas, Docker
**Deployment**: Coolify (Docker-based), WordPress iframe integration

---

## Key Technical Decisions

### 1. Fully Optional Column Architecture
**Decision**: Made ALL columns optional except Name, even anthropometric data (Weight, Height).

**Rationale**:
- Athletes can be injured or absent during specific tests
- Real-world CSV files often have partial data
- Coaches need flexibility to work with whatever data they have

**Implementation**:
- Used metadata-rich `optional_columns` dictionary with `numeric`, `unit`, and `chart` metadata
- `process_csv()` returns tuple: `(dataframe, available_columns_dict)`
- All display and PDF functions check `available_columns` before rendering
- Dynamic UI adapts to show 0-6 charts based on available data

**Benefits**:
- Zero data loss - never drop athletes with partial data
- Graceful degradation - show what you have
- User-friendly error messages instead of validation failures

**Lessons**:
- Don't assume all "required" fields will always be present in real-world data
- Build systems that adapt to data availability rather than forcing rigid schemas
- Metadata-driven configuration is more maintainable than hardcoded logic

---

### 2. Flexible Column Name Matching
**Problem**: Users' CSV files have descriptive column names:
- `Weight (Kg)` instead of `Weight`
- `Sprint 30m (sec)` instead of `Sprint_30m`
- `Stop & Go (5-10-5) (sec)` instead of `StopGo`
- `Yo-Yo test (level)` instead of `Yoyo`

**Solution**: Implemented `normalize_column_name()` and `find_matching_column()` functions:
1. Strip units in parentheses: `Weight (Kg)` → `weight`
2. Remove special characters: `Stop & Go` → `stop_go`
3. Normalize spacing: `Sprint 30m` → `sprint_30m`
4. Handle common variations: `Yo-Yo test` matches `Yoyo`

**Impact**:
- Users can upload real-world CSV files without manual editing
- App works with exports from Excel, Google Sheets, specialized sports software
- Reduced support burden (no "column not found" errors)

**Lessons**:
- Always build for real-world data, not idealized examples
- User convenience trumps developer convenience
- Flexible parsing is worth the extra code complexity

---

### 3. Session State Management
**Challenge**: Streamlit reruns the entire script on every interaction.

**Solution**: Used `st.session_state` to persist:
- `season_type`: User's season selection (OFF/IN)
- `processed_df`: Cleaned athlete data
- `available_columns`: Which tests are present

**Benefits**:
- Avoid reprocessing CSV on every interaction
- Maintain state across tab switches
- Enable conditional rendering without re-validation

**Lessons**:
- Understand framework execution model before building complex apps
- Session state is essential for stateful applications in Streamlit
- Store derived data (like `available_columns`) to avoid recalculation

---

### 4. Dynamic Chart Rendering
**Approach**: Charts are built dynamically based on `available_columns`:

```python
charts_to_show = []
chart_functions = {}

if available_columns.get('Sprint', False):
    charts_to_show.append('Sprint')
    chart_functions['Sprint'] = (create_sprint_chart, value, caption)

# ... repeat for all tests

cols = st.columns(len(charts_to_show))  # Dynamic column count
```

**Benefits**:
- UI adapts seamlessly to data availability
- No empty placeholders or error messages
- Same code handles 0-5 charts without special cases

**Lessons**:
- Dynamic layouts provide better UX than fixed layouts with conditionals
- Build UI from data structure, not hardcoded sections
- Streamlit's `st.columns()` with dynamic count is powerful

---

### 5. BMI and Wattbike Conditional Calculations
**Insight**: Some metrics require multiple data points:
- BMI requires BOTH Weight AND Height
- Wattbike W/kg requires BOTH Wattbike_6s AND Weight

**Implementation**: Check for all dependencies before calculating:

```python
if available_columns.get('Weight', False) and available_columns.get('Height', False):
    height_m = float(athlete['Height']) / 100
    bmi = float(athlete['Weight']) / (height_m ** 2)
    metrics_to_show.append(("BMI", f"{bmi:.1f}"))
```

**Lessons**:
- Don't assume derived metrics can always be calculated
- Check all dependencies explicitly
- Gracefully skip derived metrics when data is incomplete

---

## Architecture Patterns

### Centralized Configuration
Used `SEASON_CONFIG` dictionary as single source of truth:
- Required columns
- Optional columns with metadata
- Chart mappings
- Descriptions

**Benefits**:
- Easy to add new seasons or tests
- Self-documenting code
- Consistent validation across functions

### Tuple Returns for Multi-Value Functions
`process_csv()` returns `(df, available_columns)` instead of just `df`:
- Explicit data about what's available
- Avoids global state
- Enables conditional logic downstream

### Helper Functions for Reusability
Created focused utility functions:
- `normalize_column_name()` - Text processing
- `find_matching_column()` - Column matching logic
- `build_pdf_story()` - PDF structure generation

**Benefits**:
- Testable in isolation
- Reusable across different contexts
- Easier to debug

---

## User Experience Insights

### 1. Informative Messages Over Errors
**Bad**: "❌ Missing required column: Sprint_30m"
**Good**: "ℹ️ Optional tests not found: Sprint_30m, Yoyo. Displaying available tests only."

**Lesson**: Frame missing data as information, not failure. Users understand "optional" better than "required but missing."

### 2. Show What Charts Will Be Generated
Added expandable section showing:
- Required columns
- Optional columns (anthropometric data)
- Optional performance tests → Chart names

**Impact**: Users know exactly what to include in CSV to get desired charts.

### 3. Dynamic Metrics Display
Don't show fixed 3-column layout with empty spaces. Show only metrics that have data:

```python
if metrics_to_show:
    cols = st.columns(len(metrics_to_show))
    # Display dynamically
```

**Result**: Clean UI that adapts to data, not cluttered with "N/A" values.

---

## Testing Learnings

### Test with Real Data Early
- Sample CSVs with perfect data don't reveal real problems
- User provided actual CSV with:
  - Units in parentheses
  - Special characters (&, -, /)
  - Numbers in column names
  - Inconsistent spacing

**Action**: Create test cases from actual user files, not idealized examples.

### Test All Combinations
With fully optional columns, need to test:
- All columns present
- No optional columns
- Partial combinations (Weight but no Height)
- Edge cases (Name only)

**Solution**: Created `sample_athletes_partial.csv` for testing partial data scenarios.

### Syntax Check Is Not Enough
`python -m py_compile` catches syntax errors but not:
- Logic errors
- Missing imports
- Runtime type mismatches

**Better**: Run actual test scripts that exercise code paths.

---

## Docker & Deployment Lessons

### 1. .dockerignore Is Critical
Don't copy unnecessary files into Docker image:
- `venv/` - Virtual environment (rebuild from requirements.txt)
- `__pycache__/` - Python cache files
- `.git/` - Git history
- Test files - Not needed in production

**Result**: Smaller images, faster builds, cleaner deploys.

### 2. Sample Data in Docker
Include sample CSV files in Docker image:
```dockerfile
COPY sample_athletes.csv .
COPY sample_athletes_in_season.csv .
```

**Benefit**: Users can test app immediately without preparing data.

### 3. Healthcheck for Container Monitoring
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')"
```

**Benefit**: Coolify/Docker knows if app is actually running, not just container.

### 4. Git Branch Strategy for Beta Testing
- `main` branch → Production deployment
- `feature/season-selection` branch → Beta deployment at subdomain

**Benefits**:
- Safe testing of new features
- Easy rollback (just switch branch)
- Parallel deployments for comparison

---

## Code Quality Practices

### 1. Docstrings for Complex Functions
Every function has clear docstring with:
- Purpose
- Args with types
- Returns with types
- Special behavior notes

**Example**:
```python
def process_csv(df, season_type):
    """
    Process CSV with fully optional columns (only Name required).
    Handles flexible column name matching.

    Args:
        df (pd.DataFrame): Raw uploaded DataFrame
        season_type (str): "OFF Season" or "IN Season"

    Returns:
        tuple: (processed_df, available_columns_dict) or (None, None)
    """
```

### 2. Explicit Error Handling
Use try-except only where needed, return `None` for failures:
```python
if processed_df is not None and available_columns is not None:
    # Continue processing
else:
    # Error already shown to user via st.error()
```

**Benefit**: Clear failure modes, no silent errors.

### 3. Consistent Naming Conventions
- Functions: `lowercase_with_underscores()`
- Constants: `UPPERCASE_WITH_UNDERSCORES`
- Variables: `lowercase_with_underscores`
- Classes: `CapitalizedWords` (not used in this project)

---

## Git & Version Control

### Commit Message Structure
Used structured commit messages:
```
[Type]: [Short summary]

[Detailed description of changes]
- Bullet points for key changes
- Technical details
- Rationale

[Impact/Benefits]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Benefits**:
- Easy to understand what changed and why
- Searchable commit history
- Clear attribution

### Branch Naming
`feature/season-selection` clearly indicates:
- Type (feature, not bugfix)
- What it adds (season selection)

### Merge Strategy
Used fast-forward merge from feature branch to main:
```bash
git checkout main
git merge feature/season-selection
git push origin main
```

**Result**: Clean linear history, all commits preserved.

---

## Performance Considerations

### 1. In-Memory Processing Only
- CSV processed in memory (Pandas DataFrame)
- Charts generated as BytesIO buffers
- PDFs built in memory

**Benefits**:
- Fast (no disk I/O)
- Stateless (no cleanup needed)
- Secure (no persistent data)

### 2. Chart Caching Not Used
Streamlit's `@st.cache_data` not used because:
- Each athlete's data is unique
- Charts are fast to generate (<100ms)
- Session-based usage (not high-traffic site)

**Decision**: Simplicity over micro-optimization.

### 3. Pandas for CSV Processing
Using Pandas instead of CSV module:
- Easier numeric validation (`pd.to_numeric`)
- Built-in missing data handling
- DataFrame operations more intuitive

---

## Security & Privacy

### Security Module Implementation
Created a dedicated `security.py` module with comprehensive protection:

**Input Validation & Sanitization:**
- CSV injection prevention (formulas: `=`, `@`, `+`, `-`)
- XSS prevention (`<script`, `javascript:`, `data:`)
- Command injection prevention (`|`, `;`)
- File size limits (10MB max)
- Row limits (500 athletes max)
- Cell length limits (200 characters)

**Rate Limiting:**
- Session-based rate limiting using Streamlit session state
- Per-action limits: uploads (20/hr), PDFs (50/hr), team reports (5/hr)
- Graceful degradation with user-friendly warnings

**Usage Logging:**
- Anonymous session tracking (hashed session IDs)
- Event logging: uploads, PDF generations, errors
- Privacy-first: No athlete names logged
- JSON format for easy parsing

**Email Collection:**
- Optional sidebar form
- Email validation (format + typo detection)
- Consent-based storage
- Secure file storage

### Data Handling
- **No persistent storage**: Uploaded data exists only in session
- **Anonymous logging**: Usage logs contain no PII
- **Session isolation**: Each user's data separate
- **Auto cleanup**: Data cleared when session ends

### Docker Security
- Run as non-root user (implicit in python:3.11-slim)
- Minimal base image (only Python and dependencies)
- No exposed secrets or API keys
- Logs directory created at container startup

### Lessons Learned from Security Implementation
1. **Defense in depth**: Multiple layers (app + potential Cloudflare)
2. **Graceful rate limiting**: Warn users, don't just block
3. **Privacy by design**: Hash/anonymize everything possible
4. **Separate security module**: Easier to audit and maintain
5. **Configurable limits**: Easy to adjust without code changes

---

## Future Improvements Considered

### 1. Historical Tracking (NOT Implemented)
**Why Not**: Adds complexity (database, auth, data retention policies). Current scope is single-session reporting only.

**If Needed**: Could add PostgreSQL + user authentication + data retention settings.

### 2. Custom Performance Zones (NOT Implemented)
**Why Not**: Current zones are based on sports science standards. Customization adds UI complexity.

**If Needed**: Add settings page where coaches define their own thresholds.

### 3. Multi-Language Support (NOT Implemented)
**Why Not**: Primary users are English-speaking coaches.

**If Needed**: Use `streamlit-i18n` or similar package.

### 4. Export to Excel (NOT Implemented)
**Why Not**: PDF reports meet current needs.

**If Needed**: Add `openpyxl` for Excel generation.

---

## Key Takeaways

### Technical
1. **Build for real data**: Perfect test data hides real problems
2. **Fail gracefully**: Missing data shouldn't break the app
3. **Flexible parsing**: Handle variations in user input
4. **Dynamic UI**: Adapt to data, don't force fixed layouts
5. **Metadata-driven config**: Easier to extend than hardcoded logic
6. **Security as a module**: Separate security code for easy auditing
7. **Rate limiting early**: Prevent abuse before it becomes a problem

### Process
1. **Iterate based on feedback**: User's real CSV revealed column name issues
2. **Test early and often**: Syntax checks aren't enough
3. **Document as you go**: Lessons learned doc helps future you
4. **Git branches for safety**: Feature branches enable safe testing
5. **Commit messages matter**: Future you will thank present you

### Product
1. **User convenience is king**: Extra dev work for flexible CSV parsing pays off
2. **Clear error messages**: Help users understand what's wrong and how to fix it
3. **Show, don't hide**: Display what data you have, not what's missing
4. **Sample data is essential**: Users need examples to get started
5. **Responsive feedback**: Loading states, success messages, progress bars

---

## Conclusion

This project demonstrated the importance of:
- **Building for real-world use cases**, not idealized scenarios
- **Graceful degradation** when data is incomplete
- **User-centric design** that adapts to what users provide
- **Robust error handling** that guides users to success
- **Clean architecture** that's easy to extend and maintain
- **Security from the start**: Rate limiting, validation, and logging

The transition from rigid schema validation to flexible optional columns was the most impactful change, transforming the app from "works with perfect data" to "works with real data." The security module provides a solid foundation for production deployment and future membership integration.

---

**Last Updated**: 2026-02-14
**Author**: Coach Calixte with Claude Code
**Project**: Athlete Performance Report Generator
**Repository**: https://github.com/Coachcalixte/Perf-Chart-Gen

### Change History
| Date | Changes |
|------|---------|
| 2026-01-29 | Initial lessons learned document |
| 2026-02-14 | Added Broad Jump test, security implementation, updated to 6 OFF Season tests |
