Qreu
====

.. image:: https://github.com/gisce/qreu/workflows/Python%20Testing/badge.svg
    :target: https://github.com/gisce/qreu/actions
.. image:: https://coveralls.io/repos/github/gisce/qreu/badge.svg?branch=master
    :target: https://coveralls.io/github/gisce/qreu?branch=master


Email Wrapper to `python email module <https://docs.python.org/library/email.html>`_

**Supported Python Versions:** 2.7, 3.5, 3.8, 3.9, 3.10, 3.11, 3.12

Installation
------------

.. code-block:: bash

    pip install qreu

Basic Usage
-----------

.. code-block:: python

    # -*- coding: utf-8 -*-
    from qreu import Email
    
    # Create a simple email
    email = Email()
    email.set_from('sender@example.com')
    email.set_to(['recipient@example.com'])
    email.set_subject('Hello from Qreu!')
    email.set_text('This is a plain text message.')
    
    # Send the email (requires proper SMTP configuration)
    # email.send()

Features
--------

- **Python 2.7 and 3.x compatibility** - Works seamlessly across Python versions
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
