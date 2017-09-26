mbs-messaging-umb
==================

A plugin for the Module Build Service to support sending and receiving messages from the Unified Message Bus
-----------------------------------------------------

The [Module Build Service](https://pagure.io/fm-orchestrator/) is a system
for building individual components (rpms) and aggregating them into modules
which can be treated as discrete units for testing and deployment.

The MBS was originally built to work with [fedmsg](http://fedmsg.com).
However, it has a pluggable system for message parsing and publising. This
package provides a plugin that enables fully config-driven message parsing,
and publishing using STOMP.

Build Status
------------

  | Branch | Status                         | Coverage                 |
  | ------ | ------------------------------ | ------------------------ |
  | master | [![][travisbadge]][travislink] | [![][covbadge]][covlink] |

  [travisbadge]: https://secure.travis-ci.org/release-engineering/mbs-messaging-umb.png?branch=master "Travis CI build status"
  [travislink]: https://travis-ci.org/release-engineering/mbs-messaging-umb "Travis CI for mbs-messaging-umb"
  [covbadge]: https://codecov.io/gh/release-engineering/mbs-messaging-umb/branch/master/graph/badge.svg "codecov.io status"
  [covlink]: https://codecov.io/gh/release-engineering/mbs-messaging-umb "codecov.io for mbs-messaging-umb"

Running the Tests
-----------------

    # install the test tool
    $ sudo dnf install python2-detox
    # Run it.
    $ detox

If detox is unavailable on your system, you can also use plain old tox.
