from setuptools import setup
import os
import shutil

# Create ~/.rbible/bibles directory if it doesn't exist
user_bible_dir = os.path.join(os.path.expanduser("~"), ".rbible", "bibles")
os.makedirs(user_bible_dir, exist_ok=True)

# Copy Bible files to user directory during installation
source_bible_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bibles")
if os.path.exists(source_bible_dir):
    for file in os.listdir(source_bible_dir):
        if file.endswith('.mybible'):
            source_file = os.path.join(source_bible_dir, file)
            dest_file = os.path.join(user_bible_dir, file)
            shutil.copy2(source_file, dest_file)
            print(f"Copied {file} to {user_bible_dir}")

# Define custom install commands to ensure Bible files are copied
from setuptools.command.install import install
from setuptools.command.develop import develop

class CustomInstallCommand(install):
    def run(self):
        self._copy_bible_files()
        install.run(self)
    
    def _copy_bible_files(self):
        user_bible_dir = os.path.join(os.path.expanduser("~"), ".rbible", "bibles")
        os.makedirs(user_bible_dir, exist_ok=True)
        source_bible_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bibles")
        if os.path.exists(source_bible_dir):
            for file in os.listdir(source_bible_dir):
                if file.endswith('.mybible'):
                    source_file = os.path.join(source_bible_dir, file)
                    dest_file = os.path.join(user_bible_dir, file)
                    shutil.copy2(source_file, dest_file)
                    print(f"Copied {file} to {user_bible_dir}")

class CustomDevelopCommand(develop):
    def run(self):
        self._copy_bible_files()
        develop.run(self)
    
    def _copy_bible_files(self):
        user_bible_dir = os.path.join(os.path.expanduser("~"), ".rbible", "bibles")
        os.makedirs(user_bible_dir, exist_ok=True)
        source_bible_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bibles")
        if os.path.exists(source_bible_dir):
            for file in os.listdir(source_bible_dir):
                if file.endswith('.mybible'):
                    source_file = os.path.join(source_bible_dir, file)
                    dest_file = os.path.join(user_bible_dir, file)
                    shutil.copy2(source_file, dest_file)
                    print(f"Copied {file} to {user_bible_dir}")

setup(
    name="rbible",
    version="0.1",
    py_modules=["rbible"],
    entry_points={
        'console_scripts': [
            'rbible=rbible:main',
        ],
    },
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
    },
)