"""
This is a conditional setup script that checks if the system is a Raspberry Pi or a different system.
It replaces the typical requirements.txt installation with a direct installation of packages using pip.
The requirements.txt alone is not able to identify the system type.
"""

import subprocess
import sys
import os

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
    'psutil',
    'flasgger'
]


def is_raspberry_pi():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            content = f.read()
            return 'BCM' in content or 'Raspberry Pi' in content
    except:
        return False


def install_package(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


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


def install_plugin_requirements():
    plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    if not os.path.isdir(plugins_dir):
        print(f"[PLUGIN-SETUP] No plugins directory found at {plugins_dir}")
        return
    for plugin_name in os.listdir(plugins_dir):
        plugin_path = os.path.join(plugins_dir, plugin_name)
        if os.path.isdir(plugin_path):
            req_path = os.path.join(plugin_path, 'requirements.txt')
            if os.path.exists(req_path):
                print(f"[PLUGIN-SETUP] Installing requirements for plugin: {plugin_name}")
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_path])
                except Exception as e:
                    print(f"[PLUGIN-SETUP] Failed to install requirements for {plugin_name}: {e}")
            else:
                print(f"[PLUGIN-SETUP] No requirements.txt for plugin: {plugin_name}")


if __name__ == '__main__':
    """
    Installs automatically the required dependencies
    """
    check_and_install_packages()
    install_plugin_requirements()
