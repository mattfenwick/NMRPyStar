from distutils.core import setup

setup(
    name='NMRPyStar',
    version='0.0.15',
    packages=['nmrpystar', 
              'nmrpystar.unparse', 
              'nmrpystar.examples',
              'nmrpystar.test'],
    license='MIT',
    author='Matt Fenwick',
    author_email='mfenwick100@gmail.com',
    url='https://github.com/mattfenwick/NMRPyStar',
    description='a parser for the NMR-Star data format'
)