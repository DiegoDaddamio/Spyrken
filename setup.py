from setuptools import setup, find_packages


setup(
    name='spyrken',  
    version='0.1.7',         
    packages=find_packages(),
    install_requires=[       
        'numpy',
        'matplotlib','tqdm',
    ],

    author="DiegoDaddamio",
    author_email='diego.daddamio3110@gmail.com',
    description="Simulateur de circuits électriques linéaire pour l'analyse et la visualisation de ceux-ci.",
    url='https://github.com/DiegoDaddamio/Spyrken.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6', # Version minimale de Python requise
)