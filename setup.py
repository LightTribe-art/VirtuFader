import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-pkg-YOUR-USERNAME-HERE", # Replace with your own username
    version="0.0.1",
    author="Rick Winkler",
    author_email="rick@lighttribe.art",
    description="A MIDI to OSC bridge for the FaderPort 16",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LightTribe-art/VirtuFader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: MIDI"
    ],
    python_requires='>=3.6',
)