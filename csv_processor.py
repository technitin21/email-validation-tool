import pandas as pd
import re
from typing import List, Set

class CSVProcessor:
    def __init__(self):
        self.email_regex = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
    
    def extract_emails(self, df: pd.DataFrame, email_column: str) -> List[str]:
        """Extract unique valid email addresses from a DataFrame column."""
        if email_column not in df.columns:
            raise ValueError(f"Column '{email_column}' not found in the CSV file")
        
        # Extract email column and remove NaN values
        email_series = df[email_column].dropna()
        
        # Convert to string and clean
        emails = email_series.astype(str).str.strip().str.lower()
        
        # Filter out empty strings and invalid entries
        emails = emails[emails != '']
        emails = emails[emails != 'nan']
        
        # Basic email format validation
        valid_emails = []
        for email in emails:
            if self.is_valid_email_format(email):
                valid_emails.append(email)
        
        # Return unique emails while preserving order
        return list(dict.fromkeys(valid_emails))
    
    def is_valid_email_format(self, email: str) -> bool:
        """Check if string has basic email format."""
        return bool(self.email_regex.match(email))
    
    def validate_csv_structure(self, df: pd.DataFrame) -> dict:
        """Validate CSV structure and provide information."""
        info = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'email_like_columns': [],
            'has_header': True  # Assume CSV has header
        }
        
        # Find columns that might contain emails
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['email', 'mail', 'e-mail']):
                info['email_like_columns'].append(col)
        
        return info
    
    def preview_emails(self, df: pd.DataFrame, email_column: str, limit: int = 10) -> List[str]:
        """Preview first few emails from the specified column."""
        if email_column not in df.columns:
            return []
        
        emails = df[email_column].dropna().astype(str).str.strip()
        return emails.head(limit).tolist()
    
    def get_domain_statistics(self, emails: List[str]) -> dict:
        """Get statistics about email domains."""
        domain_counts = {}
        
        for email in emails:
            if '@' in email:
                domain = email.split('@')[1]
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Sort by count descending
        sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_domains': len(domain_counts),
            'domain_distribution': dict(sorted_domains),
            'top_domains': sorted_domains[:10]
        }
