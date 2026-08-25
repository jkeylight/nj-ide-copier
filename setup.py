from setuptools import setup, find_packages

setup(
    name="nj-ide-copier",
    version="2.0.0",
    description="Intelligent bridge between DeepSeek AI chat and development environments",
    author="NJ IDE Copier Team",
    author_email="support@nj-ide-copier.dev",
    url="https://github.com/nj-ide-copier/nj-ide-copier",
    packages=find_packages(),
    install_requires=[
        "pyperclip",
        "psutil",
        "websockets",
        "python-dotenv",
        "cryptography",
        "pyjwt",
        "redis",
        "sqlalchemy",
        "fastapi",
        "uvicorn",
        "pydantic",
        "tqdm",
        "plyer",
    ],
    entry_points={
        "console_scripts": [
            "nj-ide-copier=src.server.main:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: IDEs",
    ],
)
