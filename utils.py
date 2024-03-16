# utils.py
import re

# Function to replace date patterns with placeholders
def protect_dates(text):
    # Pattern for dates like 1930–31–32, including Unicode dashes
    date_pattern = r'\b\d{4}\u2013\d{2}\u2013\d{2}\b'
    dates = re.findall(date_pattern, text)
    for i, date in enumerate(dates):
        # Replace Unicode dashes with standard hyphens
        standard_date = date.replace('\u2013', '-')
        text = text.replace(date, f'{{DATE{i}}}')
        dates[i] = standard_date  # Update with standard hyphen
    return text, dates


# Function to restore date patterns
def restore_dates(text, dates):
    for i, date in enumerate(dates):
        text = text.replace(f'{{DATE{i}}}', date)
    return text