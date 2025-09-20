"""
Setup script for Legion AI Agent Swarm
"""
from setuptools import setup, find_packages
import os

# Read the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="legion-ai",
    version="1.0.0",
    author="Legion Development Team",
    author_email="legion@example.com",
    description="AI Agent Swarm for Code Intelligence and Automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/legion-ai/legion",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "asyncio-mqtt>=0.11.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "pyyaml>=6.0",
        "flask>=2.3.0",
        "flask-socketio>=5.3.0",
        "python-socketio>=5.8.0",
        "ollama>=0.1.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "google-generativeai>=0.3.0",
        "chromadb>=0.4.0",
        "pathlib2>=2.3.0",
        "typing-extensions>=4.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "sphinx>=7.0.0",
        ],
        "tts": [
            "pyttsx3>=2.90",
            "TTS>=0.22.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "sphinx>=7.0.0",
            "pyttsx3>=2.90",
            "TTS>=0.22.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "legion=legion.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "legion": [
            "config/*.yaml",
            "dashboard/templates/*",
            "dashboard/static/*",
        ],
    },
    keywords="ai agent swarm coding assistant development automation",
    project_urls={
        "Bug Reports": "https://github.com/legion-ai/legion/issues",
        "Source": "https://github.com/legion-ai/legion",
        "Documentation": "https://legion-ai.readthedocs.io/",
    },
)