from pathlib import Path
import sys

# set package_man project root directory in string type object
CURRENT_DIR = Path(__file__).parent
PJROOT_DIR = CURRENT_DIR.parent.parent
SETTINGS_DIR = PJROOT_DIR / "settings_package_man"

sys.path.append(str(SETTINGS_DIR))

# import objects
from hostlist import MANAGED_HOSTS_DCT
from settings_ansible import ANSIBLE_CONF

import pandas as pd
import re
import yaml
import os
import csv
import json
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime as dt
import shutil
import os
import filecmp
import tarfile
import subprocess

# global variables
PLAYBOOK_DIR = PJROOT_DIR / "playbook"
SETTINGS_DIR = PJROOT_DIR / "settings_package_man"
DATA_DIR = PJROOT_DIR / "data_package_man"
HOSTS_OUTPUT_DIR = DATA_DIR / "hosts"
PACKAGES_OUTPUT_DIR =  DATA_DIR / "packages"
INVENTORY_FNAME = ANSIBLE_CONF["inventory_fname"]
HOSTNAME_WITH_IP = ANSIBLE_CONF["hostname_with_ip"]    
GET_OS_VERSION_PLAYBOOK_FNAME = ANSIBLE_CONF["get_os_version_playbook_fname"]
GET_PACKAGES_PLAYBOOK_FNAME = ANSIBLE_CONF["get_packages_playbook_fname"]
PACKAGE_DATA_FNAME = "package_list_data.parquet"
# 個別playbooks
UPGRADE_PACKAGE_PLAYBOOK_DIR = PLAYBOOK_DIR / "upgrade_package_playbook"
UPGRADE_PACKAGE_PLAYBOOK_FNAME = ANSIBLE_CONF["upgrade_package_playbook_fname"]

### ツール類
class PlaybookExecutor():
    def __init__(self):
        self.inventory = PLAYBOOK_DIR / INVENTORY_FNAME
        self.get_os_version_playbook =  PLAYBOOK_DIR / GET_OS_VERSION_PLAYBOOK_FNAME
        self.get_packages_playbook = PLAYBOOK_DIR / GET_PACKAGES_PLAYBOOK_FNAME

    # target_data = <"os_version"|"packages">
    def execute_collecting_data_playbook(self, target_data):
        stdout = f"Call PlaybookExecutor.execute_collecting_data_playbook method with parameter={target_data}"
        print(stdout)

        # cd
        os.chdir(str(PLAYBOOK_DIR))

        # execute playbook
        if target_data == "os_version":
            playbook = str(GET_OS_VERSION_PLAYBOOK_FNAME)
        elif target_data == "packages":
            playbook = str(GET_PACKAGES_PLAYBOOK_FNAME)
            
        inventory = str(INVENTORY_FNAME)
        ansible_command = f"ansible-playbook {playbook} -i {inventory}"
        process = subprocess.Popen(ansible_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # stdout, stderr
        print("Ansible Output:")
        print(stdout.decode())

        std_err = stderr.decode()
        if stderr == "":
            print("Ansible Error: no error")
        else:
            std_out = f"Ansible Error: {std_err}"
            print(std_out)      

# backup_target=<"raw_text_host_os_list"|"raw_text_host_packages_list"|"joined_parquet_host_os_packages_list"|"raw_josn_settings_hostlist"|"raw_josn_settings_ansible"|"playbook">
class PackageManBackup():
    def __init__(self, backup_target, saved_generation_num=3):
        self.backup_target = backup_target
        self.temporary_backupfile_extension = "temp_bak"
        self.backup_file_extention ="bak"
        self.backup_archive_extention = "tar.gz"
        self.saved_generation_num = saved_generation_num

        self.dir, self.fname_pattern, self.backup_fname_pattern = self._get_filepath_patterns_tpl()
        
        # pathlib.glob()はgeneratorなので、listに変換しないと複数回loopを回せない
        self.target_files = list(self.dir.glob(self.fname_pattern))
        self.backup_files = list(self.dir.glob("*.bak"))

    def move_to_temporaly_backup_files(self):
        stdout = "Call PackageManBackup.move_to_temporaly_backup_files method"
        print(stdout)
        TIMESTAMP = dt.now().strftime("%Y%m%d_%H%M")

        if len(self.target_files) == 0:
            stdout = f"No target files({self.fname_pattern}) --> skip moving source files to temporaly backup files"
            print(stdout)
            print()
            return

        for f in self.target_files:
            source = str(f)
            dest = f"{source}_{TIMESTAMP}.{self.temporary_backupfile_extension}" 

            shutil.move(source, dest)

            stdout = f"temporary backup file '{dest}' moved"
            print(stdout)
        print()

    def create_temporaly_backup_files(self):
        stdout = "Call PackageManBackup.create_temporaly_backup_files method"
        print(stdout)

        TIMESTAMP = dt.now().strftime("%Y%m%d_%H%M")

        for f in self.target_files:
            source = str(f)
            dest = f"{source}_{TIMESTAMP}.{self.temporary_backupfile_extension}" 

            shutil.copy(source, dest)

            stdout = f"temporary backup file '{dest}' generated"
            print(stdout)
        print()
    
    def extract_last_backup_files(self):
        stdout = "Call PackageManBackup.extract_last_backup_files method"
        print(stdout)

        # 最新バックアップファイルの取得
        file_pattern = f"*.{self.backup_archive_extention}"
        # あまりきれいじゃないけど・・・
        # temp_bakファイルにsourceの拡張子が残っていると別のメソッドで問題になるので、self.target_fileを拡張子付きで
        # 指定しているbackup_targetは、ここで拡張子を落としておく
        if (self.backup_target == "raw_josn_settings_hostlist") or (self.backup_target == "raw_josn_settings_ansible"): 
            file_pattern = f"{self.backup_fname_pattern}*.{self.backup_archive_extention}"

        backup_archive_files = list(self.dir.glob(file_pattern))


        # もしバックアップアーカイブがなければ、スキップする。
        if len(backup_archive_files) == 0:
            stdout = "No backup archive files --> skip extracting backup archive files"
            print(stdout)
            print()
            return

        # それ以外の場合は、最新バックアップファイルから、temporary backupファイルとして解凍する
        backup_archive_files.sort()
        last_backup_file = backup_archive_files[-1]

        last_backup_file_fp = str(last_backup_file)
        dest_dir_parts = last_backup_file_fp.split("/")[:-1]
        dest_dir = "/".join(dest_dir_parts)
        with tarfile.open(last_backup_file_fp, "r:gz") as tar:
            tar.extractall(path=dest_dir)

        # extentionを、.bakから.temp_bakに変更する
        file_pattern = f"*.{self.backup_file_extention}"
        target_files = list(self.dir.glob(file_pattern))

        for tf in target_files:
            sbf = str(tf)
            new_sbf = sbf.replace(self.backup_file_extention, self.temporary_backupfile_extension)

            # あまりきれいじゃないけど・・・
            # temp_bakファイルにsourceの拡張子が残っていると別のメソッドで問題になるので、self.target_fileを拡張子付きで
            # 指定しているbackup_targetは、ここで拡張子を落としておく
            if (self.backup_target == "raw_josn_settings_hostlist") or (self.backup_target == "raw_josn_settings_ansible"): 
                new_sbf = new_sbf.replace(".py", "")

            shutil.move(sbf, new_sbf)

            stdout = f"extract backup files: {new_sbf}"
            print(stdout)
            print()        

    def is_backup_archive_of_settings_package_man(self, backup_target):
        pass

    def is_backup_archive(self):
        stdout = "Call PackageManBackup.is_backup_archive method"
        print(stdout)

        # backup_targetごとのsearchするfileパターンのセット
        if (self.backup_target ==  "raw_josn_settings_hostlist") or (self.backup_target ==  "raw_josn_settings_ansible"):
            host_parts = self.fname_pattern.split(".")
            host_parts = host_parts[:-1]
            host_part = host_parts[0]
            file_pattern = f"{host_part}*.{self.backup_archive_extention}"
        else:
            file_pattern = f"*.{self.backup_archive_extention}"

        # バックアップアーカイブファイルの取得
        backup_archive_files = list(self.dir.glob(file_pattern))

        # もしバックアップアーカイブがなければ、Falseをreturn
        num_backup_archive_files = len(backup_archive_files)
        if num_backup_archive_files == 0:
            stdout = "No backup archive files --> skip extracting backup archive files"
            print(stdout)
            print()
            return False

        # Falseでなければ、Trueをreturn
        stdout = f"{num_backup_archive_files} backup archive files found --> extracting last backup archive file"
        print(stdout)
        print()
        return True

    def check_if_backup_required(self):
        stdout = "Call PackageManBackup.check_if_backup_required method"
        print(stdout)

        for f in self.target_files:
            original_file = str(f)
            file_pattern = original_file.split("/")[-1] + f"_*.{self.temporary_backupfile_extension}"
            # あまりきれいじゃないが・・
            # pj/settings_package_man/hostlist.pyとpj/settings_package_man/settings_ansible.pyは拡張子を取り除いているので、
            # ここでfile_petternを修正する必要がある
            if (self.backup_target == "raw_josn_settings_hostlist") or (self.backup_target == "raw_josn_settings_ansible"):
                file_pattern = file_pattern.replace(".py", "")

            temporary_backup_files = list(self.dir.glob(file_pattern))


            # temporary_backup_fileが存在するかどうかチェックして、なければスキップ
            # 本来は、ありえないシチュエーション。
            if len(temporary_backup_files) == 0:
                stdout = f"WARNING: {original_file}: temporary backup file not exist --> skip diff check"
                print(stdout)
                print()
                continue
            
            # もしバックアップアーカイブファイルが存在しなければ、Trueを返す
            if not self.is_backup_archive():
                stdout = f"New file found: {original_file} -> creating backup archive"
                print(stdout)
                print()
                return True           
            
            # original fileとtemporary backup fileの差分をチェックして、差分がなければbackupの作成をスキップ
            # 差分がある場合はバックアップを作成する
            temporary_backup_file = temporary_backup_files[-1]
            if not filecmp.cmp(original_file, temporary_backup_file):
                stdout = "original files changed --> create backup"
                print(stdout)
                print()
                return True

        stdout = "original files not changed --> skip creating backup"
        print(stdout)
        print()
        return False        

    def create_backup_archive_file(self):
        stdout = "Call PackageManBackup.create_backup_archive file method"
        print(stdout)

        TIMESTAMP = dt.now().strftime("%Y%m%d_%H%M")
        bfname = f"{self.backup_fname_pattern}_{TIMESTAMP}.tar.gz"

        p = f"*.{self.temporary_backupfile_extension}"
        backup_target_files = list(self.dir.glob(p))

        # temporary backup fileがなかったら、bckupファイルを作成せず、warningを出力して処理を終了
        if len(backup_target_files) == 0:
            print("WARNING: No temporary backup files --> skip creating backup")
            print()
            return 
        
        # backup 対象のfile名を変更(*.temp_bakから、*.bakへ)
        for bf in backup_target_files:
            sbf = str(bf)
            new_sbf = sbf.replace(self.temporary_backupfile_extension, self.backup_file_extention)
            shutil.move(sbf, new_sbf)

        # 対象ファイルを再度読み込む
        p = f"*.{self.backup_file_extention}"
        backup_target_files = list(self.dir.glob(p))

        # backupの作成
        # archiveファイルがフルパスで記録されると、解凍時に、解凍先フォルダからフルパスで解凍されてしまうことを避けるため、
        # os.chdirする。
        os.chdir(str(self.dir))
        with tarfile.open(bfname, 'w:gz') as gzf:
            for bf in backup_target_files:
                new_sbf = os.path.basename(str(bf))
                gzf.add(new_sbf)

                # addしたら、バックアップファイルの拡張子.bakを.temp_bakに戻して、後でdeleteできるようにする
                # 最後に.temp_bakファイルを削除する処理が走る
                temp_bak_bf = new_sbf.replace(self.backup_file_extention, self.temporary_backupfile_extension)
                shutil.move(new_sbf, temp_bak_bf)
                
                bf_fullpath = str(self.dir/new_sbf)
                stdout = f"added backup archive: {bf_fullpath}"
                print(stdout)
                
        bf_fullpath = str(self.dir/bfname)
        stdout = f"backup file is created: {bf_fullpath}"
        print(stdout)
        print()

    def delete_temporaly_backup_files(self):
        stdout = "Call PackageManBackup.delete_temporaly_backup_files method"
        print(stdout)
        for f in self.target_files:
            original_file = str(f)

            # あまりきれいじゃないけど・・
            # settings_package_manのfileは拡張子がついていると問題が起きるので、originalから拡張子を取り除く
            if (self.backup_target == "raw_josn_settings_hostlist") or (self.backup_target == "raw_josn_settings_ansible"):
                original_file = original_file.replace(".py", "")

            file_pattern = original_file.split("/")[-1] + "*.temp_bak"
            temporary_backup_files = list(self.dir.glob(file_pattern))

            # temporary_backup_fileが存在するかどうかチェックして、なければスキップ
            if len(temporary_backup_files) == 0:
                stdout = f"WARNING: {original_file}: temporary backup file not exist --> delete temporary backup files process skipped"
                print(stdout)
                print()
                break

            # 消し漏れのtemporary backup fileも含めて削除
            for bf in temporary_backup_files:
                delete_target_file = str(bf)
                os.remove(delete_target_file)

                stdout = f"{delete_target_file} removed"
                print(stdout)
        print()
    
    def delete_old_bakup_files(self):
        stdout = "Call PackageManBackup.delete_old_bakup_files method(<- backup rotation process)"
        print(stdout)
        # バックアップファイル一覧の取得してタイムスタンプ順にsort
        file_pattern = f"*.{self.backup_archive_extention}"

        # あまりきれいじゃないけど、pj/settings_package_man/*.pyは、個別にfile_patternを作る必要がある。
        if (self.backup_target == "raw_josn_settings_hostlist") or (self.backup_target == "raw_josn_settings_ansible"):
            file_pattern = f"{self.backup_fname_pattern}*.{self.backup_archive_extention}"

        backup_files = list(self.dir.glob(file_pattern))
        backup_files.sort()

        # rotationの必要がなければスキップ
        num_backup_files = len(backup_files)
        if num_backup_files <= self.saved_generation_num:
            stdout = f"num_backup_files={num_backup_files}, max_backup_files={self.saved_generation_num} --> backup rotation process skipped"
            print(stdout)
            print()
            return 

        # 削除バックアップファイルの抽出
        delete_file_num = num_backup_files - self.saved_generation_num
        delete_files = backup_files[:delete_file_num]
            
        for df in delete_files:
            delete_target_file = str(df)
            os.remove(delete_target_file)

            stdout = f"backup file rotation: {delete_target_file} removed"
            print(stdout)
        print()

    def _get_filepath_patterns_tpl(self):
        if self.backup_target == "raw_text_host_os_list":
            fdir = HOSTS_OUTPUT_DIR
            fname_pattern = "*.txt"
            backup_fname_pattern = "host_os_list"
        elif self.backup_target == "raw_text_host_packages_list":
            fdir = PACKAGES_OUTPUT_DIR
            fname_pattern = "*.json"
            backup_fname_pattern = "host_packages_list"
        elif self.backup_target == "joined_parquet_host_os_packages_list":
            fdir = DATA_DIR
            fname_pattern = "package_list_data.parquet"
            backup_fname_pattern = "package_list_data"
        elif self.backup_target == "raw_josn_settings_hostlist":
            fdir = SETTINGS_DIR
            fname_pattern = "hostlist.py"
            backup_fname_pattern = "hostlist"
        elif self.backup_target == "raw_josn_settings_ansible":
            fdir = SETTINGS_DIR
            fname_pattern = "settings_ansible.py"
            backup_fname_pattern = "settings_ansible"
        elif self.backup_target == "playbook":
            fdir = PLAYBOOK_DIR
            fname_pattern = "*.yml"
            backup_fname_pattern = "playbooks_and_inventory"

        return fdir, fname_pattern, backup_fname_pattern        


# /settings_package_man/hostlist.pyと、
# /setteing_package_man/settings_ansibleを
# 読み込んで、
# /playbook配下に、以下のplaybookを自動作成するメソッドが利用できる
# inventory: MakePlaybook.make_inventory()
# get_os_version: MakePlaybook.make_get_os_version_playbook()
# get_packages: MakePlaybook.make_get_packages_playbook()
class MakePlaybook():
    def __init__(self):
        # ./settings_package_man/hostlis.pyからhost情報を読み込んでdataframeにセット
        self.df = self._set_hostlist_df()
        
        # playbookが収集してきたデータの出力先フォルダが無ければ、作成
        self._mkdir_playbook_outputdir()
    
    # self.dfをfilterする。
    # **kwargsで指定できるkey(列名)は、self.dfのindexである"ssh_ip_address"とself.df.columnsの各要素
    # self.df.columnsの各要素は、hostlist.pyでhostを登録する際にセットしたtag(key-value)により、変動する。
    # 例
    # instance.filter_hosts(ssh_ip_address="192.168.0.100", package_manager="apt")
    # self.dfのindexであるssh_ip_addressでfilterすると、1台のホストのみにfilterされる。
    def filter_hosts(self, **kwargs):
        filter_keys = kwargs.keys()

        # filterが設定されていない場合は、何もせずreturnする
        if len(filter_keys)==0:
            # return
            print("no filter data")

        # validation & filter
        correct_keys = ["ssh_ip_address"] + self.df.columns.tolist()
        for k in filter_keys:
            # 正しいfilterが設定されてなければexit
            if not k in correct_keys:
                stdout = f'Exception: incorrect key "{k}" was set to filter --> exit process'
                sys.exit(stdout)

            fv = kwargs[k]
            if k == "ssh_ip_address":
                self.df = self.df.loc[fv:fv, :]
            else:
                self.df = self.df[self.df[k]==fv]

        # validation2 -> レコード数が0になってしまった場合は、例外を発生させる。
        if self.df.shape[0] == 0:
                stdout = f'Exception: No upgrade target host!! --> exit process'
                sys.exit(stdout)

    # self.dfをfilterして指定したpackageをupgradeするためのinventoryファイルとplaybookを出力する。
    # **kwargsで指定できるkey(列名)は、self.dfのindexである"ssh_ip_address"とself.df.columnsの各要素
    # self.df.columnsの各要素は、hostlist.pyでhostを登録する際にセットしたtag(key-value)により、変動する。
    # 例
    # instance.make_package_upgrade_playbook(ssh_ip_address="192.168.0.100", package_manager="apt")
    # self.dfのindexであるssh_ip_addressでfilterすると、1台のホストのみにfilterされる。
    def make_upgrade_package_inventory_and_playbook(self, package, post_upgrade_task="", service_name="", **kwargs):
        stdout = "Call MakePlaybook.make_get_packages_playbook method"
        print(stdout)

        # **kwargsでupgrade対象のhostをfilterする。
        self.filter_hosts(**kwargs)

        playbook = []

        for ssh_ip_address in self.df.index:
            hostname = self.df.loc[ssh_ip_address, "name"]
            manager = self.df.loc[ssh_ip_address, "package_manager"]
            play = self._make_package_upgrade_play(ssh_ip_address, hostname, manager, package, post_upgrade_task, service_name)
            playbook.append(play)
        
        # 保存dirがなければ作成
        os.makedirs(UPGRADE_PACKAGE_PLAYBOOK_DIR, exist_ok=True)

        # filter済のself.dfから作成されたplaybookファイルをUPGRADE_PACKAGE_PLAYBOOK_DIRに保存
        output = yaml.dump(playbook, sort_keys=False)
        fpath = str(UPGRADE_PACKAGE_PLAYBOOK_DIR/UPGRADE_PACKAGE_PLAYBOOK_FNAME)
        with open(str(fpath), "w") as f:
            f.write(output)
        stdout = f"Playbook {fpath} was made"
        print(stdout)

        # filter済のself.dfからinventoryファイルを作成して、UPGRADE_PACKAGE_PLAYBOOK_DIRに保存
        fPath = UPGRADE_PACKAGE_PLAYBOOK_DIR / INVENTORY_FNAME
        self.make_inventory(fPath)

    def _make_package_upgrade_play(self, ssh_ip_address, hostname, manager, package, post_upgrade_task, service_name):
        play = {}
        
        # nameの生成
        hostname = self._get_hostname(ssh_ip_address)
        name_val = f'Upgrade {hostname}\'s {package} package to latest play'
        play["name"] = name_val
        
        # hostsの生成
        play["hosts"] = hostname

        # become root
        play["become"] = "yes"
        
        # tasksの生成
        play["tasks"] = self._make_tasks_for_package_upgrade_play(hostname, manager, package, post_upgrade_task, service_name)

        # post_upgrade_taskが指定されていた場合は、handlersをセット。
        if post_upgrade_task == "reloaded" or post_upgrade_task == "restarted":
            handlers_name = f'{post_upgrade_task} {service_name}'
            handlers_service_name = service_name
            handlers_service_state = post_upgrade_task 
            play["handlers"] = self._make_handlers_for_package_upgrade_play(handlers_name, handlers_service_name, handlers_service_state)
        elif post_upgrade_task == "reboot":
            handlers_name = f'REBOOT {hostname}'
            play["handlers"] = self._make_handlers_for_package_upgrade_play(handlers_name)
        elif post_upgrade_task == "":
            pass
        else:
            stdout = f'WARNING!!!: {hostname} --> unknown post_upgrade_task "{post_upgrade_task}" --> ignored\n'
            print(stdout)
        
        return play

    def _make_tasks_for_package_upgrade_play(self, hostname, manager, package, post_upgrade_task="", service_name=""):
        tasks = []
        
        # repositories cach updateタスク
        dct = {}
        dct["name"] = f'Update host {hostname}\'s {manager} repositories cache task'
        dct[manager] = {
            "update_cache": "yes",
            "cache_valid_time": 3600,
        }
        tasks.append(dct)
        
        # package更新タスク
        dct = {}
        dct["name"] = f'Upgrade {hostname}\'s {package} package to latest task'
        dct[f'{manager}'] = {
            "name": package,
            "state": "latest"
        }
        # post_upgrade_taskが正しく指定されていた場合は、notifyをセット。
        if post_upgrade_task == "reloaded" or post_upgrade_task == "restarted":
            dct["notify"] = f'{post_upgrade_task} {service_name}'
            
        elif post_upgrade_task == "reboot":
            dct["notify"] = f'REBOOT {hostname}'

        tasks.append(dct)
        
        return tasks

    def _make_handlers_for_package_upgrade_play(self, handlers_name, handlers_service_name="", handlers_service_state=""):
        handlers = []
        handler = {}
        handler["name"] = handlers_name

        # rebootが必要な場合
        pattern = r"^REBOOT"
        if re.search(pattern, handlers_name):
            handler["reboot"] = {
                "pre_reboot_delay": 10,  # 再起動コマンドを発行する前に待機する秒数
                "post_reboot_delay": 30,  # 再起動後に待機する秒数
                "test_command": "uptime",  # システムが正常に起動したことを確認するためのコマンド
                "reboot_timeout": 300  # 再起動を待つ最大秒数
            }
        
        # その他(reloadedまたはrestarted)の場合
        # このメソッドの親メソッドで場合分けしているので、rebootでなければreloadedかrestartedしかありえない
        else:        
            handler["service"] = {
                "name": handlers_service_name,
                "state": handlers_service_state
            }

        handlers.append(handler)

        return handlers


    
    def make_get_packages_playbook(self):
        stdout = "Call MakePlaybook.make_get_packages_playbook method"
        print(stdout)

        playbook = []

        # inventory fileでは、package managerごとにhostグループを作成しているので、
        # package managerごとにOS情報を取得するplayを作成
        host_groups = self.df["package_manager"].drop_duplicates().tolist()
        for hg in host_groups:
            # OS情報収集結果を出力するためのフォルダを作成するplayを作成してplaybookに追加
            # playbook.append(self._make_get_os_version_plays(hg))
            playbook += self._make_get_package_plays(hg)

        output = yaml.dump(playbook, sort_keys=False)
        output = output.replace("'\"", '"').replace("''", "'").replace("''", "'").replace("\"'", '"').replace("]\n", "]").replace("]        }}", "] }}")

        fpath = PLAYBOOK_DIR / GET_PACKAGES_PLAYBOOK_FNAME
        with open(str(fpath), "w") as f:
            f.write(output)
        
        stdout = f"Playbook {str(fpath)} was made"
        print(stdout)
        print()

    def _make_get_package_plays(self, package_manager):
        # dfをhgでfilter
        pdf = self.df[self.df["package_manager"]==package_manager]

        # playはhostごとに作成する
        ssh_ip_addresses = pdf.index
        package_plays = []
        for ip in ssh_ip_addresses:
            package_plays.append(self._make_get_packages_play(ip))
        
        return package_plays
    
    def _make_get_packages_play(self, ssh_ip_address):
        dct = {}

        # nameの生成
        hostname = self._get_hostname(ssh_ip_address)
        name_val = hostname + " get packages"
        dct["name"] = name_val

        # hostsの生成
        dct["hosts"] = hostname

        # tasksの生成
        manager = self.df.loc[ssh_ip_address, "package_manager"]
        dct["tasks"] = self._make_tasks_for_get_packages_play(hostname, manager)

        return dct

    def _make_tasks_for_get_packages_play(self, hostname, manager):
        tasks = []
    
        # packageリストの収集タスク
        dct = {}
        dct["name"] = hostname + ": Gather package facts"
        dct["package_facts"] = {"manager": manager}
        tasks.append(dct)

        # 収集したpackageリストをローカルホストに保存するタスク
        dct = {}
        dct["name"] = hostname + ": Save package facts to file"

        copy_dct = {}
        copy_dct["content"] =  "\"{{ ansible_facts.packages | to_nice_json }}\""
        copy_dct["dest"] = str(PACKAGES_OUTPUT_DIR / hostname) + ".json"

        dct["copy"] = copy_dct
        dct["delegate_to"] = "localhost"

        tasks.append(dct)

        return tasks



    def _make_initial_play_for_get_packages_playbook(self):
        # local_actionモジュール
        local_action_dct = {}
        local_action_dct["module"] = "file"
        local_action_dct["path"] = "./output/packages"
        local_action_dct["state"] = "directory"
        local_action_dct["mode"] = "0755"

        # tasks
        tasks_dct = {}
        tasks_dct["name"] = "create output dir for host package list if not exist"
        tasks_dct["local_action"] = local_action_dct

        tasks = [tasks_dct]

        # play
        play_dct = {}
        play_dct["name"] = "create output dir for host package list if not exist"
        play_dct["hosts"] = "localhost"
        play_dct["gather_facts"] = "no"
        play_dct["tasks"] = tasks

        return play_dct

    def make_get_os_version_playbook(self):
        stdout = "Call MakePlaybook. make_get_os_version_playbook method"
        print(stdout)

        playbook = []

        # 出力先フォルダが無い場合は作成する
        # 不要になったので、コメントアウト
        # playbook.append(self._make_initial_play_for_get_os_version_playbook())

        # inventory fileでは、package managerごとにhostグループを作成しているので、
        # package managerごとにOS情報を取得するplayを作成
        hosts = self.df["package_manager"].drop_duplicates().tolist()
        for hg in hosts:
            # OS情報収集結果を出力するためのフォルダを作成するplayを作成してplaybookに追加
            # playbook.append(self._make_get_os_version_plays(hg))
            playbook += self._make_get_os_version_plays(hg)

        output = yaml.dump(playbook, sort_keys=False)
        output = output.replace("'\"", '"').replace("''", "'").replace("''", "'").replace("\"'", '"').replace("]\n", "]").replace("]        }}", "] }}")

        fpath = PLAYBOOK_DIR / GET_OS_VERSION_PLAYBOOK_FNAME
        with open(str(fpath), "w") as f:
            f.write(output)
        
        stdout = f"Playbook {str(fpath)} was made"
        print(stdout)
        print()

    def _make_get_os_version_plays(self, package_manager):
        # dfをhgでfilter
        pdf = self.df[self.df["package_manager"]==package_manager]

        # playはhostごとに作成する
        ssh_ip_addresses = pdf.index
        os_version_plays = []
        for ip in ssh_ip_addresses:
            os_version_plays.append(self._make_get_os_version_play(ip))

        return os_version_plays

    def _make_get_os_version_play(self, ssh_ip_address):
        dct = {}

        # nameの生成
        hostname = self._get_hostname(ssh_ip_address)
        name_val = hostname + " get os version"
        dct["name"] = name_val

        # hostsの生成
        dct["hosts"] = hostname

        # tasksの生成
        dct["tasks"] = self._make_tasks_for_get_os_version_play(hostname)

        return dct

    def _make_tasks_for_get_os_version_play(self, hostname):
        tasks = []
    
        dct = {}
        dct["name"] = hostname + ": Save host OS facts to file"

        copy_dct = {}
        copy_dct["content"] =  "\"{{ ansible_facts['distribution'] }},{{ ansible_facts['distribution_version'] }}\""
        copy_dct["dest"] = str(HOSTS_OUTPUT_DIR / hostname) + ".txt"

        dct["copy"] = copy_dct
        dct["delegate_to"] = "localhost"

        tasks.append(dct)

        return tasks

    def _make_initial_play_for_get_os_version_playbook(self):
        # local_actionモジュール
        local_action_dct = {}
        local_action_dct["module"] = "file"
        local_action_dct["path"] = "./output/hosts"
        local_action_dct["state"] = "directory"
        local_action_dct["mode"] = "0755"

        # tasks
        tasks_dct = {}
        tasks_dct["name"] = "create output dir for host os version list if not exist"
        tasks_dct["local_action"] = local_action_dct

        tasks = [tasks_dct]

        # play
        play_dct = {}
        play_dct["name"] = "create output dir for host os version list if not exist"
        play_dct["hosts"] = "localhost"
        play_dct["gather_facts"] = "no"
        play_dct["tasks"] = tasks

        return play_dct
    
    def make_inventory(self, Path_inventory_file=(PLAYBOOK_DIR/INVENTORY_FNAME)):
        stdout = "Call MakePlaybook.make_inventory method"
        print(stdout)

        # package_managerごとにhostgroupを作成する
        host_groups = self._get_hostgroups()
        hg_dct = {}
        for hg in host_groups:
            hosts_dct = {}
            hosts_dct["hosts"] = self._make_hosts_dct(hg)
            hg_dct[hg] = hosts_dct

        output = yaml.dump(hg_dct)

        # yaml.dumpのコーテーションの扱いが悪く、正しく出力されないので、バグ修正
        # "'''"を修正するために、"''"を2回"'"にreplaceしている。
        output = output.replace("'\"", '"').replace("''", "'").replace("''", "'").replace("\"'", '"').replace(")\n       ", ")")

        # インベントリファイルの出力
        fpath = str(Path_inventory_file)
        with open(fpath, "w") as f:
            f.write(output)
        
        stdout = f"Inventory file {str(fpath)} was made"
        print(stdout)
        print()
                
    def _make_hosts_dct(self, hg):
        # hostgroup(hg)のhostのindex(ssh_ip_address)を取得
        df = self.df
        hg_hosts_df = df[df["package_manager"]==hg]
        hg_hosts = hg_hosts_df.index
        
        # hostgroup(hg)のhostごとのinventoryのdctを生成
        h_dct = {}
        for ssh_ip in hg_hosts:
            name = self._get_hostname(ssh_ip)
            h_s = hg_hosts_df.loc[ssh_ip, :]
            h_dct[name] = self._make_host_dct(ssh_ip, h_s)
        
        return h_dct
    
    def _get_hostname(self, ssh_ip_address):
        if HOSTNAME_WITH_IP:
            return self.df.loc[ssh_ip_address, "name"] + "_" + ssh_ip_address
        else: 
            return self.df.loc[ssh_ip_address, "name"]

    
    def _make_host_dct(self, ssh_ip, h_s):
        dct = {}
        dct = self._make_hostvars_dct(ssh_ip, h_s)

        return dct
    
    def _make_hostvars_dct(self, ssh_ip, h_s):
        dct = {}
        dct["ansible_host"] = ssh_ip
        
        ssh_auth_method = h_s["ssh_auth_method"]
        envvar_pattern = r"^\$[A-Z].+"
        
        # 対象managedホストへのsshログインがpassword認証の場合
        if ssh_auth_method == "password":
            # ssh_userのセット
            ssh_user = h_s["ssh_user"]
            # ssh_userが環境変数にセットされている場合
            if re.match(envvar_pattern, ssh_user):
                ansible_user = "\"{{ lookup('env', '" + f"{ssh_user[1:]}" + "') }}\""
            # ssh_userがliteralでセットされている場合
            else:
                ansible_user = ssh_user
            dct["ansible_user"] = ansible_user
            
            # ssh_passwordのセット
            ssh_password = h_s["ssh_password"]
            # ssh_passwordが環境変数にセットされている場合
            if re.match(envvar_pattern, ssh_password):
                ansible_ssh_pass = "\"{{ lookup('env', '" + f"{ssh_password[1:]}" + "') }}\""
            # ssh_userがliteralでセットされている場合
            else:
                ansible_ssh_pass = ssh_password
            dct["ansible_ssh_pass"] = ansible_ssh_pass

        # 対象managedホストへのsshログインがpassword認証の場合
        elif ssh_auth_method == "keypair":
            # private key fileのパスをセット
            ssh_secretkey_path = h_s["ssh_secretkey_path"]
            # ssh_userが環境変数にセットされている場合
            if re.match(envvar_pattern, ssh_secretkey_path):
                ansible_ssh_private_key_file = "\"{{ lookup('env', '" + f"{ssh_secretkey_path[1:]}" + "') }}\""
            # ssh_userがliteralでセットされている場合
            else:
                ansible_ssh_private_key_file = ssh_secretkey_path
            dct["ansible_ssh_private_key_file"] = ansible_ssh_private_key_file
            
        # SSHホストキー(SSH接続先ホストfinger print)のチェックを無効化
        # fingerprintをチェックしたい場合は不要。
        # finger printをチェックしたい場合は、一度接続先にSSHアクセスをしてansilble managedホストのfingerpirintを記録しておく必要がある
        dct["ansible_ssh_extra_args"] = "'-o StrictHostKeyChecking=no'"
        
        # 収集したfactsの出力先ファイルのパスをroot=./playbookからの相対パスで指定
        # 不要になったのでコメントアウト
        # dct["host_os_output_dir"] = "./output/host_os/"
        # dct["host_packages_output_dir"] = "./output/host_packages/"

        return dct
    
    def _get_hostgroups(self):
        return self.df["package_manager"].drop_duplicates().tolist()
    
    def _set_hostlist_df(self):
        dct = MANAGED_HOSTS_DCT

        # ホストkey(dataframe indexのセット)
        ssh_ip_addresses = dct.keys()
        tbl = []
        for ip in ssh_ip_addresses:
            tbl.append([ip])
        df = pd.DataFrame(data=tbl, columns=["ssh_ip_address"])
        df.set_index("ssh_ip_address", inplace=True, drop=True)
        
        # set host properties
        for ip in ssh_ip_addresses:
            # set ssh properties
            ssh_keys = dct[ip]["ssh"].keys()
            for sk in ssh_keys:
                df.loc[ip, sk] = dct[ip]["ssh"][sk]
        
            # set other properties
            host_dct_keys = list(dct[ip].keys())
            host_dct_keys.remove("ssh")
            for k in host_dct_keys:
                df.loc[ip, k] = dct[ip][k]
        
        return df
    
    def _mkdir_playbook_outputdir(self):
            Ds = [HOSTS_OUTPUT_DIR, PACKAGES_OUTPUT_DIR]
            
            for D in Ds:
                d = str(D)

                if not os.path.exists(d):
                    os.makedirs(d)

class CreatePackagelistParquet():
    def __init__(self):
        self.os_df_cols = [
            "ssh_ip_address",   # index
            "os",
            "os_version",
        ]
        self.hostlist_df = MakePlaybook().df

    # /playbook/output/hostsと/playbook/output/packagesから、ansibleが収集してきた
    # factsの出力ファイルを読み込んで、dataframeにセットして、pqrquet形式でファイルに保存
    def collect_data(self):
        stdout = "Call CreatePackagelistParquet.collect_data method"
        print(stdout)
        print()

        # host os情報の収集
        os_df = self._read_os_df()

        # package情報の収集
        packages_df = self._read_packages_df()

        # packages_dfとos_dfを連結
        self.df = pd.merge(os_df, packages_df, on="ssh_ip_address", how="right")
        
        # parquet形式でstr(DATA_DIR/PACKAGE_DATA_FNAME)にデータを保存
        self._save_data()

        print()
    
    def _save_data(self):
        self._mkdir_data_output_dir_if_not_exists()
        parquet_tbl = pa.Table.from_pandas(self.df)
        fp = DATA_DIR / PACKAGE_DATA_FNAME
        sfp = str(fp)
        stdout = f"Saving host package list data: {sfp}"
        print(stdout)

        with open(sfp, "wb") as f:
            pq.write_table(parquet_tbl, f)
    
    def _mkdir_data_output_dir_if_not_exists(self):
        D = PJROOT_DIR / "data_package_man"
        d = str(D)

        if not os.path.exists(d):
            os.makedirs(d)
        

    def _read_packages_df(self):
        # dataframeの初期化
        df = pd.DataFrame()
        
        # file一覧の取得
        files = PACKAGES_OUTPUT_DIR.glob("*.json")
        
        for fp in files:
            sfp = str(fp)
            stdout = f"Reading host packages: {sfp}"
            print(stdout)

            with open(sfp, "r") as jsonf:
                dct = json.load(jsonf)
            
            file_name = sfp.split("/")[-1]
            splited_fname_parts = file_name.split("_")
            ip = splited_fname_parts[-1].replace(".json", "")
            packages = list(dct.keys())

            hostname_parts = splited_fname_parts[:-1]
            hostname = "_".join(hostname_parts)

            for p in packages:
                # p_properies = self._get_package_properties(dct, p)
                p_properties = dct[p]

                i = 0 
                rec_dct ={}
                for p_prop in p_properties:
                    rec_dct["ssh_ip_address"] = [ip]
                    rec_dct["hostname"] = hostname
                    rec_dct["pkg_id"] = [i]

                    for k in p_prop.keys():
                        rec_dct[k] = [p_prop[k]]
    
                    rec_df = pd.DataFrame(rec_dct)
                    df = pd.concat([df, rec_df], ignore_index=True)
                    i += 1

        stdout = ""
        print(stdout)
        return df
                
    def _read_os_df(self):
        # file一覧の取得
        files = list(HOSTS_OUTPUT_DIR.glob("*.txt"))
        data = []
        for fp in files:
            sfp = str(fp)
            stdout = f"Reading host os list: {sfp}"
            print(stdout)

            with open(sfp, "r", newline="") as csvf:
                csvd = list(csv.reader(csvf))

            ip = sfp.split("_")[-1].replace(".txt", "")
            rec = [ip] + csvd[0]
            data.append(rec)

        os_df = pd.DataFrame(data=data, columns=self.os_df_cols)
        # os_df.set_index("ssh_ip_address", inplace=True, drop=True)

        stdout = ""
        print(stdout)
        return os_df

###########################
##
## workflow1
##
###########################    
# DAG1-Task4
# pj/settings_package_man/hostlist.pyのバックアップ(変更があったとき、またはbackupファイルが存在しないときのみ)
def backup_settings_package_man_files():
    _backup_settings_package_man_files("raw_josn_settings_ansible")
    _backup_settings_package_man_files("raw_josn_settings_hostlist")
# backup_target = <"raw_josn_settings_hostlist"|"raw_josn_settings_ansible">
def _backup_settings_package_man_files(backup_target):
    if backup_target == "raw_josn_settings_ansible":
        subprocess_num = 1
    elif backup_target == "raw_josn_settings_hostlist":
        subprocess_num = 2
    stdout = f"start workflow1-DAG4-{subprocess_num}: backup_settings_package_man_files({backup_target})"
    print(stdout)

    ins_PMB = PackageManBackup(backup_target)
    stdout  = f"function backup_settings_package_man_files({backup_target}) called\n"
    stdout += f"Settings File {ins_PMB.fname_pattern}'s backup archive will be created if changed"
    print(stdout)
    print()

    # backup archiveがない場合はtempbakを作成して
    # tempbakからbackup archiveを作成する
    if not ins_PMB.is_backup_archive():
        ins_PMB.create_temporaly_backup_files()
        ins_PMB.create_backup_archive_file()
    # backup archiveが存在する場合は、originalの変更有無チェックのために
    # 最新のbackup archiveからbackupを解凍する
    else:
        ins_PMB.extract_last_backup_files()

    # 比較のためにbackup archiveからextractしたtempファイルを削除して、
    # originalファイルから改めてtempファイルを作成し、
    # tempファイルからbackup archiveを作成する
    if ins_PMB.check_if_backup_required():
        ins_PMB.delete_temporaly_backup_files()
        ins_PMB.create_temporaly_backup_files()
        ins_PMB.create_backup_archive_file()   

    # temp_bakファイルを削除
    ins_PMB.delete_temporaly_backup_files()

    # バックアップファイルのローテーション
    ins_PMB.delete_old_bakup_files()

# DAG1-Task3
# 収集データから、検索、処理がしやすいparquetファイルを生成
# pj/data_package_man/*/<*.txt|*.json>から自動生成でき、こちらでbackupもとっていることから、parquetのバックアップは作成しない。
def update_parquet_data():
    stdout = f"start workflow1-DAG3: update_parquet_data"
    print(stdout)

    ins_CPP = CreatePackagelistParquet()
    ins_CPP.collect_data()

# DAG1-Task2
# playbookを使って、データを収集し、変更がある場合はbackupを作成する
# また、backupファイル数が多くなったらローテーションする
def collect_and_update_data():
    _collect_and_update_data("os_version")
    _collect_and_update_data("packages")
# target_data = <"os_version"|"packages">
def _collect_and_update_data(target_data):
    if target_data == "os_version":
        subprocess_num = 1
    elif target_data == "packages":
        subprocess_num = 2
    stdout = f"start workflow1-DAG2-{subprocess_num}: update_playbook({target_data})"
    print(stdout)

    #  PackageManBackupインスタンスの生成
    if target_data == "os_version":
        backup_target = "raw_text_host_os_list"
    elif target_data == "packages":
        backup_target = "raw_text_host_packages_list"
    ins_PMB = PackageManBackup(backup_target)

    # playbookをtemporary backupとしてfile名を変更(mv)
    ins_PMB.move_to_temporaly_backup_files()

    # playbookを実行して、dataを取得
    ins_PE = PlaybookExecutor()
    ins_PE.execute_collecting_data_playbook(target_data)

    # backupが必要な場合(playbookに変更がある場合)は、temporary backup fileからplaybookのバックアップを作成
    if ins_PMB.check_if_backup_required():
        ins_PMB.create_backup_archive_file()

    # temporary backupの削除
    ins_PMB.delete_temporaly_backup_files()

    # backupローテーション。backup generationより古いbackup fileを削除
    ins_PMB.delete_old_bakup_files()

# DAG1-task1
# pj/settings_package_man/hostlist.pyから、inventoryとplaybookを更新する
def update_playbook():
    #  PackageManBackupインスタンスの生成
    stdout = "start workflow1-DAG1: update_playbook"
    print(stdout)

    backup_target = "playbook"
    ins_PMB = PackageManBackup(backup_target)

    # playbookをtemporary backupとしてfile名を変更(mv)
    ins_PMB.move_to_temporaly_backup_files()

    # MakePlaybookインスタンスの生成
    ins_MP = MakePlaybook()

    # playbookの作成
    ins_MP.make_inventory()
    ins_MP.make_get_os_version_playbook()
    ins_MP.make_get_packages_playbook()

    # backupが必要な場合(playbookに変更がある場合)は、temporary backup fileからplaybookのバックアップを作成
    if ins_PMB.check_if_backup_required():
        ins_PMB.create_backup_archive_file()

    # temporary backupの削除
    ins_PMB.delete_temporaly_backup_files()

    # backupローテーション。backup generationより古いbackup fileを削除
    ins_PMB.delete_old_bakup_files() 

### workfow1のDAGで指定するtasks
### ホストごとのinstall済packageリストの収集workflow
### for debug用
def workflow1_collect_host_package_list():
    # Dag1
    update_playbook()

    # DAG2
    collect_and_update_data()

    # DAG3
    update_parquet_data()

    # DAG4
    backup_settings_package_man_files()





    
    
