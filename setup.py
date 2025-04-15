from setuptools import setup, find_packages

setup(
    name="wegnots",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'requests',
        'python-telegram-bot',
        'imaplib2'
    ],
)
