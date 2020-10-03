import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = ["tika==1.24", "tqdm==4.50", "psutil==5.7.2"]

setuptools.setup(
    name="tikatree",
    version="0.1.0",
    author="Zeigren",
    author_email="zeigren@zeigren.com",
    description="Directory tree metadata parser using Apache Tika",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://phabricator.kairohm.dev/diffusion/49/",
    project_urls={"Project Page": "https://phabricator.kairohm.dev/project/view/51/",},
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["tikatree = tikatree.tikatree:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    install_requires=REQUIREMENTS,
    python_requires=">=3.7",
)
