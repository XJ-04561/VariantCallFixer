from setuptools import setup, find_packages

setup(
    name="VariantCallFixer",
    version=1.0,
    url=None,
    description="Create and read vcf files.",

    # Author details
    author="Fredrik Sörensen",
    author_email="fredrik.sorensen@foi.se",

    license='GNU GENERAL PUBLIC LICENSE version 3',

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.8",

    keywords="VCF variant-calling",

    install_requires=[],
    entry_points={"console_scripts": [
                    "VariantCallFixer=VariantCallFixer.CommandLineParser:main"
    ]})
