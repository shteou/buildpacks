import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="buildpacks",
    version="0.0.1",
    author="Stewart Platt",
    author_email="shteou@gmail.com",
    description="A tool for building Dockerfiles from a buildpack-like specification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shteou/buildpacks",
    entry_points={"console_scripts": ["buildpacks=buildpacks.builder:main"]},
    packages=["buildpacks"],
    install_requires=[
    ],
    package_data={
      "buildpacks": ["data/*"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

