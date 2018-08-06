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

import logging
import inspect
import fnmatch
import jsonpath_rw
from conf import load_config


class CustomParser(object):

    def __init__(self):
        super(CustomParser, self).__init__()
        self.conf = load_config()
        self.log = logging.getLogger(__name__)

    def parse(self, msg):
        """
        Takes a message and converts it to a message object. How the message
        is converted into a BaseMessage is defined by the
        message_mapping config.
        :param msg: the message as as delivered by fedmsg-hub
        :return: a subclass of BaseMessage. If there is no mapping defined
                 for the topic the message was delivered to, return None.
        """
        for cls_name, mapping in self.conf.message_mapping.items():
            # extracts the topic from the message
            if 'topic' not in mapping:
                self.log.warn('No topic path configured for %s, skipping', cls_name)
                continue
            topic_expr = jsonpath_rw.parse(mapping['topic'])
            results = [r.value for r in topic_expr.find(msg)]
            if not results:
                self.log.warn('No topic found at %s, skipping', mapping['topic'])
                continue
            topic = results[0]

            # we have the message topic, now see if it it's a match for this class
            if 'matches' not in mapping:
                self.log.warn('No topic match configured for %s, skipping', cls_name)
                continue
            matches = mapping['matches']
            if not isinstance(matches, (list, tuple)):
                matches = [matches]
            for match in matches:
                if fnmatch.fnmatch(topic, match):
                    self.log.debug('Topic %s matched %s, using class %s',
                                   topic, match, cls_name)
                    break
            else:
                self.log.debug('%s does not match topic %s, skipping', cls_name, topic)
                continue

            # we know this is the correct class, so extract the rest of the
            # attribute values from the message
            attrs = {}
            for attr, path in mapping.items():
                if attr in ['topic', 'matches']:
                    continue
                attr_expr = jsonpath_rw.parse(path)
                results = [r.value for r in attr_expr.find(msg)]
                if results:
                    attrs[attr] = results[0]
                else:
                    attrs[attr] = None

            # can't import at the top of the file, or we create a circular
            # reference at class-loading time
            import module_build_service.messaging
            # get a reference to the class and construct an instance
            msg_cls = getattr(module_build_service.messaging, cls_name, None)
            if not msg_cls:
                self.log.warn('Could not find %s class, skipping', cls_name)
                continue
            try:
                return msg_cls(**attrs)
            except:
                accepted_args = inspect.getargspec(msg_cls.__init__).args
                # Remove 'self' from the accepted arguments
                accepted_args.pop(0)
                error = ('Error constructing {0}. The args of the constructor '
                         'are: {1}. The args passed in were (not in order): {2}'
                         .format(cls_name, ', '.join(accepted_args),
                                 ', '.join(attrs.keys())))
                # incorrect number of parameters passed to the constructor, probably
                self.log.exception(error)
                continue

        # nothing worked
        return None
