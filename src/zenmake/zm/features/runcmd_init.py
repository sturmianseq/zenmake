# coding=utf-8
#

"""
 Copyright (c) 2020, Alexander Magola. All rights reserved.
 license: BSD 3-Clause License, see LICENSE for more details.
"""

from os.path import relpath

from zm.pyutils import maptype
from zm.buildconf.schemeutils import ANYAMOUNTSTRS_KEY

CONF_TASKSCHEME_SPEC = {
    'base' : {
        'run' : {
            'type' : ('dict', 'str', 'func'),
            'dict-allow-unknown-keys' : False,
            'dict-vars' : {
                'cmd' : { 'type': ('str', 'func') },
                'cwd' : { 'type': 'str' },
                'env' : {
                    'type': 'dict',
                    'vars' : { ANYAMOUNTSTRS_KEY : { 'type': 'str' } },
                },
                'repeat' : { 'type': 'int' },
                'timeout' : { 'type': 'int' },
                'shell' : { 'type': 'bool' },
            },
        },
    },
    # Can be boolean or list of particular param names
    # True means all keys from 'base' and 'export' (prefix 'export-' will be added)
    'select' : True,
}

TASK_FEATURES_SETUP = {
    'runcmd' : {}
}

def getBuildConfTaskParamHooks():
    """
    Get pairs of (param, function) where the function is called during
    processing of task param in buildconf before actual processing
    """

    def handleParam(bconf, param):
        if param is None:
            return None
        if not isinstance(param, maptype):
            param = { 'cmd' : param }
        param['startdir'] = relpath(bconf.startdir, bconf.rootdir)
        return param

    return [('run', handleParam)]

def detectFeatures(tasks):
    """
    Function to detect features in buildconfig.
    It's used by zm.features.loadFeatures.
    It should return a list of detected features.
    """

    for taskParams in tasks.values():
        if 'runcmd' in taskParams['features']:
            return ['runcmd']
        if 'run' in taskParams:
            return ['runcmd']

    return []
