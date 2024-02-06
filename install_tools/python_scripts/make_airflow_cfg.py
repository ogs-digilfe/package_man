from pathlib import Path

CURRENT_DIR = Path(__file__).parent
PJROOT_DIR = CURRENT_DIR.parent.parent
AIRFLOW_CFG_DIR =PJROOT_DIR / "airflow"
AIRFLOW_CFG_FNAME = "airflow.cfg"

# import & set gloal objects
from configparser import ConfigParser
from datetime import datetime
import subprocess

def make_airflow_cfg(airflow_cfg_dir, airflow_cfg_fname):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    airflow_cfg_path = str(airflow_cfg_dir/airflow_cfg_fname)

    # original　airflow.cfgのバックアップ
    # ConfigParserを使って編集するとコメント文が全部消えてしまうので、originalのconfファイルをバックアップで残しておく
    command = f"cp {airflow_cfg_path} {airflow_cfg_path}.{timestamp}.original.bak"
    subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)

    # airflow.cfgの編集と保存
    conf = ConfigParser()
    conf.read(airflow_cfg_path)

    section1 = "core"
    option_key1 = "default_timezone"
    option_value1 = "Asia/Tokyo"

    section2 = "webserver"
    option_key2 = "default_ui_timezone"
    option_value2 = "Asia/Tokyo"

    conf[section1][option_key1] = option_value1
    conf[section2][option_key2] = option_value2

    with open(airflow_cfg_path, "w") as f:
        conf.write(f)

if __name__ == '__main__':
    make_airflow_cfg(airflow_cfg_dir=AIRFLOW_CFG_DIR, airflow_cfg_fname=AIRFLOW_CFG_FNAME)