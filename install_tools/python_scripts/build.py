from pathlib import Path

# set package_man project root directory in string type object
CURRENT_DIR = Path(__file__).parent
PJROOT_DIR = CURRENT_DIR.parent.parent

TEMPLATE_DIR = CURRENT_DIR.parent / "playbook_templates"
INVENTORY_TEMPLATE_FNAME = "inventory.template"
PLAYBOOK_TEMPLATE_FNAME = "install_python_packages.template"
PLAYBOOK_DIR = CURRENT_DIR.parent / "playbook"
INVENTORY_FNAME = "inventory.yml"
PLAYBOOK_FNAME = "install_python_packages.yml"
DEFAULT_VENV_DIR = PJROOT_DIR.parent / ("venv_" + str(PJROOT_DIR).split("/")[-1])
AIRFLOW_HOME_PATH = PJROOT_DIR / "airflow"
ENVIRONMENT_FILE_PATH = "/etc/environment"
AIRFLOW_HOME_ENV_VAR = "AIRFLOW_HOME"
AIRFLOW__CORE__LOAD_EXAMPLES_VAR = "AIRFLOW__CORE__LOAD_EXAMPLES"


# imoprt objects
import argparse
import os
import subprocess
from datetime import datetime
from settings_airflow_version import INSTALLED_AIRFLOW_VERSION_INFO


#
# コマンドラインから引数として設定されたosパッケージシステムを読み込む
# ※)現時点ではaptしか対応していない。default値もaptなので、指定不要
#
def get_args():
    global OS_PACKAGE_SYSTEM, VENVPATH

    description = '''build python environment on which this application will be installed'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--package', type=str, default="apt", help="set the os package system to which this aplication will be installed (now spport 'apt' only...). default: apt")
    parser.add_argument('--venvpath', type=str, default=str(DEFAULT_VENV_DIR), help=f"set venv fullpath. default: {str(DEFAULT_VENV_DIR)}")
    args = parser.parse_args()
    OS_PACKAGE_SYSTEM = args.package
    VENVPATH = Path(args.venvpath)

#
# python3-pipとpython3-venvのinstall
#
def _package_exists(package_name):
    stdout = "Call _package_exists method"
    print(stdout)

    if OS_PACKAGE_SYSTEM == "apt":
        command = f"dpkg -l |grep {package_name}"
        # command = "dpkg -l |grep hello-world"
        
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True).stdout

    count = result.count(package_name)

    if count == 0:
        return False
    else:
        return True

def _install_package(package_name):
    stdout = "Call _install_package method"
    print(stdout)

    if OS_PACKAGE_SYSTEM == "apt":
        update_command = "sudo apt update"
        install_command =  f"sudo apt install {package_name}"
        
    print("update package list")
    result = subprocess.run(update_command, shell=True, stdout=subprocess.PIPE, text=True)
    print(result.stdout)
    print()

    stdout = "install f{package_name}"
    print(stdout)
    result = subprocess.run(install_command, shell=True, stdout=subprocess.PIPE, text=True)
    print(result.stdout)

def install_os_packages():
    stdout = "Call install_os_packages method"
    print(stdout)

    install_packages = ["python3-pip", "python3-venv"]
    for p in install_packages:
        package_exists = _package_exists(p)
        if package_exists:
            stdout = f"python3-pip package exists: --> skip apt install {p}"
            print(stdout)
        else:
            _install_package(p)
    print()


#
# venvの作成
#
def build_venv():
    stdout = "Call build_venv method"
    print(stdout)

    # 仮想環境作成先フォルダの作成(無ければ作る)
    venv_dir = str(VENVPATH)
    os.makedirs(venv_dir, exist_ok=True)

    # 仮想環境が作成済かどうかチェックする
    fp = str(VENVPATH/"pyvenv.cfg")
    if os.path.exists(fp):
        stdout = f"venv {VENVPATH} already exists --> skip building venv"
        print(stdout)

    else:
        stdout = f"building python venv in {VENVPATH}"
        print(stdout)
        command = f"python3 -m venv {VENVPATH}"
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
        stdout = f"complete building {VENVPATH}"
        print(stdout)
    
    print()

#
# 必要なpython packagesのinstall
#
def install_python_packages():
    stdout = "Call install_python_packages method"
    print(stdout)

    venvpath = str(VENVPATH)
    currentpath = str(CURRENT_DIR)

    # requirements.txtから必要なpypiのパッケージをinstallする
    venv_name = venvpath.split("/")[-1]
    stdout = f"install paython external packages required to venv {venv_name}"
    print(stdout)
    command = f"{venvpath}/bin/python -m pip install -r {currentpath}/requirements.txt"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
    print(result.stdout)
    print()

    # airflowのinstall
    # ここから
    stdout = f"install airflow to venv {venv_name}"
    print(stdout)
    airflow = INSTALLED_AIRFLOW_VERSION_INFO["target"]
    constraint_url = INSTALLED_AIRFLOW_VERSION_INFO["constraint"]
    command = f'{venvpath}/bin/python -m pip install "{airflow}" --constraint "{constraint_url}"'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
    print(result.stdout)
    print()

#
# airflow homeを環境変数にセットする
# export, /etc/environment
#
def set_environment(airflow_home_env_var, value, file="/etc/environment"):
    stdout = "Call set_environment_vars method"
    print(stdout)

    # Pathオブジェクトで渡された場合を想定して文字列オブジェクトに変換しておく
    value = str(value)
    export_value = value

    # timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # /etc/environmentに環境変数をセットする場合は、valueを""でクォートする必要がある
    if not '"' in value:
        value = f'"{value}"'

    # /etc/environmentに、環境変数AIRFLOW_HOMEがすでに設定されていた場合は、AIRFLOW_HOMEを設定せずに警告を出力する
    with open(str(file), "r") as f:
        content = ""
        flg = True
        for l in f:
            content += l
            env_var = l.split("=")[0]
            if env_var == airflow_home_env_var:
                stdout  = f"Warning: Environment variable '{l.strip()}' already set in {file}.\n"
                stdout += "skip setting environment varialbe\n"
                stdout += f'If new airflow home must be set in {file}, replace the old airflow home environment variable conf with: {env_var}={value}'
                print(stdout)
                flg = False

    # 環境変数AIRFLOW_HOMEの設定を/etc/environmentに追加
    if flg:
        content += f'\n{airflow_home_env_var}={value}\n'
        # /etc/environmentのバックアップをコピー
        command = f"sudo cp {file} {file}.{timestamp}.bak"
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)

        # /etc/environmentはownerがrootなので、一旦カレントディレクトリに作成してsudo権限を使ってmoveする
        current_dir = str(CURRENT_DIR)
        fpath = f"{current_dir}/environment"
        print(fpath)
        with open(fpath, "w") as f:
            f.write(content)
        command = f"sudo mv {current_dir}/environment {file}"
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)

def airflow_db_init():
    stdout = "Call airflow_db_migrate method"
    print(stdout)

    # db migration済である場合は、処理をスキップする
    fp = str(AIRFLOW_HOME_PATH / "airflow.db")
    if os.path.exists(fp):
        stdout = "Airflow db migration already done --> skip migrating airflow db"
        print(stdout)
        print()
        return

    venvpath = str(VENVPATH)

    # migrateでうまくいくと思われる。initはもうすぐ廃止されるとのこと。
    # command = f"{venvpath}/bin/python -m airflow db init"
    command = f"{venvpath}/bin/python -m airflow db migrate"

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
    print(result.stdout)


def build_python_venv():
    # defaultオプションでinstallする場合は、不要
    # defaultオプションのinstallで十分なので、なくても良いが、つけておいた
    get_args()

    # aptはpython subprocessモジュールから実行すると動きが不安定になるので、ここは最初に手動でinstallする。
    # $ sudo apt update
    # $ sudo apt install make python3-venv python3-pip
    # install_os_packages()
    
    build_venv()
    install_python_packages()

    # 環境変数の設定
    set_environment(AIRFLOW_HOME_ENV_VAR, AIRFLOW_HOME_PATH) # AIRFLOW_HOME
    set_environment(AIRFLOW__CORE__LOAD_EXAMPLES_VAR, "False") # skip loading defalut dag examples

    print()
    
if __name__ == "__main__":
    build_python_venv()