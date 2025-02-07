
fragment1 = """
program Empty
end program Empty
"""

fragment2 = """
program HelloWorld
    write (*,*) 'Hello, world!'
end program HelloWorld
"""

tasks = {
    'hello': {
        'features' : 'fcprogram',
        'source'   : 'src/hello.f90',
    },
    'sharedlib' : {
        'features' : 'fcshlib',
        'source'   : 'src/funcs.f90',
        'ver-num'  : '2.1.3',
    },
    'staticlib' : {
        'features' : 'fcstlib',
        'source'   : 'src/funcs2.f90',
    },
    'test' : {
        'features' : 'fcprogram',
        'source'   : 'src/calculator.f90 src/main.f90',
        'includes' : 'src/inc',
        'use'      : 'staticlib sharedlib',
        'configure'  : [
            dict( do = 'parallel', actions = [
                dict(do = 'check-code', text = fragment1, label = 'fragment1'),
                dict(do = 'check-code', text = fragment2, label = 'fragment2', execute = True)
            ]),
        ],
    },
}

buildtypes = {
    'release' : {
        #'toolchain': 'auto-fc',
        #'toolchain': 'gfortran',

        'fcflags.select' : {
            'windows ifort': '/O2',
            'default': '-O2',
        },
        'rpath' : '.',
    },
}

toolchains = {
    'gfortran': {
        'FCFLAGS' : '-Wall -W',
    },
    'ifort': {
        'FCFLAGS' : '-warn',
    },
}
