"""
WikiAccess - Transform DokuWiki into Accessible Documents
Setup configuration for wikiaccess package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="wikiaccess",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Transform DokuWiki into accessible HTML and Word documents with WCAG compliance reporting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wikiaccess",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'wikiaccess=wikiaccess.cli:main',
            'wikiaccess-convert=wikiaccess.unified:convert_wiki_page',
        ],
    },
    python_requires=">=3.7",
    install_requires=[
        "python-docx>=0.8.11",
        "requests>=2.31.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
        "Pillow>=10.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: System Administrators",
        "Topic :: Text Processing :: Markup",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Documentation",
        "Topic :: Accessibility",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="dokuwiki word html accessibility a11y wcag converter mathjax omml equations",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/wikiaccess/issues",
        "Source": "https://github.com/yourusername/wikiaccess",
        "Documentation": "https://github.com/yourusername/wikiaccess#readme",
    },
)
