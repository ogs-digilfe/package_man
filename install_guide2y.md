[１．環境構築](#１．環境構築)

# はじめに
このシステムは、現時点では、ubuntu22.04で動作することが前提となっている。
# １．linux install時に実施すること  
まずは、sshでアプリケーションを構築するホスト(以下、airflowホスト)にログインする。
## 1.1 loginユーザをsudowersに追記
airflowホストを操作するユーザをsudoersに追加して特権権限を利用できるようにする。
\$ sudo visudo  
/etc/sudoers  
が開くので、最終行に、以下を追記。  
\<username\>は、loginユーザ名に置き換える。

\---------------  
\<username\> ALL=NOPASSWD: ALL  
\---------------

## 1.2 packageの最新化
os packageを最新化しておく。  
\$ sudo apt update  
\$ sudo apt upgrade

# ２．アプリケーションのインストール
## 2.1. パッケージのインストール
airflowのインストールに必要なosパッケージをinstallしておく。  
以下は、ubuntu22.04にデフォルトで入ってなくて、installに必要なパッケージ。

\$ sudo apt install make python3-venv python3-pip sshpass

## 2.2. コンテンツのgit clone
アプリケーションコンテンツは、プロジェクトフォルダ配下に作成される。  
git cloneする際、プロジェクトフォルダごとダウンロードされるため、  
まずはプロジェクトフォルダをダウンロードするフォルダに移動し、以下のgit cloneコマンドを実行する。  
プロジェクトフォルダの保存場所(gitcloneを実行するフォルダ)は任意。  
git cloneコマンドにおいて、リモートリポジトリの後ろにフォルダ名を指定すると、プロジェクトフォルダ名を自身の好みのディレクトリ名に変更することができる。  
デフォルトのプロジェクトフォルダ名は、"package_man"。

\$ cd /path/to/project_folders  
\$ git clone https://github.com/ogs-digilfe/package_man [\<your favorit dir pj folder name\>]  

以下、プロジェクトフォルダ名をpackage_manとして記述。

## 2.3. アプリケーションのビルド
Makefileを実行する。
pacage_man/install_toolsに移動し、
$ make install

# ３．初期設定
## 3.1. 仮想環境に入る
アプリケーションは、osのpython環境に影響を与えないよう、専用の仮想環境にインストールされている。  
このため、airflowを操作する際は、仮想環境に入って操作する。
仮想環境は、プロジェクトフォルダと同じフォルダに  
venv_package_man 
のフォルダ配下にインストールされている。  
sourceコマンドで  仮想環境のactvateファイルを読み込んで仮想環境に入る   
\$ cd ..  
\$ source venv_package_man/bin/activate  
(venv_package_man)\$  

(参考)
仮想環境から抜ける場合は、  
(venv_package_man)\$ deactivate  
を実行。

## 3.2. 初期ユーザ登録
管理コンソールにログインするための初期ユーザを設定。
設定値は、適宜書き換える。  
(venv_package_man)\$ airflow users create \\  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--username airflow_user \\  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--firstname  your_firstname\\  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--lastname your_lastname \\  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--role Admin \\  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--email your_mailaccount@example.org  

初期パスワード設定のプロンプトが表示されるので、パスワード設定をして初期ユーザ設定は完了。

確認は、  
\$ airflow users list

## 3.2. webサーバの起動
仮想環境から、airflowに付属のwebaplicationを起動して初期ユーザでログインできるか確認する。  
-pオプションでポート番号は自由に設定可能であるが、以下、8080に指定したことを前提に説明。  
(venv_package_man)\$ airflow webserver -p 8080  

バックエンドでwebserverを起動したい場合は、nohupコマンドと出力のリダイレクトを使って、
(venv_package_man)\$ nohup airflow webserver -p 8080  > /dev/null 2>&1 &  

webserverが起動したら、操作端末のブラウザを起動。  
http://\<airflowサーバのipアドレス>:8080  

(例)  
http://192.168.0.136:8080

とりあえず、ログインできたらok。
一旦、airflow webサーバのプロセスを落とす。  

フロントエンドで起動している場合は、  
Ctrl+C  
でプロセスを停止。  

バックエンドで起動している場合は、  
(venv_package_man)\$ ps -ax |grep aiflow  
で、  
"airflow webserver -p 8080"  
の文字列を含むプロセスがメインプロセスなので、メインプロセスのprocessIDを確認。  
killする。

(venv_package_man)\$ sudo kill \<processid>

## 3.3. 対象ホストの設定
パッケージ情報を収集先ホストのホスト情報の設定をする。  

サンプルの設定ファイルが、  
package_man/settings_package_man/samples/hostlist.py.sample  
に保存されているので、
package_man/settings_pacage_man/hostlist.py  
にコピーする。  

(例)
(venv_package_man)\$ cp package_man/settings_package_man/samples/hostlist.py.sample \\  
package_man/settings_package_man/hostlist.py


nanoなどのエディタを使ってhostlist.pyを編集。

以下、設定例。  
\----- package_man/settings_package_man/hostlist.py -----  
MANAGED_HOSTS_DCT = \{  
&nbsp;&nbsp;\# sshでアクセスするipアドレスをキーとする  
&nbsp;&nbsp;"192.168.0.100": {  
&nbsp;&nbsp;&nbsp;&nbsp;\# 必須設定項目  
&nbsp;&nbsp;&nbsp;&nbsp;\# sshのログインユーザとパスワードでログインする場合。ここで直に設定。   
&nbsp;&nbsp;&nbsp;&nbsp;"ssh": {  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_auth_method": "password",  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_user": "ssh_user",    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_password": "ssh_password",   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_secretkey_path": "$ANSIBLE_SSH_PRIVATE_KEY_FILE",  
&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;"name": "host0",  
&nbsp;&nbsp;&nbsp;&nbsp;"package_manager": "apt",

&nbsp;&nbsp;&nbsp;&nbsp;\# 任意設定項目(タグ)  
&nbsp;&nbsp;&nbsp;&nbsp;"env": "dev",  
&nbsp;&nbsp;},

&nbsp;&nbsp;"192.168.0.101": {  
&nbsp;&nbsp;&nbsp;&nbsp;\# 必須設定項目  
&nbsp;&nbsp;&nbsp;&nbsp;\# sshのログインユーザとパスワードでログインする場合。airflowホストの環境変数にsshログインユーザとパスワードを設定  
&nbsp;&nbsp;&nbsp;&nbsp;"ssh": {  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_auth_method": "password",  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_user": "$ANSIBLE_USER",    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_password": "$ANSIBLE_SSH_PASS",   
&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;"name": "host1",  
&nbsp;&nbsp;&nbsp;&nbsp;"package_manager": "apt",

&nbsp;&nbsp;&nbsp;&nbsp;\# 任意設定項目(タグ)  
&nbsp;&nbsp;&nbsp;&nbsp;"env": "dev",  
&nbsp;&nbsp;},

&nbsp;&nbsp;"192.168.0.110": {  
&nbsp;&nbsp;&nbsp;&nbsp;\# 必須設定項目  
&nbsp;&nbsp;&nbsp;&nbsp;\# 公開鍵でログインする場合。airflowホストの環境変数に公開鍵のペアとなる秘密鍵ファイルのパスを記述して設定。  
&nbsp;&nbsp;&nbsp;&nbsp;"ssh": {  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_auth_method": "keypair",  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_user": "ssh_user",    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_secretkey_path": "/home/your_username/.ssh/id_rsa",  
&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;"name": "host10",  
&nbsp;&nbsp;&nbsp;&nbsp;"package_manager": "apt",

&nbsp;&nbsp;&nbsp;&nbsp;\# 任意設定項目(タグ)  
&nbsp;&nbsp;&nbsp;&nbsp;"env": "dev",  
&nbsp;&nbsp;},

&nbsp;&nbsp;"192.168.0.111": {  
&nbsp;&nbsp;&nbsp;&nbsp;\# 必須設定項目  
&nbsp;&nbsp;&nbsp;&nbsp;\# 公開鍵でログインする場合。airflowホストの環境変数に公開鍵のペアとなる秘密鍵ファイルのパスをセットして設定。  
&nbsp;&nbsp;&nbsp;&nbsp;"ssh": {  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_auth_method": "keypair",  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_user": "$ANSIBLE_USER",    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ssh_secretkey_path": "$ANSIBLE_SSH_PRIVATE_KEY_FILE",  
&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;"name": "host11",  
&nbsp;&nbsp;&nbsp;&nbsp;"package_manager": "apt",

&nbsp;&nbsp;&nbsp;&nbsp;\# 任意設定項目(タグ)  
&nbsp;&nbsp;&nbsp;&nbsp;"env": "dev",  
&nbsp;&nbsp;},

&nbsp;&nbsp;\# 次のホストを同じように設定  
&nbsp;&nbsp;\# 以下続く  
  
}

\----- package_man/settings_package_man/hostlist.py -----   

パッケージデータ収集対象のホストの設定はpythonの辞書オブジェクト(変数名MANAGED_HOSTS_DC)で、json形式で定義する。  
複数のデータ収集対象ホストを登録可能。

<b>ホスト</b>  
ホストは、「<b><u>sshで接続するipアドレス</u></b>」で指定のこと  
(例) "192.168.0.100": {\<ホスト設定の中身\>}

以下は、必須設定項目  
"ssh"  
"name"  
"package_manager"  
は必須設定項目。

任意設定項目は、ホストのタグとして活用。  
"key": "value"  
の形式で任意に、いくつでも設定できる。  
アプリケーションが対象ホストをフィルタするために利用される。

<b>"ssh"の設定</b>  
パッケージデータ収集は、airflowホストがansibleを使って収集する。

"ssh_auth_method"は、ansibleのssh認証方式をパスワード認証にするか、公開鍵認証にするか指定。  
"password"、または"keypair"(公開鍵認証)で指定する。

"ssh_user"は、ansibleで対象ホストにログインする際のosユーザーを指定する。  
osユーザの指定において、airflowがインストールされたホストの環境変数を参照する場合は、\$\<環境変数\>の形式で環境変数を参照可能。  
linuxホストへの環境変数のセット方法は、複数ある。
一例として、airflowホストの/etc/environmentに、
ANSIBLE_USER="your_user_name"  
のように記述すると、airflowホスト起動時に、環境変数ANSIBLE_USERを自動読み込みする。
/etc/environmentを編集後、ホストを再起動せずに環境変数の設定を反映させたい場合はsourceコマンドを使って/etc/environmentを読み込む。  

(venv_package_man)\$ source /etc/environment

"ssh_password"は、ansibleでホストにログインする際のパスワードを指定する。  
"ssh_auth_method"が"keypair"の場合は、"ssh_password"は設定不要であり、何か設定されていても無視される。
ssh_userの設定と同様に、\$\<環境変数\>で環境変数を参照させることも可能。  
パスワードをプレーンテキストで設定ファイルに残すのはセキュリティ上好ましくないため、  
airflowホストの~/.profileや/etc/environmentに環境変数としてセットし、  
設定ファイル(hostlist.py)は環境変数を参照させること。
もしくは、利用開始前に最初に公開鍵認証に対応させること。

"ssh_secretkey_path"は、ansibleでホストに公開鍵認証でログインする際の秘密鍵のパスを指定する。
"ssh_auth_method"が"password"の場合は、設定不要。何か設定されていても無視される。
airflowがインストールされたホストの環境変数にセットしている場合は、\$\<環境変数\>で指定可能。
新たに鍵ペアを作成して、パッケージデータ収集ホストにairflowホストの公開鍵をコピー

<b>"name"の設定</b> 
ホスト名を設定する。  
ホスト名がfqdnである必要はなく、また、他のホストと重複しても問題ない。  
hostのインデックスは、ホストキーで指定したipアドレスとホスト名の組み合わせで一意に識別されるため。

<b>"package_manager"の設定</b>  
データ収集対象ホストのパッケージシステムを指定。  

(例)  
 "package_manager": "apt"

他には、"yum", "dnf", "pacman"などに対応予定。  

<b>任意設定項目</b>  
フィルタ用途で任意のタグをkey-value形式で設定すると後々便利。  
例えば、"env"というキーに、商用環境か、検証環境か、ステージング環境か設定しておくと、  
フィルタ機能を使って検証環境だけ対象にするなどの操作が可能。  
将来的にはパッケージの自動更新にも対応する予定なので、用途に合わせて任意設定項目を設定する。  
任意設定項目は、必要なだけ、複数設定可能である。

(例)  
"env": "dev"

# ４．ansibleのログインテスト
package_man/settings_package_man/hostlist.py  
が正しく設定できたかどうか確認する。

確認は、ansibleを使って行う。  
まずは、インベントリファイルを作成。  

(venv_package_man)\$ cd package_man/install_tools  
(venv_package_man)\$ make inventory  

package_man/settings_package_man/hostlist.pyの設定内容を元に、  
hostlist.pypackage_man/playbook配下に、インベントリファイル"inventory.yml"が自動生成される。  

ansible pingを使って、パッケージデータ収集対象のホストに正しくログインできるか確認。  
インベントリファイルを使ってansible pingを実行。

(venv_package_man)\$ cd package_man/playbook  
(venv_package_man)\$ ansible all -i inventory.yml -m ping

package_man/settings_package_man/hostlist.pyに記述したパッケージ情報収集対象ホストに  
ansibleで正しくログインできているか確認できる。
正しくログインできている場合は、以下のように出力される。

(正しくログインできた場合の出力例)  
\---------------  
hostname_192.168.0.100 | SUCCESS => {  
&nbsp;&nbsp;"ansible_facts": {  
&nbsp;&nbsp;&nbsp;&nbsp;"discovered_interpreter_python": "/usr/bin/python3"  
&nbsp;&nbsp;},  
&nbsp;&nbsp;"changed": false,  
&nbsp;&nbsp;"ping": "pong"  
}  
：  
以下、設定したすべてのホストがerrorなく出力されていればok。  
\---------------

ansibleによる対象ホストへのログインの確認のみであり、対象ホストの"package_manager"のチェックは行わない。  
ubuntuホストの"package_manager"に、"yum"などの誤ったパッケージシステムを設定した場合は、
パッケージ情報収集時にエラーを出力する。

# ５．ansibleのログインテスト




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




