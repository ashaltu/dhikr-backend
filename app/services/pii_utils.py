import re


def redact_pii(text: str) -> str:
    if not text:
        return text
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = re.sub(email_pattern, '[EMAIL_REDACTED]', text)
    
    phone_patterns = [
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',                      # simple 123-456-7890
        r'\(\d{3}\)\s*\d{3}[-.\s]*\d{4}',                          # (123) 456 7890, (123)456-7890
        r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'  # international
    ]

    for pattern in phone_patterns:
        text = re.sub(pattern, '[PHONE_REDACTED]', text)
    
    uuid_pattern = r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
    text = re.sub(uuid_pattern, '[UUID_REDACTED]', text)
    
    token_patterns = [
        r'\b(?:Bearer\s+)?[A-Za-z0-9_-]{20,}\b',
        r'\b(?:token|key|api[_-]?key|access[_-]?token|auth[_-]?token)[=:]\s*[A-Za-z0-9_-]{10,}\b'
    ]
    for pattern in token_patterns:
        text = re.sub(pattern, '[TOKEN_REDACTED]', text, flags=re.IGNORECASE)
    
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    text = re.sub(ssn_pattern, '[SSN_REDACTED]', text)
    
    credit_card_pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    text = re.sub(credit_card_pattern, '[CARD_REDACTED]', text)
    
    return text


def redact_url(url: str) -> str:
    return redact_pii(url)


def redact_title(title: str) -> str:
    return redact_pii(title)
