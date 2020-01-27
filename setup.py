from setuptools import setup
from setuptools import find_packages

def setup_package():

    from filabres import __version__
    REQUIRES = ['numpy', 'astropy', 'pandas', 'matplotlib']
    META_DATA = dict(
        name='filabres',
        version=__version__,
        description='Data Reduction Package for CAHA instruments',
        author='Enrique Galcerán / Nicolás Cardiel',
        author_email='cardiel@ucm.es',
        packages=find_packages('.'),
        entry_points={
            'console_scripts': [
                'filabres = filabres.filabres:main',
                'filabes-version = filabres.version:main'
            ],
            },
        install_requires=REQUIRES,
        zip_safe=False
        )

    setup(**META_DATA)


if __name__ == '__main__':
    setup_package()

