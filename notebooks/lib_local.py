# $ jupyter-lab --ip='0.0.0.0' --no-browser

from pathlib import Path
import sys

# set package_man project root directory in string type object
PJROOT_DIR = Path(__file__).parent.parent
DATA_DIR = PJROOT_DIR / "data_package_man"

# import objects
import pyarrow.parquet as pq
from packaging import version
import re
import pandas as pd
from IPython.display import display, HTML

class PackageList():
    def __init__(self):
        # 標準出力する際のデフォルト出力列
        self.output_cols = [
            "hostname",
            "ssh_ip_address",
            "os", 
            "os_version",
            "name",
            "version"
        ]

        # 出力データをdfに読み込む
        fp = DATA_DIR / "package_list_data.parquet"
        data = pq.read_table(str(fp))
        self.df = data.to_pandas()

        # version情報にepocを含む場合は、epocだけ別列に分離
        self.df["epoc"] = self.df["version"].apply(self._set_epoc)

        # version情報を、比較できるように加工する
        # 加工する際、epocを切り捨てる
        self.df["transformed_versiondata"] = self.df["version"].apply(self._transform_versiondata)

        # 比較のため、"version"をparseした列を追加
        # ubuntuのバージョニングにある、"12ubuntu4.4"のようなversionは、評価できないため、parsed_version列は0に置き換える
        self.df["parsed_versiondata"] = self.df["transformed_versiondata"].apply(self._parse_versiondata)
    
    # package_name_string文字列を含む、管理対象ホストへのinstall済packageの一覧をhtml出力するか、
    # html_output_flg = Falseの場合は検索結果のpandas.DataFrameをreturnする。
    # package_name_stringのアルファベットの大文字と小文字は区別しないので、大文字小文字は気にしなくて良い。
    def search_installed_packages(self, package_name_string, html_output_flg=True):
        df = self.df
        df = df[df["name"].str.contains(package_name_string, case=False)]

        if html_output_flg:
            print("検索結果(pandas.DataFrame)：")
            display(HTML(df[self.output_cols].to_html()))
            print()
        
        return df[self.output_cols]


    
    # os, os_versionについては、リストにあるものを正確に指定すること
    # package_versionの指定については、以下のいずれかのパターンで指定する。
    # patern1 "1:1.2.11.dfsg-2ubuntu9.2"のように、正確に指定する
    #   epocを入れる場合、epocを優先的に評価するので要注意。versionが該当していても、epocが該当していなければ無視する
    # patarn2 "1.2.11.dfsg-2ubuntu9.2"のように、epocを入力せずにversionのみ入力する
    #   この場合、1.2.11のように、数字の部分だけ比較評価され、文字が混ざった情報.dfsg-2ubuntu9.2は省略されて評価する。
    # patern3 "1.2.11"のように、数字部分だけ指定する
    # patarn3 "1.2.x"のように、枝バージョンをxで表記する
    #   この場合、1.2.xはxの数字が何であろうとすべて抽出される(実際にはxを"1000000"に変換して評価している)
    # patarn4 "1.2"のように、枝ーバージョン、下位バージョンを省略して指定する
    #   この場合、1.2.xと同じ抽出結果となる
    # その他 オリジナルのバージョン情報の最上位が"2Ubuntu3"のように、文字入りの場合、バージョン比較ができない。
    #   この場合、transformed_versionは0に変換されるので、指定バージョンにかかわらず該当パッケージがすべて抽出される。
    #
    # html_output_flg = Falseの場合、該当パッケージリストと、脆弱性該当パッケージリストのpandas.DataFrameをタプルで返す
    # この場合、結果の出力は呼び出し側で行う。
    # html_output_flg = Trueは、jupyterから呼び出す場合を想定。該当パッケージリストと、脆弱性該当パッケージリストのpandas.DataFrameをhtmlで出力。
    # 該当パッケージリストと、脆弱性該当パッケージリストのpandas.DataFrameオブジェクトはreturnされない。
    def check_vulnerability(self, os, os_version, package, package_version, html_output_flg=True):
        # 標準出力の列幅を無制限に
        pd.set_option('display.max_colwidth', 1000)

        # check_vulnerabiiltyのvalidationチェックとpackage_version比較対象packageのリストアップ
        candidate_df = self._check_vulnerability_extract_target_package(os, os_version, package)
        if candidate_df is None:
            return

        if html_output_flg:
            print("該当パッケージリスト(pandas.DataFrame)：")
            display(HTML(candidate_df[self.output_cols].to_html()))
            print()

        # 入力されたpackage_versionを、比較できるようにtransformしてparseする。
        # transformする際、末尾に.1000000を追記する。また、.xを.1000000に変換する
        # 入力バージョンが2、実バージョンが2.xの場合に、上記処理をしないとうまくtargetlistを抽出できないため
        input_epoc = self._set_epoc(package_version)
        input_transformed_version = self._transform_versiondata(package_version)
        if ".x" in input_transformed_version:
            input_transformed_version = input_transformed_version.replace(".x", ".1000000")
        else:
            input_transformed_version += ".1000000"

        input_parsed_version = self._parse_versiondata(input_transformed_version)

        # debug
        # print(input_epoc, input_parsed_version)

        # epocがある場合は、epocを比較する
        if not input_epoc is None:
            target_df1 = candidate_df[candidate_df["epoc"]<input_epoc]
            
            candidate_df = candidate_df[candidate_df["epoc"]==input_epoc]
            target_df2 = candidate_df[candidate_df["parsed_versiondata"]<=input_parsed_version]

            target_df = pd.concat([target_df1, target_df2], ignore_index=True)
        
        else:
            target_df = candidate_df[candidate_df["parsed_versiondata"]<=input_parsed_version]
        
        if html_output_flg:
            print("要脆弱性対応リスト(pandas.DataFrame)：")
            display(HTML(target_df[self.output_cols].to_html()))
        
        return candidate_df[self.output_cols], target_df[self.output_cols]

    def _parse_versiondata(self, v):
        if v == "":
            v = "0"
        return version.parse(v)

    # validation check & filter target packages
    def _check_vulnerability_extract_target_package(self, os, os_version, package):
        df = self.df
        pdf = df[df["os"]==os]
        if len(pdf.index) == 0:
            print(f"osが{os}のVMは存在しません\n管理対象OSは以下です：\n->{df['os'].drop_duplicates().tolist()}")
            return
        ppdf = pdf[pdf["os_version"]==os_version]
        if len(ppdf.index) == 0:
            print(f"バージョン{os_version}の{os}のVMは存在しません\n管理対象の{os}のVMのバージョンは以下です：\n ->{pdf['os_version'].drop_duplicates().tolist()}")
            return
        pppdf = ppdf[ppdf["name"]==package]
        if len(pppdf.index) == 0:
            print(f"管理している{os}{os_version}のVMに、{package}パッケージはインストールされていません\n導入済パッケージのリストは以下です：\n->")
            pkgs =ppdf['name'].drop_duplicates().tolist()
            for p in pkgs:
                print(f" {p}")    
            return
        
        # バージョンチェック
        target_df = pppdf.copy()

        return target_df

    # versiondataを、versionメソッドで比較できるように加工する
    def _transform_versiondata(self, v):
        # step0: epocがある場合は、epocを切り離す
        l = v.split(":")
        v = l[-1]

        # step1: "-"で分離して"-"から後ろを省略
        l = v.split("-")
        v = l[0]

        # step2: バージョン情報を"."で分け、
        # 文字列(ただし、:は除く)を含むバージョン情報があったら、それより後ろの情報は切り捨てる
        l = v.split(".")
        i = 0
        for c in l:
            pattern = r'[^0-9:]'
            if re.search(pattern, c):
                break
            i += 1
        
        l = l[:i]

        v =  ".".join(l)

        return v
    
    def _set_epoc(self, v):
        l = v.split(":")

        if len(l) >= 2:
            return l[0]
        else:
            return None

if __name__ == '__main__':
    ins_PL = PackageList()
    
    os = "Ubuntu"
    os_version = "22.04"
    package = "zlib1g"
    package_version = "1:1.2.11.dfsg-2ubuntu9.2"
    package_version = "1:1.2.x"
    ins_PL.check_vulnerability(os, os_version, package, package_version)
    
