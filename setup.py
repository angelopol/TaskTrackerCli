from setuptools import setup

setup(
    name="TaskTrackerCli",
    version="1.0.0",
    description="Una app en línea de comandos para manejar tareas.",
    author="angelopol",
    url="https://github.com/angelopol/TaskTrackerCli",
    py_modules=["TaskTrackerCli"],
    entry_points={
        "console_scripts": [
            "TaskTrackerCli=TaskTrackerCli:main",
        ],
    },
    install_requires=[
        "tabulate",
    ],
    tests_require=[
        "pytest",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
