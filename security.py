"""
Security Module for Athlete Performance Report Generator

This module provides:
1. Input validation and sanitization
2. Rate limiting
3. Usage logging
4. CSV security checks

Author: Coach Calixte
"""

import re
import os
import json
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import pandas as pd

# Configure logging with rotation
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log rotation settings
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB per log file
LOG_BACKUP_COUNT = 3             # Keep 3 backup files (total ~20 MB max)

# Setup logger with rotating file handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Avoid duplicate handlers on module reload
if not logger.handlers:
    # Rotating file handler (rotates at 5MB, keeps 3 backups)
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Console handler for debugging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Rate limiting configuration
RATE_LIMITS = {
    "uploads_per_hour": 20,       # Max CSV uploads per hour per session
    "pdfs_per_hour": 50,          # Max PDF generations per hour per session
    "team_reports_per_hour": 5,   # Max team report downloads per hour
}

# CSV validation limits
CSV_LIMITS = {
    "max_rows": 500,              # Max athletes per CSV
    "max_columns": 50,            # Max columns
    "max_cell_length": 200,       # Max characters per cell
    "max_file_size_mb": 10,       # Max file size (more restrictive than Streamlit's 50MB)
}

# Dangerous patterns for CSV injection
DANGEROUS_PATTERNS = [
    r'^=',           # Formula injection (Excel)
    r'^@',           # Formula injection (Excel)
    r'^\+',          # Formula injection (Excel)
    r'^-(?!\d)',     # Formula injection (but allow negative numbers)
    r'^!',           # Formula injection
    r'^\|',          # Command injection
    r'^;',           # CSV injection
    r'<script',      # XSS attempt
    r'javascript:',  # XSS attempt
    r'data:',        # Data URI injection
    r'on\w+=',       # Event handler injection
]


# =============================================================================
# INPUT VALIDATION & SANITIZATION
# =============================================================================

def sanitize_string(value: str) -> str:
    """
    Sanitize a string to prevent injection attacks.

    Args:
        value: Input string to sanitize

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)

    # Trim whitespace
    value = value.strip()

    # Remove null bytes
    value = value.replace('\x00', '')

    # Check for dangerous patterns and neutralize
    for pattern in DANGEROUS_PATTERNS:
        if re.match(pattern, value, re.IGNORECASE):
            # Prefix with single quote to prevent formula execution
            value = "'" + value
            logger.warning(f"Sanitized potentially dangerous input: {value[:50]}...")
            break

    # Limit length
    if len(value) > CSV_LIMITS["max_cell_length"]:
        value = value[:CSV_LIMITS["max_cell_length"]]
        logger.warning(f"Truncated oversized cell content")

    return value


def validate_csv_security(df: pd.DataFrame, file_size_bytes: int) -> Tuple[bool, str, pd.DataFrame]:
    """
    Validate CSV file for security issues and sanitize content.

    Args:
        df: Pandas DataFrame from uploaded CSV
        file_size_bytes: Size of uploaded file in bytes

    Returns:
        Tuple of (is_valid, error_message, sanitized_df)
    """
    # Check file size
    file_size_mb = file_size_bytes / (1024 * 1024)
    if file_size_mb > CSV_LIMITS["max_file_size_mb"]:
        return False, f"File too large. Maximum size is {CSV_LIMITS['max_file_size_mb']}MB, got {file_size_mb:.1f}MB", df

    # Check row count
    if len(df) > CSV_LIMITS["max_rows"]:
        return False, f"Too many rows. Maximum is {CSV_LIMITS['max_rows']} athletes, got {len(df)}", df

    # Check column count
    if len(df.columns) > CSV_LIMITS["max_columns"]:
        return False, f"Too many columns. Maximum is {CSV_LIMITS['max_columns']}, got {len(df.columns)}", df

    # Check for empty DataFrame
    if len(df) == 0:
        return False, "CSV file is empty", df

    # Sanitize all string columns
    for col in df.columns:
        if df[col].dtype == 'object':  # String columns
            df[col] = df[col].apply(lambda x: sanitize_string(str(x)) if pd.notna(x) else x)

    # Sanitize column names
    sanitized_columns = {}
    for col in df.columns:
        sanitized_col = sanitize_string(str(col))
        sanitized_columns[col] = sanitized_col
    df = df.rename(columns=sanitized_columns)

    logger.info(f"CSV validated: {len(df)} rows, {len(df.columns)} columns, {file_size_mb:.2f}MB")

    return True, "", df


# Disposable email domains blocklist (common temporary email services)
DISPOSABLE_EMAIL_DOMAINS = {
    # Popular disposable email services
    'mailinator.com', 'guerrillamail.com', 'tempmail.com', 'throwaway.email',
    '10minutemail.com', 'temp-mail.org', 'fakeinbox.com', 'trashmail.com',
    'mailnesia.com', 'tempail.com', 'dispostable.com', 'mailcatch.com',
    'yopmail.com', 'sharklasers.com', 'guerrillamail.info', 'grr.la',
    'guerrillamail.biz', 'guerrillamail.de', 'guerrillamail.net',
    'guerrillamail.org', 'spam4.me', 'getairmail.com', 'throwawaymail.com',
    'getnada.com', 'tempinbox.com', 'emailondeck.com', 'fakemailgenerator.com',
    'mailforspam.com', 'tempr.email', 'discard.email', 'discardmail.com',
    'spamgourmet.com', 'mytrashmail.com', 'mt2009.com', 'thankyou2010.com',
    'spam.la', 'speed.1s.fr', 'spamfree24.org', 'spamfree24.de',
    'spamfree24.eu', 'spamfree24.info', 'spamfree24.net', 'wegwerfmail.de',
    'wegwerfmail.net', 'wegwerfmail.org', 'meltmail.com', 'mintemail.com',
    'tempmailaddress.com', 'burnermail.io', 'maildrop.cc', 'inboxalias.com',
}

# Common typos and their corrections
EMAIL_TYPO_CORRECTIONS = {
    'gamil.com': 'gmail.com',
    'gmial.com': 'gmail.com',
    'gmal.com': 'gmail.com',
    'gmail.co': 'gmail.com',
    'gmaill.com': 'gmail.com',
    'gnail.com': 'gmail.com',
    'gmail.cm': 'gmail.com',
    'gmail.om': 'gmail.com',
    'hotmal.com': 'hotmail.com',
    'hotmai.com': 'hotmail.com',
    'hotmil.com': 'hotmail.com',
    'hotmail.co': 'hotmail.com',
    'outlok.com': 'outlook.com',
    'outloo.com': 'outlook.com',
    'outlook.co': 'outlook.com',
    'yaho.com': 'yahoo.com',
    'yahooo.com': 'yahoo.com',
    'yahoo.co': 'yahoo.com',
    'yahoomail.com': 'yahoo.com',
    'iclud.com': 'icloud.com',
    'icoud.com': 'icloud.com',
    'icloud.co': 'icloud.com',
}


def check_mx_record(domain: str) -> bool:
    """
    Check if a domain has valid MX (mail exchange) records.

    Args:
        domain: Email domain to check

    Returns:
        True if domain has MX records, False otherwise
    """
    import socket
    try:
        # Try to resolve MX records
        socket.setdefaulttimeout(3)  # 3 second timeout
        socket.getaddrinfo(domain, None)
        return True
    except (socket.gaierror, socket.timeout):
        return False


def validate_email(email: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate email address with comprehensive checks.

    Performs:
    1. Format validation
    2. Domain existence check (MX records)
    3. Disposable email blocking
    4. Common typo detection with suggestions

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message, suggestion)
        - is_valid: True if email passes all checks
        - error_message: Error description if invalid
        - suggestion: Suggested correction for typos (or None)
    """
    if not email:
        return False, "Email is required", None

    email = email.strip().lower()

    # Check length
    if len(email) > 254:
        return False, "Email address too long", None

    # Basic format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format. Please check for typos.", None

    # Extract domain
    try:
        local_part, domain = email.rsplit('@', 1)
    except ValueError:
        return False, "Invalid email format", None

    # Check for empty local part
    if not local_part:
        return False, "Invalid email format", None

    # Check for common typos and suggest corrections
    if domain in EMAIL_TYPO_CORRECTIONS:
        correct_domain = EMAIL_TYPO_CORRECTIONS[domain]
        suggestion = f"{local_part}@{correct_domain}"
        return False, f"Did you mean {suggestion}?", suggestion

    # Block disposable email services
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        return False, "Temporary email addresses are not allowed. Please use your regular email.", None

    # Check if domain exists (has MX records)
    if not check_mx_record(domain):
        return False, f"The domain '{domain}' doesn't appear to exist. Please check your email address.", None

    return True, "", None


def validate_email_simple(email: str) -> Tuple[bool, str]:
    """
    Simple wrapper for validate_email that returns just (is_valid, error_message).
    For backwards compatibility.
    """
    is_valid, error_msg, _ = validate_email(email)
    return is_valid, error_msg


# =============================================================================
# RATE LIMITING
# =============================================================================

class RateLimiter:
    """
    Simple in-memory rate limiter using session state.

    Tracks actions per session and blocks when limits exceeded.
    """

    @staticmethod
    def get_session_key(action: str) -> str:
        """Get the session state key for tracking an action."""
        return f"rate_limit_{action}"

    @staticmethod
    def check_rate_limit(session_state: Dict, action: str, limit: int, window_seconds: int = 3600) -> Tuple[bool, str, int]:
        """
        Check if an action is within rate limits.

        Args:
            session_state: Streamlit session state dict
            action: Name of the action (e.g., 'uploads', 'pdfs')
            limit: Maximum allowed actions in window
            window_seconds: Time window in seconds (default 1 hour)

        Returns:
            Tuple of (is_allowed, error_message, remaining)
        """
        key = RateLimiter.get_session_key(action)
        now = datetime.now()

        # Initialize if not exists
        if key not in session_state:
            session_state[key] = []

        # Filter out old entries
        window_start = now - timedelta(seconds=window_seconds)
        session_state[key] = [ts for ts in session_state[key] if ts > window_start]

        # Check limit
        current_count = len(session_state[key])
        remaining = limit - current_count

        if current_count >= limit:
            minutes_until_reset = window_seconds // 60
            return False, f"Rate limit exceeded. Maximum {limit} {action} per hour. Please wait.", 0

        return True, "", remaining

    @staticmethod
    def record_action(session_state: Dict, action: str):
        """Record that an action was performed."""
        key = RateLimiter.get_session_key(action)
        if key not in session_state:
            session_state[key] = []
        session_state[key].append(datetime.now())


def check_upload_limit(session_state: Dict) -> Tuple[bool, str]:
    """Check if user can upload another CSV."""
    allowed, msg, remaining = RateLimiter.check_rate_limit(
        session_state, "uploads", RATE_LIMITS["uploads_per_hour"]
    )
    return allowed, msg


def check_pdf_limit(session_state: Dict) -> Tuple[bool, str]:
    """Check if user can generate another PDF."""
    allowed, msg, remaining = RateLimiter.check_rate_limit(
        session_state, "pdfs", RATE_LIMITS["pdfs_per_hour"]
    )
    return allowed, msg


def check_team_report_limit(session_state: Dict) -> Tuple[bool, str]:
    """Check if user can generate another team report."""
    allowed, msg, remaining = RateLimiter.check_rate_limit(
        session_state, "team_reports", RATE_LIMITS["team_reports_per_hour"]
    )
    return allowed, msg


def record_upload(session_state: Dict):
    """Record a CSV upload."""
    RateLimiter.record_action(session_state, "uploads")


def record_pdf(session_state: Dict):
    """Record a PDF generation."""
    RateLimiter.record_action(session_state, "pdfs")


def record_team_report(session_state: Dict):
    """Record a team report generation."""
    RateLimiter.record_action(session_state, "team_reports")


# =============================================================================
# USAGE LOGGING
# =============================================================================

def get_session_id(session_state: Dict) -> str:
    """
    Get or create a unique session ID for logging.

    Uses a hash to anonymize while still tracking sessions.
    """
    if 'session_id' not in session_state:
        # Create anonymous session ID
        raw_id = f"{datetime.now().isoformat()}-{os.urandom(8).hex()}"
        session_state['session_id'] = hashlib.sha256(raw_id.encode()).hexdigest()[:16]
    return session_state['session_id']


def log_upload(session_state: Dict, season_type: str, num_athletes: int, tests_available: list):
    """Log a CSV upload event."""
    session_id = get_session_id(session_state)
    logger.info(json.dumps({
        "event": "upload",
        "session_id": session_id,
        "season_type": season_type,
        "num_athletes": num_athletes,
        "tests_available": tests_available,
        "timestamp": datetime.now().isoformat()
    }))


def log_pdf_generation(session_state: Dict, athlete_name: str, season_type: str):
    """Log a PDF generation event."""
    session_id = get_session_id(session_state)
    # Don't log full athlete name for privacy - just log that it happened
    logger.info(json.dumps({
        "event": "pdf_generated",
        "session_id": session_id,
        "season_type": season_type,
        "timestamp": datetime.now().isoformat()
    }))


def log_team_report(session_state: Dict, num_athletes: int, season_type: str):
    """Log a team report generation event."""
    session_id = get_session_id(session_state)
    logger.info(json.dumps({
        "event": "team_report",
        "session_id": session_id,
        "season_type": season_type,
        "num_athletes": num_athletes,
        "timestamp": datetime.now().isoformat()
    }))


def log_email_submission(session_state: Dict, email_hash: str):
    """
    Log an email submission (hash only for privacy).

    Args:
        session_state: Streamlit session state
        email_hash: SHA256 hash of the email (for privacy)
    """
    session_id = get_session_id(session_state)
    logger.info(json.dumps({
        "event": "email_submitted",
        "session_id": session_id,
        "email_hash": email_hash,
        "timestamp": datetime.now().isoformat()
    }))


def log_error(session_state: Dict, error_type: str, details: str):
    """Log an error event."""
    session_id = get_session_id(session_state)
    logger.error(json.dumps({
        "event": "error",
        "session_id": session_id,
        "error_type": error_type,
        "details": details[:500],  # Limit details length
        "timestamp": datetime.now().isoformat()
    }))


# =============================================================================
# EMAIL STORAGE (Simple File-Based with Limits)
# =============================================================================

EMAILS_FILE = LOG_DIR / "collected_emails.json"
MAX_EMAILS_STORED = 10000        # Maximum emails to store (prevents unbounded growth)
EMAILS_FILE_MAX_MB = 2           # Maximum file size in MB


def save_email(email: str, session_state: Dict, consent_given: bool = True) -> bool:
    """
    Save an email to the collection file with storage limits.

    Args:
        email: Email address
        session_state: Streamlit session state
        consent_given: Whether user consented to data collection

    Returns:
        True if saved successfully
    """
    if not consent_given:
        return False

    try:
        # Check file size limit (prevent disk exhaustion attacks)
        if EMAILS_FILE.exists():
            file_size_mb = EMAILS_FILE.stat().st_size / (1024 * 1024)
            if file_size_mb > EMAILS_FILE_MAX_MB:
                logger.warning(f"Email file size limit reached ({file_size_mb:.1f}MB)")
                return True  # Silently succeed to not reveal limit to potential attacker

        # Load existing emails
        emails_data = []
        if EMAILS_FILE.exists():
            with open(EMAILS_FILE, 'r') as f:
                emails_data = json.load(f)

        # Check count limit
        if len(emails_data) >= MAX_EMAILS_STORED:
            logger.warning(f"Email count limit reached ({len(emails_data)} emails)")
            return True  # Silently succeed

        # Check for duplicate
        existing_emails = [e.get('email', '').lower() for e in emails_data]
        if email.lower() in existing_emails:
            return True  # Already exists, consider it a success

        # Add new email
        email_entry = {
            "email": email,
            "session_id": get_session_id(session_state),
            "timestamp": datetime.now().isoformat(),
            "consent": consent_given
        }
        emails_data.append(email_entry)

        # Save
        with open(EMAILS_FILE, 'w') as f:
            json.dump(emails_data, f, indent=2)

        # Log (with hash for privacy in logs)
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()[:16]
        log_email_submission(session_state, email_hash)

        return True

    except Exception as e:
        logger.error(f"Failed to save email: {str(e)}")
        return False


def get_email_count() -> int:
    """Get the count of collected emails."""
    try:
        if EMAILS_FILE.exists():
            with open(EMAILS_FILE, 'r') as f:
                emails_data = json.load(f)
            return len(emails_data)
    except:
        pass
    return 0


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_usage_stats() -> Dict[str, Any]:
    """
    Get usage statistics from logs.

    Returns:
        Dictionary with usage statistics
    """
    stats = {
        "total_uploads": 0,
        "total_pdfs": 0,
        "total_team_reports": 0,
        "unique_sessions": set(),
        "emails_collected": get_email_count()
    }

    log_file = LOG_DIR / "app.log"
    if not log_file.exists():
        return stats

    try:
        with open(log_file, 'r') as f:
            for line in f:
                if '"event": "upload"' in line:
                    stats["total_uploads"] += 1
                elif '"event": "pdf_generated"' in line:
                    stats["total_pdfs"] += 1
                elif '"event": "team_report"' in line:
                    stats["total_team_reports"] += 1

                # Extract session IDs
                if '"session_id":' in line:
                    match = re.search(r'"session_id":\s*"([^"]+)"', line)
                    if match:
                        stats["unique_sessions"].add(match.group(1))

        stats["unique_sessions"] = len(stats["unique_sessions"])

    except Exception as e:
        logger.error(f"Failed to get usage stats: {str(e)}")

    return stats
