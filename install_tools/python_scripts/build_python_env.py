from pathlib import Path

# set package_man project root directory in string type object
CURRENT_DIR = Path(__file__).parent
PJROOT_DIR = CURRENT_DIR.parent.parent.parent

TEMPLATE_DIR = CURRENT_DIR.parent / "playbook_templates"
INVENTORY_TEMPLATE_FNAME = "inventory.template"
PLAYBOOK_TEMPLATE_FNAME = "install_python_packages.template"
PLAYBOOK_DIR = CURRENT_DIR.parent / "playbook"
INVENTORY_FNAME = "inventory.yml"
PLAYBOOK_FNAME = "install_python_packages.yml"

# imoprt objects
import argparse
import os

#
# コマンドラインから引数として設定されたosパッケージシステムを読み込む
# ※)現時点ではaptしか対応していない。default値もaptなので、指定不要
#
def get_args():
    global OS_PACKAGE_SYSTEM

    description = '''build python environment on which this application will be installed'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--package', type=str, default="apt", help="set the os package system to which this aplication will be installed (now spport 'apt' only...)")
    args = parser.parse_args()
    OS_PACKAGE_SYSTEM = args.package

#
# templateファイルから、仮想環境を作成するためのinventoryファイルとplaybookを自動生成する
#
def _read_inventory_template():
    fpath = str(TEMPLATE_DIR / OS_PACKAGE_SYSTEM / INVENTORY_TEMPLATE_FNAME)
    with open(fpath, "r") as f:
        content = f.read()

    return content

def _save_inventory(inventory):
    fpath = str(PLAYBOOK_DIR / INVENTORY_FNAME)
    with open(fpath, "w") as f:
        f.write(inventory)

def _read_playbook_template():
    fpath = str(TEMPLATE_DIR / OS_PACKAGE_SYSTEM / PLAYBOOK_TEMPLATE_FNAME)
    with open(fpath, "r") as f:
        content = f.read()

        content = content.replace("{{ package }}", OS_PACKAGE_SYSTEM)
        content = content.replace("{{ venv_dir_path }}", str(PJROOT_DIR))

    return content

def _save_playbook(playbook):
    fpath = str(PLAYBOOK_DIR / PLAYBOOK_FNAME)
    with open(fpath, "w") as f:
        f.write(playbook)

def _make_playbook_dir():
    dpath = str(PLAYBOOK_DIR)
    os.makedirs(dpath, exist_ok=True)

def make_ansible_playbook():
    _make_playbook_dir()

    inventory = _read_inventory_template()
    _save_inventory(inventory)

    playbook = _read_playbook_template()
    _save_playbook(playbook)

#
# 
#

def build_python_env():
    get_args()
    make_ansible_playbook()
    play_ansible()
    
if __name__ == "__main__":
    build_python_env()