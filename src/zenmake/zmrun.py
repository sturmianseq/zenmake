#!/usr/bin/env python3
# coding=utf-8
#

"""
Copyright (c) 2019, Alexander Magola
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import os

# It's should be set to specific path to ZenMake if current script is copied to
# some different path without all the other files of ZenMake.
ZENMAKE_DIR = None

#######################################################################

if not ZENMAKE_DIR:
    ZENMAKE_DIR = os.path.abspath(__file__)
    ZENMAKE_DIR = os.path.dirname(os.path.realpath(ZENMAKE_DIR))

def main():
    """
    Prepare sys paths and run
    """

    if ZENMAKE_DIR not in sys.path:
        sys.path.insert(0, ZENMAKE_DIR)

    try:
        from zm import starter
    except ImportError:
        print('Cannot import starter.py. Check that ZENMAKE_DIR has a valid path')
        return 1

    return starter.run()

if __name__ == '__main__':
    sys.exit(main())
