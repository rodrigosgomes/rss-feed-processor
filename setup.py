from setuptools import setup, find_packages

setup(
    name="rss-feed-processor",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=1.0.0",
        "google-generativeai>=0.3.0",
        "jinja2>=3.1.2",
        "beautifulsoup4>=4.12.2",
        "requests>=2.31.0",
        "pytz>=2024.1",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "responses>=0.24.1",
            "cachetools>=5.3.2",
        ],
    },
)
