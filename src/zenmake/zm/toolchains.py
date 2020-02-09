# coding=utf-8
#

"""
 Copyright (c) 2019, Alexander Magola. All rights reserved.
 license: BSD 3-Clause License, see LICENSE for more details.
"""

import itertools

from zm.error import ZenMakeError
from zm.autodict import AutoDict as _AutoDict
from zm.pyutils import maptype
from zm.constants import PLATFORM

# to change outside in modules for task features
langTable = {}

# private cache
_cache = _AutoDict()

def get(lang, platform = PLATFORM):
    """
    Return toolchains tuple for selected language for current platform
    """

    if not lang or lang not in langTable:
        raise ZenMakeError("Compiler for feature '%s' is not supported" % lang)

    toolchains = _cache[platform][lang].get('toolchains')
    if toolchains:
        return toolchains

    table = langTable[lang]
    if table is None or not isinstance(table, maptype):
        # Code of Waf was changed
        raise NotImplementedError()

    if platform == 'all':
        toolchains = tuple(set(itertools.chain(*table.values())))
    else:
        _platform = platform
        if platform == 'windows':
            _platform = 'win32'
        toolchains = table.get(_platform, table['default'])

    _cache[platform][lang].toolchains = toolchains
    return toolchains

def getAll(platform = PLATFORM):
    """
    Return tuple of unique compiler names supported on selected platform
    """

    toolchains = _cache[platform].get('all-toolchains')
    if toolchains:
        return toolchains

    toolchains = [ c for l in langTable for c in get(l, platform) ]
    toolchains = tuple(set(toolchains))
    _cache[platform]['all-toolchains'] = toolchains
    return toolchains
