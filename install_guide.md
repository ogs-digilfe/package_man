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

\$ cd /path/to/project_folders  
\$ git clone https://github.com/ogs-digilfe/package_man 

以下、プロジェクトフォルダ名をpackage_manとして記述。

## 2.3. アプリケーションのビルド
pacage_man/install_tools/Makefileを実行して、アプリケーションをinstall&ビルドする。
pacage_man/install_toolsに移動し、

\$ make install

## 2.4. アプリケーション動作環境のセット
make installコマンド実行時に、package_man(airflow)アプリケーションを実行するための仮想環境が  
作成される。  
ただし、install直後は、アプリケーションが参照する環境変数の設定や、アプリケーションを実行するシェルの仮想環境へのスイッチがなされていない。  
package_man/install_toolsのシェルスクリプト"set_airflow_env.sh"を実行してアプリケーション環境をセットする。

\$ source set_airflow_env.sh

シェルスクリプトを実行すると、シェルがpackage_man(airflow)実行するための環境変数をセットし、実行するための仮想環境のシェルにスイッチする。  
シェルプロンプトの前に仮想環境名(venv_package_man)が表示されればok。

次回以降sshログイン時は、ログイン時に<b><u>自動でpackage_man(airflow)を実行するためのpython仮想環境にスイッチ</u></b>する。  
ただし、シェルプロンプトの前の(venv_package_man)は表示されない。  
自身がどのpython実行環境にいるか確認したい場合は、whichコマンドでpythonインタープリタへのパスを表示することで確認することができる。  
仮想環境のpythonインタープリタが表示されたら、仮想環境にスイッチしている。

\$ which python  
/path/to/venv_package_man/bin/python

# ３．アプリケーションの初期設定
## 3.1. airflowコマンドへのパスが通っているか、確認
whichコマンドで、airflow実行ファイルへのパスが表示されたらok。

\$ which airflow  
/path/to/venv_package_man/bin/airflow

補足  
airflow実行ファイルは、make install実行時に作成されたpython仮想環境の中に作成されている。
以後、python実行環境がpackage_man(airflow)仮想環境にスイッチされている状態であれば、  
任意のフォルダですべてのairflowコマンドを実行可能。

## 3.1. airflow初期ユーザ登録
airflowの管理コンソールwebにログインするための初期ユーザを設定。
role以外の設定値は、適宜書き換える。  

\$ airflow users create  --username user  --firstname firstname --lastname lastname --role Admin --email email@domain.com

初期パスワード設定のプロンプトが表示されるので、パスワード設定をして初期ユーザ登録は完了。

airflowの登録ユーザの確認は、  

\$ airflow users list

## 3.4. webサーバの起動
仮想環境から、airflowに付属のwebaplicationを起動して初期ユーザでログインできるか確認する。  
-pオプションでポート番号は自由に設定可能であるが、以下、8080に指定したことを前提に説明。  
(venv_package_man)\$ airflow webserver -p 8080  

(例)  
http://\<package_manホストip address\>:8080

とりあえず、初期ユーザでログインできたらok。
一旦、Ctrl+Cでairflow webサーバのプロセスを落とし、ブラウザを閉じる。  

## 3.5. 対象ホストの設定
パッケージ情報を収集先ホストのホスト情報の設定をする。  

サンプルの設定ファイルが、  
package_man/settings_package_man/samples/hostlist.py.sample  
に保存されているので、
package_man/settings_pacage_man/hostlist.py  
にコピーする。  

(例)
(venv_package_man)\$ cd /path/to/package_man
(venv_package_man)\$ cp settings_package_man/samples/hostlist.py.sample settings_package_man/hostlist.py

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
即時反映させたい場合は、exportコマンドで反映させる。


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
新たに鍵ペアを作成して、パッケージデータ収集ホストにairflowホストの公開鍵をコピー。

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

## 3.6. 認証情報の環境変数設定(オプション)
package_man/settings_package_man/hostlist.py  
で、認証情報を環境変数から参照する場合は、

~/.profile  
または/および
/etc/profile.d/set_airflow_env.sh

に、環境変数を設定するexportコマンドのスクリプトを追記する。  
環境変数はpackage_man/settings_package_man/hostlist.pyから参照される。
参照される認証情報の環境変数はすべて設定すること。

~/.profileは、~でsshログイン時に実行される。
/etc/profile.d/set_airflow_env.shは、ホスト起動時に実行される。

例  
export ANSIBLE_USER=your_loginname  
export ANSIBLE_SSH_PASS=your_login_password

export ANSIBLE_SSH_PRIVATE_KEY_FILE=/home/username/.ssh/keypair

※対象ホストへのログインに公開鍵認証を利用する場合は、先にkeypairを作成し、ログイン先ホストに公開鍵を渡しておく必要がある。

環境変数の設定が完了したら、  
~/.profile  
に設定した場合は一旦logout/loginしなおす。

/etc/profile.d/set_airflow_env.sh  
に設定した場合は、一度システムを再起動する。

再度ログインしたら、echoコマンドを使って環境変数が正しく設定されているか確認。

確認例  
\$ echo $ANSIBLE_USER  
your_loginname

# ４．ansibleのSSHによるログインテスト
package_man/settings_package_man/hostlist.py  
が正しく設定できたかどうか確認する。

package_manはansibleを使ってhostlist.pyに登録したホストのインストール済パッケージリストを  
取得する。  
このため、package_manホストから、パッケージリスト取得対象ホストに対してSSHでログインできる必要がある。  
この確認は、ansibleを使って行う。  
まずは、install_toolsフォルダでmake inventoryコマンドを実行して、hostlist.pyから、ansibleのインベントリファイルを作成する。

(venv_package_man)\$ cd package_man/install_tools  
(venv_package_man)\$ make inventory  

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
以下、設定したすべてのホストがerrorなくSUCESSと出力されていればok。  
\---------------

うまくいかない場合は、hostlist.pyの認証情報設定や、環境変数設定がうまくいってない可能性が高い。  
修正する。  

環境変数の設定を編集した場合は、再度logout/login、または再起動するなどして環境変数を再読み込みさせる。

hostlist.pyを修正した場合は、修正後、再度以下を実行してansible pingで確認。
(venv_package_man)\$ cd package_man/install_tools  
(venv_package_man)\$ make inventory  

補足  
ansible pingの確認は、対象ホストへのログインの確認のみであり、対象ホストの"package_manager"のチェックは行わない。  
ubuntuホストの"package_manager"に、"yum"などの誤ったパッケージシステムを設定した場合は、
パッケージ情報収集時にエラーを出力する。

# ５．package_manアプリケーションの起動
package_manは、airflowのアプリケーションである。  
airflowは、2つのサービスで構成される。  
(1) airflowスケジューラ
スケジューリングされた設定に従って、hostlist.pyに登録されたホストのインストール済パッケージを取得。  
デフォルトでは毎時AM2:00に実行される。  
(2) airflow webサーバ
アプリケーションの実行ログを管理するためのコンソール。  

以下のコマンドを実行して、スケジューラとairflow webサーバを起動する。
バックグラウンドプロセスとして起動する場合は、nohupコマンドとリダイレクトを使って起動。

\$ nohup airflow scheduler > /dev/null 2>&1 &  
\$ nohup airflow webserver -p 8080 > /dev/null 2>&1 &

補足  
airflow webserverのポート番号は自由に設定できる。

補足  
サービスを落としたい場合は、

\$ ps -ax |grep airflow

で、airfowスケジューラとairflow webサーバそれぞれのメインプロセスのidを確認し、killコマンドでprocess idを指定して落とす。

スケジューラメインプロセスの例

4900 pts/0    S      0:01 /home/user/venv_package_man/bin/python /home/user/venv_package_man/bin/airflow scheduler

この場合、process idは4900。

airflow webサーバのメインプロセスの例

4908 pts/0    S      0:00 /home/user/venv_package_man/bin/python /home/user/venv_package_man/bin/airflow webserver -p 8080

この場合、process idは4908

サービスダウン  
\$ kill <airflow webサーバのプロセスID>  
\$ kill <airflow スケジューラのプロセスID>

# ６．対象ホストのインストール済パッケージ情報の収集
ローカルホストのブラウザを起動し、airflow webサーバにログインする。

http://\<package_manホストip address\>:8080

例  
http://10.255.1.1:8080

ログイン完了すると、DAGの一覧ページが表示される。  
DAGとは、airflowが管理するスケジューラプログラムコードである。  
対象ホストのパッケージ情報を収集するDAGは、
collect_host_package_list_\<version\>  
である。

DAGの左にトグルスイッチがついていて、デフォルトではOFFの状態になっているので、クリックしてONにする。
DAG名collect_host_package_list_\<version\>がリンクになっているので、クリックして  
DAGの詳細画面を表示する。

画面右上に、右向きの矢印アイコン(実行ボタン)があるので、クリック。  
DAGが実行され、対象ホストのインストール済パッケージリストを収集する。

画面左に、実行結果が表示される。  
すべて正常に処理が進んでhostlist.pyのインストール済パッケージ一覧が取得できたら、  
すべてのゲージが緑色で表示される。  
エラーが出た場合は、hostlist.pyの設定に誤りがあって、正しく収集できていないため、ログを確認して  

package_man/settings_package_man/hostlist.py  

を正しく修正し、再度DAGを実行してみること。

補足  
(1)DAG実行ボタンの上に、スケジュール情報が表示されている。  
デフォルトでは、毎朝2時に自動で実行される。  
(2)画面左の進捗ゲージ  
画面左の進捗ゲージにある、  
update_playbooks～backup_settings_package_man_filesは、このDAGの処理ステップ(task)である。  
概要は以下のとおり。  
update_playbooks:  
&nbsp;&nbsp;hostlist.pyからinventoryファイルと、package情報を収集するためのansible playbookを作成する  
collect_and_update_installed_host_packages  
&nbsp;&nbsp;作成されたplaybookを実行して対象ホストのパッケージリストを収集する  
update_host_packages_parquet_data  
&nbsp;&nbsp;収集されたホストごとのパッケージリストを分析、加工が容易な表形式に変換し、parquet形式のファイルとして保存。
backup_settings_package_man_files  
&nbsp;&nbsp;DAG実行時に、package_man/settings_package_man配下の設定ファイルに変更が生じていた場合は、  
&nbsp;&nbsp;tar.gz形式のbackupをとっておく。  
&nbsp;&nbsp;デフォルトでは、バックアップは3世代保存される。

# ７．パッケージの検索と脆弱性情報の確認  
package_manでは、jupyter labのnotebookで作成したいくつかのツールを利用することができる。

jupyter labについては、利用時に都度、sshでpackage_manサーバにアクセスし、  
アクセスしたシェルからforegroundで起動する運用とする。  
利用終了時はforegroundで起動したプロセスをCtrl＋Cでkillする。  
foregroundでの起動であるため、sshセッション断で自動killされる。

## 7.1. jupyter labの起動
airflowのDAGが収集したホストごとのパッケージデータは、jupyter labのnotebookを使って検索したり、  
脆弱性情報に該当するかどうか調べることができる。  

\$ cd package_man/notebooks  
\$ jupyter lab --ip='0.0.0.0' --no-browser  

    To access the server, open this file in a browser:
        file:///home/user/.local/share/jupyter/runtime/jpserver-12408-open.html
    Or copy and paste one of these URLs:
        http://hostname:8888/lab?token=8cb85ef8d422d6ddbe87cc87bafec9ebe086d09d0de1ab59
        http://127.0.0.1:8888/lab?token=8cb85ef8d422d6ddbe87cc87bafec9ebe086d09d0de1ab59

package_manホストに接続可能な端末のwebブラウザから、  
http://\<ip_address\>\:8888
で起動したjupyter labにアクセス。  
ログインのためにtokenの入力が求められるので、上記のように、jupyter lab起動時に出力されたtoken  
をコピーしてログインする。

## 7.2. パッケージの検索
パッケージの検索は、  
search_installed_pacages.ipynb  
で行う。  

jupyter labのweb画面から、
search_installed_pacages.ipynb  
を開く。

パラメータ設定セルで、  
package_name_string = "GnuTLS"  
のように、パッケージ名のパッケージ名の一部の文字列を代入してjupyter labを実行すると、  
DAGが収集してきたパッケージリストから、指定した文字列を含むホストとパッケージのリスト  
を出力する。

## 7.3. パッケージ脆弱性チェック
パッケージ脆弱性のチェックは、  
check_vulnerability.ipynb  
で行う。  

パラメータ設定セルで、 

os = "Ubuntu"  
os_version = "22.04"  
package = "zlib1g"  
package_version = "1.2.11"  

の各項目を代入すると、該当パッケージと、package_versionで指定したバージョン以下の  
パッケージリストを出力する。  

os, os_version, packageの各項目は正確に指定する必要があることから、  
先に  
search_installed_pacages.ipynb  
でパッケージリストを検索してから利用するとよい。
