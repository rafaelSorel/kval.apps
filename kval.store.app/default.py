#!/usr/bin/env python2.7

__author__ = 'kval team'

from kvalstore.provider import Provider
import kvalstore.runner as runner

def startup():
    """
    Startup entry point
    """
    __provider__ = Provider()
    runner.run(__provider__)
