# coding=utf-8
#

# pylint: skip-file

"""
 Copyright (c) 2019, Alexander Magola. All rights reserved.
 license: BSD 3-Clause License, see LICENSE for more details.
"""

import os
import pytest
import starter

@pytest.fixture
def unsetEnviron(monkeypatch):
    from zm import toolchains
    varnames = toolchains.CompilersInfo.allVarsToSetCompiler()
    varnames.extend(toolchains.CompilersInfo.allFlagVars())
    for v in varnames:
        #os.environ.pop(v, None)
        monkeypatch.delenv(v, raising = False)

def pytest_report_header(config):
    from zm import utils
    utils.printSysInfo()
    return ""