import setuptools

with open('README.md') as f:
    README = f.read()

setuptools.setup(
    author="Matt Whitaker",
    author_email="whitaker@imageowl.com",
    name='pyTQA',
    description='Python Wrapper for the Image Owl Total QA',
    version='v1.0.0',
    long_description=README,
    url='https://github.com/imageowl/pyTQA.git',
    packages=setuptools.find_packages(),
    python_requires=">=3.8.5",
    install_requires=['requests', 'python-dateutil'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
)
