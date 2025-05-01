import subprocess
import sys

required_packages = [
    'requests',
    'Flask',
    'flask-cors',
    'flask_socketio',
    'waitress',
    'qrcode[pil]',
    'pygame',
    'PIL',
    'pyperclip',
    'python-dateutil',
    'gitpython',
    'opencv-python',
    'matplotlib',
    'eventlet',
    'scipy',
    'sphinx',
    'sphinx_rtd_theme',
    'openai'
]

# TODO: get the list for dependecies from the requirements.txt file
def install_package(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


def check_and_install_packages():
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            install_package(package)


if __name__ == '__main__':
    """
    Installs automatically the required dependencies
    """
    check_and_install_packages()
