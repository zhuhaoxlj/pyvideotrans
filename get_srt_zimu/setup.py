"""
Setup script for Whisper Auto Captions
"""

from setuptools import setup, find_packages

with open("README_PYTHON.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="whisper-auto-captions",
    version="1.0.0",
    author="Whisper Auto Captions Team",
    description="Auto Captions for Final Cut Pro Powered by OpenAI's Whisper Model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shaishaicookie/fcpx-auto-captions",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "PySide6>=6.6.0",
        "openai-whisper>=20230314",
        "pydub>=0.25.1",
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "whisper-captions=main:main",
        ],
    },
)

