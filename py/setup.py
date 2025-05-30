"""
This is a conditional setup script that checks if the system is a Raspberry Pi or a different system.
It replaces the typical requirements.txt installation with a direct installation of packages using pip.
The requirements.txt alone is not able to identify the system type.
"""

import subprocess
import sys
import platform

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
    'openai',
    'psutil'
]


def is_raspberry_pi():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            content = f.read()
            return 'BCM' in content or 'Raspberry Pi' in content
    except:
        return False


def install_package(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--break-system-packages', package])


def check_and_install_packages():
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            install_package(package)

    # Conditionally install GPIO support if on Raspberry Pi
    if is_raspberry_pi():
        try:
            print("We are on a Raspberry Pi, importing gpiozero...")
            from gpiozero import LED
        except ImportError:
            print("Installing gpiozero (Raspberry Pi detected)...")
            install_package('gpiozero')


if __name__ == '__main__':
    """
    Installs automatically the required dependencies
    """
    check_and_install_packages()
