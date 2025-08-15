from setuptools import setup, find_packages

setup(
    name='mcqgenrator',
    version='0.1.0',
    author='Gokul Sundeep',
    author_email='gokulsundeep@gmail.com',
    description='A tool to generate multiple choice questions from text',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
                        "openai", "langchain", "streamlit", "python-dotenv", "PyPDF2", "langchain-community",
                        "langchain-openai"
                    ],
    packages=find_packages(),
)