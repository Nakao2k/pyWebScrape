import json
import os
import sys
import time
# chromedriver_binaryをインポートしないとselenium.webdriverは動かない
import chromedriver_binary
import yaml

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
# 事前に　pip install chromedriver-binary==104.0.5112.20.0
from selenium import webdriver

# 設定ファイルの側
cfg = {
    "protocol": "",
    "filter_html_tag": "",
    "login": {
        "path": "",
        "xpath_id": "",
        "xpath_password": '',
        "xpath_button": ''
    },
    "session_id": {
        "name": ""
    },
    "hostname": {
        "path": "",
        "xpath": ''
    },
    "logout": {
        "path": ""
    },
    "lst_html": [],
    "lst_script": []
}

class ClsFullUrl:
    def __init__(self, argProtocol, argServer):
        self.protocol = argProtocol
        self.server = argServer
        self.sessionId = ""
        self.sessionValue = ""

    def setSessionId(self, argSessionId, argSessionValue):
        self.sessionId = argSessionId
        self.sessionValue = argSessionValue

    def getFullUrl(self, argPath):

        if not argPath.startswith("/"):
            argPath = "/" + argPath

        # Hostnameを取得
        if self.sessionId == "":
            fullUrl = self.protocol + self.server + argPath
        else:
            fullUrl = self.protocol + self.server + argPath + "?" + self.sessionId + "=" + self.sessionValue

        return fullUrl


def get_element_value(arg_elem, arg_key_attr):
    if arg_key_attr == "text":
        value = arg_elem.text
    elif arg_key_attr == "SPECIAL_TEXT":
        value = arg_elem.get_attribute("text")
    else:
        value = arg_elem.get_attribute(arg_key_attr)

    return value


def makeFooterHtml(argPngFile):
    strResult = "\n"
    strResult += '<hr style="border-top: 5px solid black;" />' + "\n"
    strResult += '<img src="' + argPngFile + '" />' + "\n"

    return strResult


def getFileName(argPath):
    return os.path.basename(argPath)


def getTypeFirstFile(argPath, argIpAddr, argHostname, argExt):
    lstSplit = os.path.splitext(os.path.basename(argPath))

    basename = lstSplit[0]

    if len(lstSplit) >= 2:
        ext = lstSplit[1]
    else:
        ext = ""

    if argExt != "":
        ext = argExt

    fullName = argIpAddr + "_" + argHostname + "_" + basename + ext

    return fullName


def getTypeSecondFile(argPath, argIpAddr, argHostname, argExt):
    lstSplit = os.path.splitext(os.path.basename(argPath))

    basename = lstSplit[0]

    if len(lstSplit) >= 2:
        ext = lstSplit[1]
    else:
        ext = ""

    if argExt != "":
        ext = argExt

    fullName = basename + "_" + argIpAddr + "_" + argHostname + ext

    return fullName

# 引数例："192.168.0.1" "admin" "Password" "Nec_AtermWX3000HP.json" "NEC" "3"
# 引数例："192.168.0.239" "" "Password" "Netgear_X521EM.json" "Netgear" "1"
# argServer = "192.168.0.239"
# argLoginId = "admin"
# argPassword = "Password"
# argCfgFile = "Netgear_X512EM.yaml"
# argOutDir = "testOutDir"
# argSleepTime = 1
if __name__ == '__main__':
    # 引数の取得
    args = sys.argv

    # 必須引数の数を確認
    # 下記args[n]であればをlen(args) <= nを指定
    if len(args) <= 6:
        print("引数が足りません")
        sys.exit(1)

    # 必須引数の取得
    argServer = args[1]
    argLoginId = args[2]
    argPassword = args[3]
    argCfgFile = args[4]
    argOutDir = args[5]
    argSleepTime = 1

    # 引数の値が正しければ引数の値を登録
    if str.isdigit(args[6]):
        argSleepTime = int(args[6])

    # IDとパスワードを実行引数に渡したくない場合はここに入力して、コメントを外す
    # 実行引数には""を指定
    #argLoginId = ""
    #argPassword = ""

    try:
        with open(argCfgFile, 'r') as file:
            #cfg = yaml.safe_load(file)
            cfg = json.load(file)
            print(cfg)
    except Exception as e:
        print('Exception occurred while loading json...', file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)

    # URL管理クラスの生成
    clsFullUrl = ClsFullUrl(cfg["protocol"], argServer)

    # Webブラウザのオプション設定
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    try:
        # セッションIDの初期化
        session_id = ""

        # Webブラウザのインスタンス化
        driver = webdriver.Chrome(options=options)

        # Loginページへの接続
        fullUrl = clsFullUrl.getFullUrl(cfg["login"]["path"])
        driver.get(fullUrl)

        # Login IDを入力
        if argLoginId != "":
            formLoginId = driver.find_element(by=By.XPATH, value=cfg["login"]["xpath_id"])
            formLoginId.send_keys(argLoginId)

        # Login Passwordを入力
        formPassword = driver.find_element(by=By.XPATH, value=cfg["login"]["xpath_password"])
        formPassword.send_keys(argPassword)

        # ログインボタンを押下
        loginButton = driver.find_element(by=By.XPATH, value=cfg["login"]["xpath_button"])
        loginButton.click()

        # ボタンを押下したのでSleep処理が必要
        time.sleep(argSleepTime)

        # Session ID取得 Start
        if cfg["session_id"]["id"] != "":
            elem = driver.find_element(by=By.XPATH, value=cfg["session_id"]["xpath"])
            session_id = get_element_value(elem, cfg["session_id"]["xpath_attr"])

            clsFullUrl.setSessionId(cfg["session_id"]["id"], session_id)
        # Session ID取得 End

        # ホスト名の取得 Start
        fullUrl = clsFullUrl.getFullUrl(cfg["hostname"]["path"])
        print(fullUrl)
        driver.get(fullUrl)

        elem = driver.find_element(by=By.XPATH, value=cfg["hostname"]["xpath"])
        hostname = get_element_value(elem, cfg["hostname"]["xpath_attr"])

        if hostname == "":
            print("Failed to get the hostname")
            sys.exit(1)
        # ホスト名の取得 End

        # 出力先フォルダの作成 Start
        if not os.path.exists(argOutDir):
            os.mkdir(argOutDir)

        os.chdir(argOutDir)
        # 出力先フォルダの作成 End

        # HTMLファイルの取得 Start
        for itemPage in cfg["lst_html"]:
            # 取得対象HTMLファイルを取得
            fullUrl = clsFullUrl.getFullUrl(itemPage)
            driver.get(fullUrl)
            time.sleep(argSleepTime)

            # BeautifulSoupを利用して<body>タグを取得
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            soBody = soup.find(cfg["filter_html_tag"])

            # URL内のファイル名を取得。ディレクトリ部分を削除
            outHtmlFile = getFileName(itemPage)

            # IPアドレスを元にしたファイル名
            outTypeFirst = getTypeFirstFile(outHtmlFile, argServer, hostname, ".html")

            # 機能を元にしたファイル名
            outTypeSecond = getTypeSecondFile(outHtmlFile, argServer, hostname, ".html")

            # get width and height of the page
            intWidth = driver.execute_script("return document.body.scrollWidth;")
            intHeight = driver.execute_script("return document.body.scrollHeight;")

            # set window size
            driver.set_window_size(intWidth, intHeight)

            # HTMLスクリーンショット画像ファイル作成 Type1
            print(outTypeFirst)
            driver.save_screenshot(outTypeFirst + ".png")
            cTagFooter = makeFooterHtml(outTypeFirst + ".png")

            # HTMLファイル作成 Type1
            with open(outTypeFirst, mode='wb') as f:
                f.write(soBody.encode('utf-8'))
            with open(outTypeFirst, mode='a', encoding='utf-8') as f:
                f.write(cTagFooter)

            # HTMLスクリーンショット画像ファイル作成 Type2
            print(outTypeSecond)
            driver.save_screenshot(outTypeSecond + ".png")

            # HTMLファイル作成 Type2
            with open(outTypeSecond, mode='wb') as f:
                f.write(soBody.encode('utf-8'))
            with open(outTypeSecond, mode='a', encoding='utf-8') as f:
                f.write(cTagFooter)

        # HTMLファイルの取得 End

        # css/jsファイルの取得 Start
        for itemPage in cfg["lst_script"]:
            # 取得対象スクリプトファイルを取得
            fullUrl = clsFullUrl.getFullUrl(itemPage)
            driver.get(fullUrl)
            time.sleep(argSleepTime)

            # 書き込み準備
            outHtmlFile = getFileName(itemPage)

            # IPアドレスを元にしたファイル名
            outTypeFirst = getTypeFirstFile(outHtmlFile, argServer, hostname, "")

            # 機能を元にしたファイル名
            outTypeSecond = getTypeSecondFile(outHtmlFile, argServer, hostname, "")

            print(outTypeFirst)
            with open(outTypeFirst, mode='w', encoding='utf-8') as f:
                f.write(driver.page_source)

            print(outTypeSecond)
            with open(outTypeSecond, mode='w', encoding='utf-8') as f:
                f.write(driver.page_source)

        # css/jsファイルの取得 End

    finally:
        # Session IDを取得していればログアウト処理を実施
        if session_id != "":
            # Logoutページへの接続
            if cfg["logout"]["path"] != "":
                urlLogout = clsFullUrl.getFullUrl(cfg["logout"]["path"])
                print(urlLogout)
                driver.get(urlLogout)
                time.sleep(argSleepTime)

        # Webブラウザの終了処理
        driver.quit()
        print("webdriver is closed")

