from setuptools import setup, find_packages

setup(
    name="license_system",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A PyQt6 license validation system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/license_system",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyQt6>=6.4.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "windows": ["wmi>=1.5.1"],
    }
) 