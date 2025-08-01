import smtplib
import dns.resolver
import socket
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Generator
import time

class EmailValidator:
    def __init__(self, timeout: int = 10, max_workers: int = 5):
        self.timeout = timeout
        self.max_workers = max_workers
        self.email_regex = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
    
    def is_valid_email_syntax(self, email: str) -> bool:
        """Check if email has valid syntax using regex."""
        return bool(self.email_regex.match(email.strip()))
    
    def get_mx_records(self, domain: str) -> List[str]:
        """Get MX records for a domain."""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return [str(mx.exchange).rstrip('.') for mx in mx_records]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.LifetimeTimeout, Exception):
            return []
    
    def validate_smtp(self, email: str, mx_servers: List[str]) -> Tuple[bool, str]:
        """Validate email using SMTP connection."""
        if not mx_servers:
            return False, "No MX records found"
        
        for mx_server in mx_servers[:3]:  # Try up to 3 MX servers
            try:
                # Create SMTP connection with timeout
                server = smtplib.SMTP(timeout=self.timeout)
                server.set_debuglevel(0)
                
                # Connect to MX server
                server.connect(mx_server, 25)
                server.helo('validator.local')
                
                # Try to start mail transaction
                code, message = server.mail('test@validator.local')
                if code != 250:
                    server.quit()
                    continue
                
                # Try to validate recipient
                code, message = server.rcpt(email)
                server.quit()
                
                if code == 250:
                    return True, "SMTP validation successful"
                elif code == 550:
                    return False, "Mailbox not found"
                elif code == 553:
                    return False, "Invalid email format"
                else:
                    return False, f"SMTP error: {code} {message.decode() if isinstance(message, bytes) else message}"
            
            except smtplib.SMTPConnectError:
                continue  # Try next MX server
            except smtplib.SMTPTimeoutError:
                continue  # Try next MX server
            except smtplib.SMTPRecipientsRefused:
                return False, "Email rejected by server"
            except smtplib.SMTPServerDisconnected:
                continue  # Try next MX server
            except Exception as e:
                continue  # Try next MX server
        
        return False, "Could not connect to any MX server"
    
    def validate_single_email(self, email: str) -> Tuple[str, str, str, str]:
        """Validate a single email address."""
        email = email.strip().lower()
        
        # Extract domain
        try:
            domain = email.split('@')[1]
        except IndexError:
            return email, '', 'Invalid', 'Invalid email format'
        
        # Check syntax
        if not self.is_valid_email_syntax(email):
            return email, domain, 'Invalid', 'Invalid email syntax'
        
        try:
            # Get MX records
            mx_records = self.get_mx_records(domain)
            
            if not mx_records:
                return email, domain, 'Invalid', 'No MX records found'
            
            # Validate using SMTP
            is_valid, error_message = self.validate_smtp(email, mx_records)
            
            if is_valid:
                return email, domain, 'Valid', ''
            else:
                return email, domain, 'Invalid', error_message
        
        except Exception as e:
            return email, domain, 'Error', f'Validation error: {str(e)}'
    
    def validate_emails_batch(self, emails: List[str]) -> Generator[Tuple[str, str, str, str], None, None]:
        """Validate emails in batches using threading."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all emails for validation
            future_to_email = {
                executor.submit(self.validate_single_email, email): email 
                for email in emails
            }
            
            # Yield results as they complete
            for future in as_completed(future_to_email):
                try:
                    result = future.result()
                    yield result
                except Exception as e:
                    email = future_to_email[future]
                    domain = email.split('@')[1] if '@' in email else ''
                    yield email, domain, 'Error', f'Processing error: {str(e)}'
