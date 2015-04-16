from setuptools import setup, find_packages

setup(
    name         = 'burn-after-reading',
    version      = '1.0',
    packages     = find_packages(),
    test_suite   = "burn.tests",
)
