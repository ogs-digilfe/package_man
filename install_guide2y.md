[１．環境構築](#１．環境構築)

# はじめに
このシステムは、現時点では、ubuntu22.04で動作することが前提となっている。
# １．linux install時に実施すること
## 1.1 loginユーザをsudowersに追記
\$ sudo visudo  
/etc/sudoers  
が開くので、最終行に、以下を追記。  
\<username\>は、loginユーザ名に置き換える。

\---------------  
\<username\> ALL=NOPASSWD: ALL  
\---------------

## 1.2 packageの最新化
以下は、debian系linuxの場合。  
\$ sudo apt update  
\$ sudo apt upgrade


# ２．アプリケーションのインストール
## 2.1. パッケージのインストール
installに必要なosパッケージをinstallしておく。  
以下は、ubuntu22.04にデフォルトで入ってなくて、installに必要なパッケージ。
pythonのsubprocessコマンドでは、aptの動きが不安定。

\$ sudo apt install make python3-venv python3-pip

## 2.2. コンテンツのgit clone
アプリケーションコンテンツは、すべてプロジェクトディレクトリ配下に作成されている。  
git cloneする際、プロジェクトディレクトリごとダウンロードされるため、  
まずはプロジェクトディレクトリをダウンロードするディレクトリに移動し、git cloneコマンドを実行する。  
git cloneコマンドにおいて、リモートリポジトリの後ろにディレクトリ名を指定すると、プロジェクトディレクトリ名を自身の好みのディレクトリ名に変更することができる。  

\$ cd /path/to/project_folders  
\$ git clone  git clone https://github.com/ogs-digilfe/package_man [\<your favorit dir name\>]  



### 1.1.2 SSH鍵ペアの作成(オプション)とmanaged hostへのコピー(オプション)
管理台数が多い場合は、ansible contorolホスト専用のカギペアを作成しておくと便利。  
managedホストへの最初のansibleのsshアクセスはpassword認証でのアクセスとなるが、  
contorolホストの公開鍵を管理対象のmanagedホストにコピーしておくと、  
2回目以降のplaybookの実行は、秘密鍵ファイルのパスを指定するだけでよくなるため。

公開鍵ファイルのmanagedホストへのコピーは、playbookで自動化可能。

## 1.2. apache airflowをpipでインストール
apache airflowは、packageのconstraintが非常に厳しいため、仮想環境からpipコマンドを使ってapache airflowをインストールする。  
以下は、apache airflow 2.7.3のinstall。

step1: pjディレクトリからsourceコマンドで以下のファイルを読み込んで実行し、作成した仮想環境に入る  
$ source ./<venv_name>/bin/activate

step2: apache airflowのインストール  
$ pip install "apache-airflow[celery]==2.7.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-3.8.txt"

## 1.3. 他に必要なpipのinstall
./reqirements.txtに他に必要なpythonの外部パッケージを記載。

./で以下のコマンドを実行し、requirements.txtに記載された必要なpython外部パッケージをインストールする。

\$ pip install -r ./requirements.txt

## 1.4. apache airflowの初期化(git clone時は不要??)
git cloneした場合は不要？？

apache airflowのルートディレクトリ./airflowで、airflowコマンドを使ってapache airflowを初期化する。

\$ cd ./airflow  
\$ airflow db migrate

## 1.5. apache airflowが参照する環境変数AIRFLOW_HOMEのセット
apache airflowは、どこがapache airflowのルートディレクトリかを参照する際、環境変数AIRFLOW_HOMEを参照するようになっているため、exportコマンドで環境変数AIRFLOW_HOMEをセット。  
__"./"は正しいpjディレクトリのフルパスに書き換えること。__

\$ export AIRFLOW_HOME=./airflow

次回以降、環境変数AIRFLOW_HOMEがシステム起動時などに自動セットされるよう、適切なファイルに環境変数AIRFLOW_HOMEの設定を追記。  
ubuntuの場合は、/etc/environmentに追記。  
__"/path/to/project/は正しいpjディレクトリのフルパスに書き換えること。__

--------------- /etc/environment ---------------  
\#  ファイルの末尾に以下を追記  
AIRFLOW_HOME=/path/to/project/airflow  
\-------------------------------------------

## 1.6. timezoneの設定
git cloneした場合は不要

上記でairflow db migrateコマンドを実行すると、apache airflowのコンフィグファイル
が自動生成される。  
apache airflowを設定した状態だと、timezoneがutcのままになっているので、  
./airflow/airflow.cfg  
で、  
　default_timezone = utc  
を、  
　default_timezone = Asia/Tokyo  
に変更する。

## 1.7. 初期ユーザ登録
apache airflowはwebの管理コンソールがセットされている。  
管理コンソールにログインするための初期ユーザを設定。
設定値は、適宜書き換える。

\$ airflow users create \\  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--username airflow_user \\  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--firstname  your_firstname\\  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--lastname your_lastname \\  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--role Admin \\  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--email your_mailaccount@example.org

## 1.8. ansibleのssh接続にパスワード認証を使うためのlinux packageのinstall
sshpassパッケージをinstallする。  
\$ sudo apt update  
\$ sudo apt install sshpass

# ２．airflow schedulerとairflow webserverの起動
## 2.1. airflow daemonの起動
apache airflowは、2つのprocessが起動してサービスを提供する。  
schedulerとwebsrver。
schedulerは、workflowで定義したscheduleに従ってworkflowを実行する。  
webserverは、workflow実行結果のログを見たり、個々のworkflowを管理するための管理コンソールして利用する。  

スケジューラの起動  
backgroundで起動したい場合はnohupコマンドから起動。
\$ nohup airflow scheduler > /dev/null 2>&1 &  

webserverの起動。  
-pオプションは適切な公開port番号を指定。  
デフォルトで、外部からのhttpリクエストも受け付ける。  
\$ nohup airflow webserver -p 8080 > /dev/null 2>&1 &  

スケジューラとwebserverが起動しているか確認。  
\$ ps -ax|grep airflow

## 2.2. ログイン
webserverを起動したら、  
http://<ip_address>:<公開port番号>  
で起動。
登録したユーザでログイン。

# ３．gitリポジトリの初期化とコンテンツのダウンロード
./で  
\$ git clone http://git_repository.com/project

※)同期されるコンテンツディレクトリは以下の自作コードのディレクトリのみ。
DAGが保存されている  
./dag/

DAGで使用するpythonの自作ライブラリが保存されている  
./pacmng_lib/

managedノードからpackagelistを収集するためのansible playbookが保存されている  
./playbook/

# ３．ssh認証の初期化
## 3.1. ssh認証の前提
ansibleのmanaged hostは、ホスト構築時のsshユーザ,SSHパスワードが共通のもので構築されていることを前提とする。  
なお、初期設定後は、ssh公開鍵認証でmanaged hostにアクセスする。

また、contorolホストはすでにsshの鍵ペアを作成済であるものとする。

## 3.2. managed hostのssh初期id, 初期passwordを環境変数にセットする
この初期idと初期password、managedホスト初期設定後のssh秘密鍵のファイルパス環境変数にセット。  
/etc/environmentの最終行に、以下の3行を追記する。  
適宜実際のssh初期id, 初期password, 秘密鍵のファイルパスに書き換えること。  

補足：  
controlホストとmanagedホストのSSH認証は、原則、公開鍵認証を行うが、そのためには、managedホストにcontrolホストの公開鍵を登録する必要がある。  
したがって、最初の1回目はpassword認証が通るようにする設定が必要。  
以下の環境変数は、playbookのinventoryファイルから参照される。  

--------------- /etc/environment ---------------  
\#以下を追記  
ANSIBLE_USER="user"  
ANSIBLE_SSH_PASS="password"  
ANSIBLE_SSH_PRIVATE_KEY_FILE="/path/to/private_key"  
\------------------------------

/etc/environmentは、ホスト再起動時にしか読み込まれないので、exportコマンドでもセットしておく  
\$ export ANSIBLE_USER=user  
\$ export ANSIBLE_SSH_PASS=password  
\$ export ANSIBLE_SSH_PRIVATE_KEY_FILE=/path/to/private_key

## 3.3. inventoryファイルの編集
playbookディレクトリに移動して、inventoryファイルを編集する。
今対応しているのは、deian系linuxとredhat系linuxディストリビューション。
debian系はapt_hostsグループに、reahat系はyum_hostsグループに追記・編集のこと

\$ cd ./playbook

--------------- ./playbook/inventory.yml ---------------  
\# ansibleコマンドとansible-playbookコマンドの実行例  
\# ansible all -m ping -i inventory_file   
\# ansible-playbook site.yml -i inventory.yml  
\##############  
\##  
\## ssh認証設定  
\##  
\##############  
all:  
&nbsp;&nbsp;vars:  
&nbsp;&nbsp;&nbsp;&nbsp;# password設定の場合  
&nbsp;&nbsp;&nbsp;&nbsp;\# OSの環境変数ANSIBLE_USERにsshユーザ名、とANSIBLE_SSH_PASSにsshパスワードをセットすること  
&nbsp;&nbsp;&nbsp;&nbsp;ansible_user: "{{ lookup('env', 'ANSIBLE_USER') }}"  
&nbsp;&nbsp;&nbsp;&nbsp;ansible_ssh_pass: "{{ lookup('env', 'ANSIBLE_SSH_PASS') }}"  

&nbsp;&nbsp;&nbsp;&nbsp;\# SSHホストキー(SSH接続先ホストfinger print)のチェックを無効化  
&nbsp;&nbsp;&nbsp;&nbsp;\# fingerprintをチェックしたい場合は不要。  
&nbsp;&nbsp;&nbsp;&nbsp;\# finger printをチェックしたい場合は、一度接続先にSSHアクセスをしてansilble managedホストのfingerpirintを記録しておく必要がある  
&nbsp;&nbsp;&nbsp;&nbsp;ansible_ssh_extra_args: '-o StrictHostKeyChecking=no'
    
&nbsp;&nbsp;&nbsp;&nbsp;\# 公開鍵認証の場合
&nbsp;&nbsp;&nbsp;&nbsp;\# 公開会議認証でmanagedホストにssh接続する場合は、controlホストの公開鍵を全managedホストに登録しておく必要がある。
&nbsp;&nbsp;&nbsp;&nbsp;\# ansible_ssh_private_key_file: "{{ lookup('env', 'ANSIBLE_SSH_PRIVATE_KEY_FILE') }}"

\##############  
\##  
\## hostgroups and hosts  
\##  
\##############  
\# debian系とredhat系でパッケージシステムが異なるため、hostグループで分ける。  
\# debian系はhostグループ apt_hostsに、redhat系はhostグループyum_hostsに加えること。    
apt_hosts:  
&nbsp;&nbsp;hosts:  
&nbsp;&nbsp;&nbsp;&nbsp;debian1:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ansible_host: 100.100.100.100  
&nbsp;&nbsp;&nbsp;&nbsp;debian2:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ansible_host: 100.100.100.101  
&nbsp;&nbsp;&nbsp;&nbsp;debian3:   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ansible_host: 100.100.100.102

yum_hosts:  
&nbsp;&nbsp;hosts:  
&nbsp;&nbsp;&nbsp;&nbsp;redhat1:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ansible_host: 100.100.100.111  
&nbsp;&nbsp;&nbsp;&nbsp;redhat2:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ansible_host: 100.100.100.112  
&nbsp;&nbsp;&nbsp;&nbsp;redhat3:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ansible_host: 100.100.100.113  
\------------------------------------------------------------

## 3.4. managedホストへの接続確認
inventoryファイルの編集が終わったらplaybookディレクトリに移動して、接続確認を実施。
初期状態のinventory.ymlファイルは、password認証でmanagedホストにアクセスする。

\$ cd ./playbook
\$ ansible all -m ping -i inventory.yml

## 3.5. パッケージ

# ４．jupyter labの起動
pjroot/notebooksで、以下のコマンドを実行
$ jupyter-lab --ip='0.0.0.0' --no-browser
バックグラウンドで起動させる場合は、
$ nohup jupyter-lab --ip='0.0.0.0' --no-browser > /dev/null 2>&1 &


