import setuptools


setuptools.setup(
    name='chess_tournament',
    version='0.0.1',
    description='Terminal App for chess_tournaments',
    author='Yoann Guillard',
    author_email='',
    packages=['chess_tournament'],
    # install_requires=setuptools.find_packages(),
    install_requires=['tinydb'],
    extras_require={
        'dev': [''],
    },
    license='GNU v3'
)
