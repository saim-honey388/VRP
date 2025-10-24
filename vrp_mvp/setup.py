from setuptools import setup, find_packages

setup(
    name="vrp_mvp",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "geopy",
        "requests",
        "folium",
        "click",
        "pydantic"
    ],
    python_requires=">=3.8",
)
