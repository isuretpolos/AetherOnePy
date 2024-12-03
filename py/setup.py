import subprocess
import sys

required_packages = [
    'Flask',
    'flask-cors',
    'waitress',
    'qrcode[pil]',
    'PIL',
    'python-dateutil'
]

def install_package(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def check_and_install_packages():
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            install_package(package)

if __name__ == '__main__':
    check_and_install_packages()