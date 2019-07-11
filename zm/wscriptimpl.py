# coding=utf-8
#

"""
 Copyright (c) 2019, Alexander Magola. All rights reserved.
 license: BSD 3-Clause License, see LICENSE for more details.
"""

import os
from waflib import Utils, Logs
from waflib.ConfigSet import ConfigSet
import zm.assist as assist
from zm.utils import maptype

def options(opt):

    # This method WAF calls before all other methods including 'init'

    # Remove incompatible options
    #opt.parser.remove_option('-o')
    #opt.parser.remove_option('-t')
    pass

def init(ctx):

    assist.buildConfHandler.handleCmdLineArgs()

def configure(conf):

    confHandler = assist.buildConfHandler

    # make independent copy of root env
    rootEnv   = assist.deepcopyEnv(conf.env)
    toolchainsEnv = assist.loadToolchains(conf, confHandler, rootEnv)

    conf.env.alltasks = assist.loadTasksFromCache()

    buildtype = confHandler.selectedBuildType
    tasks = confHandler.tasks
    conf.env.alltasks[buildtype] = tasks

    for taskName, taskParams in tasks.items():
        
        taskParams['name'] = taskName

        # make variant for each task: 'buildtype.taskname'
        taskVariant = assist.getTaskVariantName(buildtype, taskName)
        # store it
        taskParams['task.build.env'] = taskVariant

        # set up env with toolchain for task
        toolchain = taskParams.get('toolchain', None)
        parentEnv = toolchainsEnv.get(toolchain, rootEnv)
        parentEnv = assist.copyEnv(parentEnv)

        # and switch to selected env
        conf.setenv(taskVariant, env = parentEnv)

        # set variables
        assist.setTaskEnvVars(conf.env, taskParams)

        # run checkers
        assist.runConfTests(conf, buildtype, taskParams)

        # Waf always loads all *_cache.py files in directory 'c4che' during 
        # build step. So it loads all stored variants even though they 
        # aren't needed. And I decided to save variants in different files and 
        # load only needed ones.
        conf.env.store(assist.makeCacheConfFileName(taskVariant))
        
        # It's necessary to delete variant from conf.all_envs otherwise 
        # waf will store it in 'c4che'
        conf.setenv('')
        conf.all_envs.pop(taskVariant, None)

    # Remove unneccesary envs
    for toolchain in toolchainsEnv.keys():
        conf.all_envs.pop(toolchain, None)

    assist.dumpZenMakeCommonFile()
        
def build(bld):

    if bld.variant is None:
        bld.fatal('No variant!')

    buildtype = bld.variant
    if buildtype not in bld.env.alltasks:
        if bld.cmd == 'clean':
            Logs.info("Buildtype '%s' not found. Nothing to clean" % buildtype)
            return
        else:
            bld.fatal("Buildtype '%s' not found! Was step 'configure' missed?" 
                    % buildtype)

    # Some comments just to remember some details.
    # - ctx.path represents the path to the wscript file being executed
    # - ctx.root is the root of the file system or the folder containing 
    #   the drive letters (win32 systems)

    # Path must be relative
    srcDir = os.path.relpath(assist.SRCROOT, assist.BUILDROOT)
    # Since ant_glob can traverse both source and build folders, it is a best 
    # practice to call this method only from the most specific build node.
    srcDirNode = bld.path.find_dir(srcDir)

    tasks = bld.env.alltasks[buildtype]

    import zm.cli
    allowedTasks = zm.cli.selected.args.buildtasks
    if not allowedTasks:
        allowedTasks = tasks.keys()

    for taskName, taskParams in tasks.items():

        if taskName not in allowedTasks:
            continue

        # task env variables are stored in separative env 
        # so it's need to switch in
        bld.variant = taskParams['task.build.env']
        # load environment for this task
        bld.all_envs[bld.variant] = ConfigSet(assist.makeCacheConfFileName(bld.variant))
        
        target = taskParams.get('target', taskName)
        kwargs = dict(
            name     = taskParams.get('name', taskName),
            target   = assist.makeTargetPath(bld, buildtype, target),
            features = taskParams.get('features', ''),
            lib      = taskParams.get('sys-libs', []),
            libpath  = taskParams.get('sys-lib-path', []),
            rpath    = taskParams.get('rpath', []),
            use      = taskParams.get('use', []),
            vnum     = taskParams.get('ver-num', ''),
        )

        src = taskParams.get('source')
        if src:
            if isinstance(src, maptype):
                kwargs['source'] = srcDirNode.ant_glob(
                    incl       = src.get('include', ''),
                    excl       = src.get('exclude', ''),
                    ignorecase = src.get('ignorecase', False),
                    generator = True)
            else:
                src = Utils.to_list(src)
                kwargs['source'] = [ srcDirNode.find_node(s) for s in src ]

        includes = assist.handleTaskIncludesParam(taskParams)
        if includes:
            kwargs['includes'] =  includes

        # create build task generator
        bld(**kwargs)

    # It's neccesary to revert to origin variant otherwise WAF won't find
    # correct path at the end of building step.
    bld.variant = buildtype
