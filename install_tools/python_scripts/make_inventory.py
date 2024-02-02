from pathlib import Path
import sys

# set package_man project root directory in string type object
CURRENT_DIR = Path(__file__).parent
PJROOT_DIR = CURRENT_DIR.parent.parent
SETTINGS_DIR = PJROOT_DIR / "settings_package_man"
AIRFLOW_DIR = PJROOT_DIR / "airflow"
sys.path.append(str(SETTINGS_DIR))
sys.path.append(str(AIRFLOW_DIR))

# import and set global objects
from settings_ansible import ANSIBLE_CONF
from lib_package_man import MakePlaybook

PLAYBOOK_DIR = PJROOT_DIR / "playbook"
INVENTORY_FNAME = ANSIBLE_CONF["inventory_fname"]


def make_inventory(Path_inventory_file=(PLAYBOOK_DIR/INVENTORY_FNAME)):
    ins_MP = MakePlaybook()

    fpath = str(Path_inventory_file)
    ins_MP.make_inventory(fpath)

if __name__ == '__main__':
    make_inventory()