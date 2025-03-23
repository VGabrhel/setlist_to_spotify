from setuptools import setup, find_packages

setup(
    name="setlist-to-spotify",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "streamlit>=1.32.0",
        "spotipy>=2.23.0",
        "python-dotenv>=1.0.0",
        "Pillow>=10.2.0",
        "requests>=2.31.0"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Create Spotify playlists from setlist.fm data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/setlist-to-spotify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 