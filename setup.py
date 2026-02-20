from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="kreativ-diktalo",
    version="0.1.0",
    author="Kreativ Diktáló Team",
    description="Intelligens Windows diktáló alkalmazás Whisper és LLM alapú szövegtisztítással",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kreativ-diktalo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "kreativ-diktalo=src.main:main",
        ],
    },
    include_package_data=True,
)
