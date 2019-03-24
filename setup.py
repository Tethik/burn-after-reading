from setuptools import setup, find_packages

setup(
    name="burn-after-reading",
    version="1.3",
    packages=find_packages(),
    install_requires=["Flask>=0.12.2"],
    zip_safe=False,
    include_package_data=True,
)
