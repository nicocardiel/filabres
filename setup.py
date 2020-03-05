from setuptools import setup
from setuptools import find_packages

def setup_package():

    from filabres import __version__
    REQUIRES = [
        'astropy',
        'matplotlib',
        'numpy',
        'pandas',
        'python-dateutil',
        'PyYaml',
        'setuptools',
        'scipy'
    ]
    META_DATA = dict(
        name='filabres',
        python_requires='>=3.7',
        version=__version__,
        description='Data Reduction Package for CAHA instruments',
        author='Enrique Galcerán / Nicolás Cardiel',
        author_email='cardiel@ucm.es',
        packages=find_packages('.'),
        package_data={
            'filabres.instrument': ['configuration_cafos.yaml'],
            'filabres.astromatic': [
                'default.param',
                'config.sex',
                'config.scamp'
            ]
        },
        entry_points={
            'console_scripts': [
                'filabres = filabres.filabres:main',
                'filabres-ximshow = filabres.ximshow:main',
                'filabres-version = filabres.version:main'
            ],
        },
        install_requires=REQUIRES,
        zip_safe=False
        )

    setup(**META_DATA)


if __name__ == '__main__':
    setup_package()

