import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = ["tika==1.23.0"]

setuptools.setup(
    name="tikatree",
    version="0.0.3",
    author="Zeigren",
    author_email="zeigren@zeigren.com",
    description="Directory tree metadata parser using Apache Tika",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://phabricator.kairohm.dev/diffusion/49/",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["tikatree = tikatree.tikatree:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    python_requires=">=3.8",
)
