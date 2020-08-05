import setuptools


with open('README.txt') as f:
    README = f.read()

setuptools.setup(
    name='NMRPyStar',
    version='1.0.0',
    python_requires=">=3.5",
    # install_requires=[''],
    # packages=setuptools.find_packages(),
    packages=[
        'nmrpystar',
        'nmrpystar.unparse'
    ],
    license='MIT',
    author='Matt Fenwick',
    author_email='mfenwick100@gmail.com',
    url='https://github.com/mattfenwick/NMRPyStar',
    description='a parser for the NMR-STAR data format',
    # TODO this causes the twine upload to break, need to figure out why
    # long_description=README,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
)
