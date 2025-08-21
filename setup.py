"""
股票分析系統安裝配置
"""
from setuptools import setup, find_packages
import os

# 讀取 README
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# 讀取依賴
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='stock-analyzer',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='台灣股市技術分析和自動選股系統',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/stock-analyzer',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'black>=23.7.0',
            'isort>=5.12.0',
            'flake8>=6.0.0',
        ],
        'jupyter': [
            'ipython>=8.14.0',
            'jupyter>=1.0.0',
            'notebook>=6.5.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'stock-analyzer=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'stock_analyzer': ['*.json', '*.yaml', '*.yml'],
    },
    keywords='stock analysis taiwan financial LINE bot',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/stock-analyzer/issues',
        'Source': 'https://github.com/yourusername/stock-analyzer',
        'Documentation': 'https://github.com/yourusername/stock-analyzer/wiki',
    },
)