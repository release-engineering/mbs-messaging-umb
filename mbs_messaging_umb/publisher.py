# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Mike Bonnet <mikeb@redhat.com>


import json
import logging
import ssl
import uuid
import stomp
import fedmsg.config
from stomp.exception import ConnectFailedException

from .conf import load_config


class StompPublisher(object):
    _MAX_CONNECTION_RETRIES = 3

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self._using_legacy_stomppy = None

    @property
    def using_legacy_stomppy(self):
        if self._using_legacy_stomppy is None:
            try:
                # Check if stomp.py v4+ is being used
                stomp.Connection11
                self._using_legacy_stomppy = False
            except AttributeError:
                self._using_legacy_stomppy = True

        return self._using_legacy_stomppy

    @staticmethod
    def _to_host_and_port(uris):
        """
        Convert a comma-separated URI string to a list of
        (host, port) tuples.
        """
        results = []
        for uri in uris.split(','):
            host_and_port = uri.rsplit(':', 1)
            if len(host_and_port) == 2:
                host_and_port[1] = int(host_and_port[1])
            else:
                # Use the default STOMP port
                host_and_port.append(61612)
            results.append(tuple(host_and_port))
        return results

    def get_stomp_connection(self):
        """
        Start a connection to the message bus.
        """
        fm_conf = fedmsg.config.load_config()
        for opt in ['stomp_uri', 'stomp_ssl_crt', 'stomp_ssl_key']:
            if opt not in fm_conf:
                raise RuntimeError('missing config: {0}'.format(opt))

        uris = self._to_host_and_port(fm_conf['stomp_uri'])
        connection_kwargs = {
            'use_ssl': True,
            'ssl_cert_file': fm_conf['stomp_ssl_crt'],
            'ssl_key_file': fm_conf['stomp_ssl_key'],
            'ssl_ca_certs': '/etc/pki/tls/certs/ca-bundle.crt',
            'ssl_version': ssl.PROTOCOL_TLSv1_2,
            'timeout': 10.0
        }
        if self.using_legacy_stomppy:
            conn = stomp.Connection(uris, wait_on_receipt=True, version='1.1', **connection_kwargs)
        else:
            # In stomp.py v4, the `version` is determined by the "Connection" class used.
            # The `Connection` class is also an alias for `Connection11`, but let's use
            # `Connection11` directly to avoid issues in the future. Also, `wait_on_receipt` is not
            # supported. See: https://github.com/jasonrbriggs/stomp.py/issues/224
            conn = stomp.Connection11(uris, **connection_kwargs)

        conn.start()
        self.log.debug('Connecting to %s...', uris)
        conn.connect(wait=True)

        if self.using_legacy_stomppy:
            host_and_port = conn.get_host_and_port()
        else:
            host_and_port = '{}:{}'.format(*conn.transport.current_host_and_port)

        self.log.debug('Connected to %s', host_and_port)
        return conn

    def _try_to_get_stomp_connection(self):
        for attempt in range(1, self._MAX_CONNECTION_RETRIES + 1):
            try:
                return self.get_stomp_connection()
            except ConnectFailedException:
                if attempt == self._MAX_CONNECTION_RETRIES:
                    self.log.debug("Max retries reached when trying to get stomp connection.")
                    raise
                self.log.debug("Failed to get stomp connection. Attempt %d. Retrying.", attempt)

    def publish(self, topic, msg, conf, service):
        """
        Publish a message using the STOMP configuration from fedmsg.
        """
        conn = self._try_to_get_stomp_connection()
        dest = '.'.join([load_config().dest_prefix, topic])
        msg = json.dumps(msg)

        if self.using_legacy_stomppy:
            headers = {
                'content-length': len(msg),
                'content-type': 'text/json',
                'destination': dest,
                'receipt': str(uuid.uuid4())
            }
            self.log.debug('Sending message to %s, headers: %s', dest, headers)
            conn.send(message=msg, headers=headers)
        else:
            # In stomp.py v4+, content-length is automatically determined. Also,
            # waiting on receipt is not supported. See:
            # https://github.com/jasonrbriggs/stomp.py/issues/224
            self.log.debug('Sending message to %s', dest)
            conn.send(dest, msg, content_type='text/json')

        self.log.debug('Message successfully sent')
        conn.disconnect()
