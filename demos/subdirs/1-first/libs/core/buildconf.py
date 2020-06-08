
def check(**kwargs):
    # some checking
    return True

project = { 'version' : '0.4.0' }

tasks = {
    'corelib' : {
        'features' : 'shlib',
        'source'   :  dict( include = '**/*.c' ),
        'includes' : 'src',
        'export-includes' : True,
        'config-actions'  : [
            dict(do = 'check-headers', names = 'stdio.h'),
            check,
        ],
    },
}

matrix = [
    {
        'for' : { 'buildtype' : ['debug-gcc', 'release-gcc'], },
        'set' : {
            'toolchain' : 'gcc',
        }
    },
    {
        'for' : { 'buildtype' : ['debug-clang', 'release-clang'], },
        'set' : {
            'toolchain' : 'clang',
        }
    },
]
