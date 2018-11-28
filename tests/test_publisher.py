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
import os
from mock import patch

import pytest

import mbs_messaging_umb
import mbs_messaging_umb.conf
# XXX horrible hack to get tests running in travis-ci
# remove when koji is in pypi
# For more info, see:
# https://lists.fedoraproject.org/archives/list/koji-devel@lists.fedorahosted.org/thread/XLIR4DSXXRU3OYWXEZWJQJAEEIOUQEXY/
# koji is targeted for inclusion in pypi during the 1.15 development cycle.
import sys
sys.modules['kobo.rpmlib'] = ''
# XXX


class TestPublisher(object):

    @patch('mbs_messaging_umb.publisher.fedmsg.config')
    def setup_method(self, test_method, fm_conf):
        with patch('mbs_messaging_umb.publisher.fedmsg.config'):
            self.pub = mbs_messaging_umb.StompPublisher()

    def test_to_host_and_port(self):
        result = self.pub._to_host_and_port('localhost')
        assert result == [('localhost', 61612)]
        result = self.pub._to_host_and_port('localhost:1234')
        assert result == [('localhost', 1234)]
        result = self.pub._to_host_and_port('foo:123,bar,baz:456')
        assert result, [('foo', 123), ('bar', 61612), ('baz', 456)]

    @patch('mbs_messaging_umb.publisher.fedmsg.config')
    def test_missing_fedmsg_config(self, fm_conf):
        fm_conf.load_config.return_value = {}
        with pytest.raises(RuntimeError, match='^missing config: '):
            self.pub.publish(None, None, None, None)

    @patch.object(mbs_messaging_umb.conf, '_CONF_MODULE', new=None)
    @patch.dict(os.environ, MBS_MESSAGING_UMB_CONFIG='/foo')
    @patch('mbs_messaging_umb.conf.log')
    def test_missing_config_file(self, log):
        conf = mbs_messaging_umb.conf.load_config()
        assert conf is None
        log.exception.assert_called_once_with('Could not load config file: /foo')

    @patch('mbs_messaging_umb.publisher.load_config')
    @patch('mbs_messaging_umb.publisher.stomp.Connection')
    @patch('mbs_messaging_umb.publisher.fedmsg.config')
    def test_publish(self, fm_conf, Conn, load_conf):
        fm_conf.load_config.return_value = {
            'stomp_uri': 'foo:1234',
            'stomp_ssl_crt': '/tmp/crt',
            'stomp_ssl_key': '/tmp/key',
        }
        load_conf.return_value.dest_prefix = '/topic/foo'
        self.pub.publish('module.state.change', 'test', None, 'mbs')
        assert Conn.call_count == 1
        conn = Conn.return_value
        conn.start.assert_called_once_with()
        conn.connect.assert_called_once_with(wait=True)
        assert conn.send.call_count == 1
        args, kws = conn.send.call_args
        assert len(args) == 0
        assert len(kws) == 2
        headers = kws['headers']
        assert headers['content-type'] == 'text/json'
        assert headers['content-length'] == len(json.dumps('test'))
        assert headers['destination'] == '/topic/foo.module.state.change'

    @patch('mbs_messaging_umb.publisher.load_config')
    @patch('mbs_messaging_umb.publisher.stomp.Connection')
    @patch('mbs_messaging_umb.publisher.fedmsg.config')
    def test_publish_json(self, fm_conf, Conn, load_conf):
        fm_conf.load_config.return_value = {
            'stomp_uri': 'foo:1234',
            'stomp_ssl_crt': '/tmp/crt',
            'stomp_ssl_key': '/tmp/key',
        }
        load_conf.return_value.dest_prefix = '/topic/foo'
        msg = {'foo': 1, 'bar': 'baz'}
        self.pub.publish('module.state.change', msg, None, 'mbs')
        conn = Conn.return_value
        assert conn.send.call_count == 1
        args, kws = conn.send.call_args
        assert len(kws) == 2
        assert 'message' in kws
        sent_msg = kws['message']
        assert isinstance(sent_msg, str)
        assert msg == json.loads(sent_msg)

    @patch('mbs_messaging_umb.publisher.load_config')
    @patch('mbs_messaging_umb.publisher.stomp.Connection')
    @patch('mbs_messaging_umb.publisher.fedmsg.config')
    def test_stomp_publish(self, fm_conf, Conn, load_conf):
        fm_conf.load_config.return_value = {
            'stomp_uri': 'foo:1234',
            'stomp_ssl_crt': '/tmp/crt',
            'stomp_ssl_key': '/tmp/key',
        }
        load_conf.return_value.dest_prefix = '/topic/foo'
        mbs_messaging_umb.stomp_publish('module.state.change', 'test', None, 'mbs')
        conn = Conn.return_value
        conn.start.assert_called_once_with()
        conn.connect.assert_called_once_with(wait=True)
        assert conn.send.call_count == 1
        args, kws = conn.send.call_args
        assert len(args) == 0
        assert len(kws) == 2
        headers = kws['headers']
        assert headers['content-type'] == 'text/json'
        assert headers['content-length'] == len(json.dumps('test'))
        assert headers['destination'] == '/topic/foo.module.state.change'

        # send another message to use the cached publisher
        mbs_messaging_umb.stomp_publish('module.state.change2', 'test2', None, 'mbs')
        args, kws = conn.send.call_args
        assert len(args) == 0
        assert len(kws) == 2
        headers = kws['headers']
        assert headers['content-type'] == 'text/json'
        assert headers['content-length'] == len(json.dumps('test2'))
        assert headers['destination'] == '/topic/foo.module.state.change2'
