from distutils.util import convert_path
from setuptools import setup, find_packages



setup(
    name="apple_gssm_contract_engine",
    author="GSSM Solutions & Strategy AIML",
    author_email="GSSM-AIML@group.apple.com",
    description="GSSM Humming Bird",
    python_requires=">=3.11",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apple Internal",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=['tmp_folder']),
    include_package_data=True,
    install_requires=[
    ],
    tests_require=[
        # Packages required for tests
        'pytest==8.3.2',
        'pydub'
    ],
    test_suite='tests',
)
