from setuptools import setup, find_packages

setup(
    name="proyecto-final-covid",
    version="1.0.0",
    description="Análisis de datos de COVID-19 en Colombia",
    author="FactorX",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.38.0",
        "pandas>=2.2.2",
        "dask[dataframe]>=2024.5.0",
        "plotly>=5.22.0",
        "psutil>=5.9.8",
        "pyarrow>=16.1.0",
        "numpy>=1.26.4",
        "requests>=2.31.0"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "covid-analisis=app_analisis_covid:main",
        ],
    },
)