Qreu
====

.. image:: https://github.com/gisce/qreu/workflows/Python%20Testing/badge.svg
    :target: https://github.com/gisce/qreu/actions
.. image:: https://coveralls.io/repos/github/gisce/qreu/badge.svg?branch=master
    :target: https://coveralls.io/github/gisce/qreu?branch=master


Email Wrapper to `python email module <https://docs.python.org/library/email.html>`_

**Supported Python Versions:** 2.7, 3.11

Installation
------------

.. code-block:: bash

    pip install qreu

Basic Usage
-----------

.. code-block:: python

    # -*- coding: utf-8 -*-
    from qreu import Email
    
    # Create a simple email using constructor
    email = Email(
        subject='Hello from Qreu!',
        **{'from': 'sender@example.com'},  # Use dict for 'from' keyword
        to=['recipient@example.com'],
        body_text='This is a plain text message.'
    )
    
    # Alternative: Create email step by step
    email2 = Email()
    email2.add_header('from', 'sender@example.com')
    email2.add_header('to', 'recipient@example.com')
    email2.add_header('subject', 'Hello from Qreu!')
    email2.add_body_text(body_plain='This is a plain text message.')
    
    # Send the email (requires proper SMTP configuration)
    # email.send()

Features
--------

- **Python 2.7 and 3.11 compatibility** - Works seamlessly across these specific Python versions
- **Email composition** - Easy creation of plain text and HTML emails  
- **Attachment support** - Add files to your emails
- **Address parsing** - Handle email addresses with proper validation
- **Encoding handling** - Proper Unicode and encoding support
- **Lightweight** - Minimal dependencies, fast performance

Development
-----------

To set up for development:

.. code-block:: bash

    git clone https://github.com/gisce/qreu.git
    cd qreu
    pip install -r requirements-dev.txt
    pip install -e .
    
    # Run tests
    mamba
