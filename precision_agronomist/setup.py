from setuptools import setup, find_packages

setup(
    name="precision-agronomist",
    version="1.0.0",
    description="AI-powered plant disease detection system",
    author="Ayush Yajnik",
    author_email="ayushyajnik1@outlook.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "crewai[tools]>=0.203.0,<1.0.0",
        "pandas>=2.2.0,<3.0.0",
        "numpy>=1.26.0,<2.0.0",
        "gdown>=4.7.0",
        "pillow>=10.0.0",
        "deep-translator>=1.11.4",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "precision-agronomist=precision_agronomist.main:run",
        ],
    },
)
