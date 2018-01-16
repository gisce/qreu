# -*- coding: utf-8 -*-

from qreu import local


class SenderContext():
    """
    Context Manager to Send e-mails using werkzeug.local*

    This manager allows to encapsulate the sender configurations to send the email
    from qreu.Email in any possible way.

    The configurations appendend to the SenderContext may have a callable method
    `send_method` and all required argumentsin the self object

    *: werkzeug.local is subject to copyright under BSD license, see the "local.py"
    """
    def __init__(self):
        self.context_manager = local.LocalManager()

    def add_config(self, **kwargs):
        """
        Adds a new config to the SenderContext
        The configuration can be provided with two different ways:

        - Provide an already built SenderConfig
        - Provide all the required parameters via `kwargs`

        :raise ValueError:     If sender_config is provided and isn't
                                    a valid SenderConfig instance
        :param sender_config:   A SenderConfig instance to add into the manager
        :type sender_config:    SenderConfig
        :param kwargs:          All params required to init a SenderConfig
        """
        config = local.Local()
        send_method = kwargs.get('send_method', False)
        if not send_method or not callable(send_method):
            raise ValueError(
                'SenderConfig requires a callable "send_method" argument')
        for key, value in kwargs.items():
            if key == 'send_method':
                config.send = value
                continue
            config.__setattr__(name=key, value=value)
        self.context_manager.locals.append(config)

    def has_configs(self):
        """
        Returns boolean indicating if any configuration has been set
        """
        return any(self.context_manager.locals)

    @property
    def configs(self):
        """
        Returns all configs with a generator
        """
        for config in self.context_manager.locals:
            yield config

sendcontext = SenderContext()
