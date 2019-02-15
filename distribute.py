from biplist import *
import os, zipfile, shutil

# 预配置
# url = 'https://192.168.21.102:8081/static'
url = None

# 请勿修改
ipa_path = None
file_name = None


def file_exist():
    global ipa_path, file_name
    cwd = os.getcwd()
    for path, dirs, files in os.walk(cwd):
        for file in files:
            if '.ipa' in file:
                ipa_path = path + '/' + file
                file_name = file.replace('.ipa', '')
                break
    if not ipa_path:
        print('没有找到ipa文件，请检查后重试')
        exit()
    return cwd


def extract_info(cwd):
    global file_name, url
    with zipfile.ZipFile(ipa_path) as ipa_file:
        ipa_file.extractall()

    payload_fp = cwd + '/Payload'
    app_fp = '%s/%s.app' % (payload_fp, file_name)
    img_fp = app_fp + '/AppIcon60x60@3x.png'
    plist_fp = app_fp + '/Info.plist'
    shutil.copy(img_fp, cwd)
    p = readPlist(plist_fp)
    bundle_id = p.get('CFBundleIdentifier')
    display_name = p.get('CFBundleDisplayName')
    version = p.get('CFBundleVersion')
    sub_version = p.get('CFBundleShortVersionString')
    print(bundle_id, display_name, version, sub_version)
    if not url:
        url = input("信息提取已完成，请输入URL路径")
        if url[-1] != '/':
            url += '/'
    package = {'kind': 'software-package', 'url': url + file_name + '.ipa'}
    display_image = {'kind': 'display-image', 'url': url + 'AppIcon60x60@3x.png'}
    metadata = {'bundle-identifier': bundle_id, 'bundle-version': sub_version, 'kind': 'software',
                'releaseNotes': version,
                'title': display_name}
    plist_f_d = {'items': [{'assets': [package, display_image], 'metadata': metadata}]}
    writePlist(plist_f_d, file_name+'.plist')
    shutil.rmtree(payload_fp)


if __name__ == "__main__":
    f = file_exist()
    extract_info(f)
