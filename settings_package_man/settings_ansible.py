#
ANSIBLE_CONF = {
    "inventory_fname": "inventory.yml",
    # playbookの中のホスト名を一意にするために、playbookの中で扱うホスト名をhostlist.pyの
    # {name}_{ssh_ip_address}の形式に変換するかどうか
    # True: ホスト名を{name}_{ssh_ip_address}に変換
    # False: ホスト名を{name}で扱う
    # 基本、Trueで利用。
    "hostname_with_ip": True,
    "get_os_version_playbook_fname": "get-os-version.yml",
    "get_packages_playbook_fname": "get-packages.yml",
    "upgrade_package_playbook_fname": "upgrade-package.yml"
}