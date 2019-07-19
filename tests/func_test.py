# coding=utf-8
#

# pylint: skip-file

"""
 Copyright (c) 2019, Alexander Magola. All rights reserved.
 license: BSD 3-Clause License, see LICENSE for more details.
"""

import sys
import os
import subprocess
import shutil
import pytest
from waflib import Build
from waflib.ConfigSet import ConfigSet
import tests.common as cmn
from zm import utils, buildconfutil, assist, cli
import starter

joinpath = os.path.join

PLATFORM = utils.platform()
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_PROJECTS_DIR = joinpath(TESTS_DIR, 'projects')
ZM_BIN = os.path.normpath(joinpath(TESTS_DIR, os.path.pardir, "zenmake"))

def collectProjectDirs():
    result = []
    for dirpath, _, filenames in os.walk(TEST_PROJECTS_DIR):
        if 'buildconf.py' not in filenames:
            continue
        prjdir = os.path.relpath(dirpath, TEST_PROJECTS_DIR)
        if prjdir == 'cpp/005-custom-toolchain' and PLATFORM == 'windows':
            print('We ignore tests for %r on windows' % prjdir)
            continue
        result.append(prjdir)
    result.sort()
    return result

#@pytest.mark.usefixtures("setupModule")
class TestProject(object):

    def _runZm(self, cmdline):
        timeout = 60 * 5
        proc = subprocess.Popen(cmdline, stdout = subprocess.PIPE,
                            stderr = subprocess.STDOUT, cwd = self.cwd,
                            env = os.environ.copy(), universal_newlines = True)
        if utils.PY3:
            stdout, stderr = proc.communicate(timeout = timeout)
        else:
            stdout, stderr = proc.communicate()

        if proc.returncode != 0:
            print('\n' + stdout)
        return proc.returncode, stdout, stderr

    def _checkBuildResults(self, cmdLine, resultExists):
        # checks for target files
        cmd, _ = starter.handleCLI(self.confHandler, cmdLine[1:], True)
        self.confHandler.handleCmdLineArgs(cmd)
        buildtype = self.confHandler.selectedBuildType

        for taskName, taskParams in self.confHandler.tasks.items():
            taskVariant = assist.getTaskVariantName(buildtype, taskName)
            cacheConfFile = assist.makeCacheConfFileName(
                                            self.confPaths.zmcachedir, taskVariant)
            env = ConfigSet(cacheConfFile)
            target = taskParams.get('target', taskName)
            executable = False
            fileNamePattern = '%s'
            features = taskParams.get('features', '').split()
            for feature in features:
                # find pattern via brute force :)
                key = feature + '_PATTERN'
                if key not in env:
                    continue
                fileNamePattern = env[key]
                executable = feature.endswith('program')

            targetpath = joinpath(self.confPaths.buildout, buildtype,
                                  fileNamePattern % target)
            assert os.path.exists(targetpath) == resultExists
            assert os.path.isfile(targetpath) == resultExists
            if resultExists and executable:
                assert os.access(targetpath, os.X_OK)

    def _setup(self, request, tmpdir):

        testName = request.node.originalname
        if not testName:
            testName = request.node.name

        #projectDirName = request.param
        projectDirName = 'prj'

        tmpdirForTests = cmn.SHARED_TMP_DIR
        #tmptestDir = joinpath(tmpdirForTests, testName, projectDirName)
        tmptestDir = joinpath(tmpdirForTests, projectDirName)
        shutil.rmtree(tmptestDir, ignore_errors = True)
        #tmptestDir = joinpath(str(tmpdir.realpath()), projectDirName)

        shutil.copytree(joinpath(TEST_PROJECTS_DIR, request.param), tmptestDir)

        self.cwd = tmptestDir
        projectConf = buildconfutil.loadConf('buildconf',
                                            self.cwd, withImport = False)
        self.confHandler = assist.BuildConfHandler(projectConf)
        self.confPaths = self.confHandler.confPaths

        pythonbin = sys.executable
        if not pythonbin:
            pythonbin = 'python'
        self.pythonbin = pythonbin

    @pytest.fixture(params = collectProjectDirs())
    def allprojects(self, request, tmpdir):

        def teardown():
            pass

        request.addfinalizer(teardown)
        self._setup(request, tmpdir)

    @pytest.fixture(params = ['cpp/005-custom-toolchain'])
    def customtoolchains(self, request, tmpdir):
        self._setup(request, tmpdir)

    def testConfigure(self, allprojects, unsetEnviron):

        cmdLine = [self.pythonbin, ZM_BIN, 'configure', '-v']
        assert self._runZm(cmdLine)[0] == 0
        self._checkBuildResults(cmdLine, False)
        assert os.path.isfile(self.confPaths.wafcachefile)
        assert os.path.isfile(self.confPaths.zmcmnfile)

        cmdLine = [self.pythonbin, ZM_BIN, 'build', '-v']
        assert self._runZm(cmdLine)[0] == 0
        self._checkBuildResults(cmdLine, True)

    def testBuild(self, allprojects, unsetEnviron):

        # simple build
        cmdLine = [self.pythonbin, ZM_BIN, 'build', '-v']
        assert self._runZm(cmdLine)[0] == 0
        self._checkBuildResults(cmdLine, True)

    def testBuildAndClean(self, allprojects, unsetEnviron):

        # simple build
        cmdLine = [self.pythonbin, ZM_BIN, 'build', '-v']
        assert self._runZm(cmdLine)[0] == 0
        self._checkBuildResults(cmdLine, True)

        # clean
        cmdLine = [self.pythonbin, ZM_BIN, 'clean', '-v']
        assert self._runZm(cmdLine)[0] == 0
        assert os.path.isdir(self.confPaths.buildroot)
        assert os.path.isdir(self.confPaths.buildout)
        assert os.path.isfile(self.confPaths.wafcachefile)
        assert os.path.isfile(self.confPaths.zmcmnfile)
        self._checkBuildResults(cmdLine, False)

    def testBuildAndDistclean(self, allprojects, unsetEnviron):

        # simple build
        cmdLine = [self.pythonbin, ZM_BIN, 'build', '-v']
        assert self._runZm(cmdLine)[0] == 0
        self._checkBuildResults(cmdLine, True)

        # distclean
        assert os.path.isdir(self.confPaths.buildroot)
        cmdLine = [self.pythonbin, ZM_BIN, 'distclean', '-v']
        assert self._runZm(cmdLine)[0] == 0
        assert not os.path.exists(self.confPaths.buildroot)

    @pytest.mark.skipif(PLATFORM == 'windows',
                        reason = 'I have no useful windows installation for tests')
    def testCustomToolchain(self, customtoolchains, unsetEnviron):

        cmdLine = [self.pythonbin, ZM_BIN, 'build', '-v']
        returncode, stdout, stderr =  self._runZm(cmdLine)
        assert returncode == 0
        self._checkBuildResults(cmdLine, True)

        cmd, _ = starter.handleCLI(self.confHandler, cmdLine[1:], True)
        self.confHandler.handleCmdLineArgs(cmd)

        for taskName, taskParams in self.confHandler.tasks.items():
            toolchain = taskParams.get('toolchain', None)
            assert toolchain is not None
            if not toolchain.startswith('custom-'):
                continue
            emukind = toolchain[7:]
            assert emukind
            checkmsg = '%s wrapper for custom toolchain test' % emukind
            assert checkmsg in stdout