[１．脆弱性の調査](#１．脆弱性の調査)  

# １．脆弱性の調査
## 1.1. 調査UIの起動と実行方法
脆弱性調査ツールは、jupyter labで作成。

脆弱性調査ツールは、pj_folder/notebooks配下に保存されている。  
実行手順は以下のとおり。  

pj_folder/notebooksディレクトリから、jupyter labを起動する  
\$ cd pj_folder/notebooks
\$ jupyter-lab --ip='0.0.0.0' --no-browser

起動すると、onetime Token入りのurlが出力される。  
例:  
http://127.0.0.1:8888/lab?token=9227d1418d138b01637cf3fb3246745a13be1fb210bc2e3d


jupyter labのwebサーバが起動するので、ブラウザからアクセス。  
http://\<host ip address\>:8888  
tokenの入力を求められたら、上記urlのtoken=の右に表示されたtokenを入力。

jupyter labから利用したいツールの実行ファイル(.ipynb)を開く。    
各脆弱性調査ツールにはパラメータ設定セルを作成している。  
このツールでパラメータを設定後、実行すると、ツールの実行結果が  出力される仕様になっている。

## 1.2. インストール済みパッケージ一覧の検索
ファイル名：  
　search_installed_pacages.ipynb  
概要:  
　package_name_stringで指定した文字列を含むinstalle済パッケージが検索され、  
　各ホストごとに、指定した文字列を含むパッケージの  
　hostname, os, ssh_ip_address, os, os_version, name, versionを一覧で出力    
パラメータ：  
　package_name_string   
設定例：  
　package_name_string = "ssh"

## 1.3. 脆弱性を含むパッケージのリストアップ
ファイル名：  
　check_vulnerability.ipynb  
概要:  
　　脆弱性対応が必要なパッケージのos, os_version, package, package_versionの  
　各パラメータを指定すると、install済パッケージを抽出し、脆弱性対象かどうかを評価。  
　脆弱性対応が必要なパッケージの一覧を出力する。  
　出力項目は、hostname, ssh_ip_address, os, os_version, name, versionの各項目。  
　　なお、os, os_version, packageについては、リストにあるものを正確に指定する必要がある。  
　os, os_versionについては、後述のoutput_managed_os.ipynbツールを実行して  
　正確なosとos_versionを指定するなどして、正確なパラメータを設定すること。  
　　また、pachageも正確なpackage名を指定する必要がある。  
　前述のsearch_installed_pacages.ipynbツールを実行するなどして正確なpackage名  
　を指定できるようにすること。  
パッケージバージョン指定方法：  
　package_versionの指定については、以下のいずれかのパターンで指定する。   
　patern1 "1:1.2.11.dfsg-2ubuntu9.2"のように、正確なバージョンを指定する  
　　　　epoc(1:の部分)を入れる場合、epocを優先的に評価する。  
　　　　versionが該当していても、epocが該当していなければリストアップされない。  
　patarn2 "1.2.11.dfsg-2ubuntu9.2"のように、epocを入力せずにversionのみ入力する。  
　　　　この場合、1.2.11のように、epoc情報は無視されて数字のバージョン情報のみ評価される。   
　　　　なお、文字が混ざった情報(.dfsg-2ubuntu9.2の部分)は評価時に無視される。  
　patern3 "1.2.11"のように、数字部分だけ指定する  
　　　　この場合、数字のバージョン情報のみで評価される。
　patarn4 "1.2.x"のように、枝バージョンをxで表記する  
　　　　この場合、1.2.xはxの数字が何であろうとすべて抽出される  
　　　　(実際にはxを"1000000"に変換して評価している)  
　patarn5 "1.2"のように、枝ーバージョン、下位バージョンを省略して指定する  
　　　　この場合、1.2.xと同じ評価結果となる  
　その他 オリジナルのバージョン情報の最上位が"2Ubuntu3"のように、文字入りの場合、  
　　　　バージョン比較ができない。  
　　　　この場合、transformed_versionは0に変換されるので、指定バージョンにかかわらず  
　　　　該当パッケージがすべて脆弱性対象として抽出される。  
パラメータ：  
　os, os_version, package, package_version  
設定例：  
　os = "Ubuntu"  
　os_version = "22.04"  
　package = "zlib1g"  
　package_version = "1:1.2.11.dfsg-2ubuntu9.2"  
出力：  
　該当パッケージリストは、脆弱性の有無にかかわらず、install済の指定packageの一覧。  
　要脆弱性リストは、該当パッケージリストのうち、脆弱性対応が必要なもののみ抽出したpackageの一覧。