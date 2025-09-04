#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example script demonstrating qreu email library usage.

This example shows Python 2.7 and 3.x compatible usage patterns.
"""
from __future__ import absolute_import, print_function, unicode_literals

import sys
from datetime import datetime

# Import qreu components
from qreu import Email
from qreu.address import Address


def main():
    # type: () -> None
    """Main example function demonstrating qreu usage."""
    print("Qreu Email Library Example")
    print("Python version: {0}".format(sys.version))
    print("-" * 40)
    
    # Create a simple email
    print("\n1. Creating a simple text email:")
    email = Email(
        subject="Hello from Qreu!",
        body_text="This is a plain text email created with qreu library.",
        date=datetime.now()
    )
    email.add_header('from', "sender@example.com")
    email.add_header('to', "recipient@example.com")
    
    print("Subject:", email.subject)
    print("From:", email.from_)
    print("To:", email.to)
    
    # Create an email with HTML content
    print("\n2. Creating an HTML email:")
    html_content = """
    <html>
    <body>
        <h1>Hello from Qreu!</h1>
        <p>This is an <strong>HTML email</strong> with formatting.</p>
        <ul>
            <li>Python 2.7 compatible</li>
            <li>Python 3.x compatible</li>
            <li>Easy to use</li>
        </ul>
    </body>
    </html>
    """
    
    html_email = Email()
    html_email.add_header('subject', "HTML Email Example")
    html_email.add_header('from', "sender@example.com")
    html_email.add_header('to', ["recipient1@example.com", "recipient2@example.com"])
    html_email.add_header('cc', "cc@example.com")
    html_email.add_body_text(body_html=html_content, body_plain="This is the plain text version.")
    
    print("Subject:", html_email.subject)
    print("Recipients:", len(html_email.to), "addresses")
    
    # Working with addresses
    print("\n3. Working with email addresses:")
    addr = Address.parse("John Doe <john.doe@example.com>")
    print("Address name:", addr.display_name)
    print("Address email:", addr.address)
    print("Full address:", addr.display)
    
    # Parse an existing email
    print("\n4. Parsing email content:")
    raw_email = '''From: sender@example.com
To: recipient@example.com  
Subject: Test Message
Date: Thu, 01 Mar 2018 12:30:03 +0000

This is a test message body.
'''
    
    parsed_email = Email.parse(raw_email)
    print("Parsed subject:", parsed_email.subject)
    print("Parsed from:", parsed_email.from_)
    
    # Demonstrate Python 2/3 compatibility
    print("\n5. Python 2/3 compatibility features:")
    test_subject = "Test with unicode: àáâãäå"
    compat_email = Email(subject=test_subject)
    print("Unicode subject handled correctly:", compat_email.subject)
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()