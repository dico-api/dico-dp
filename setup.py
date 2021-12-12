import setuptools

with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()

setuptools.setup(
    name="dico-dp",
    version="0.0.6",
    author="eunwoo1104",
    author_email="sions04@naver.com",
    description="Simple debugger and tester for dico-command.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dico-api/dico-dp",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=["dico-api", "dico-command", "psutil"],
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
