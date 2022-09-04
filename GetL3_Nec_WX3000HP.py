import os
import re
import sys
import time
# chromedriver_binaryをインポートしないとselenium.webdriverは動かない
import chromedriver_binary

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
# 事前に　pip install chromedriver-binary==104.0.5112.20.0
from selenium import webdriver

# ネットワーク機器に応じて変更するパラメーター Start
# ログイン画面にあるHTMLタグのID属性、Name属性を指定
# ログインに使用するIDやパスワードではないので注意
# 出力フォルダ
PARAM_OUTDIR = "NEC"
# 接続プロトコル 通常はhttp or https
PARAM_PROTOCOL = "http://"
PARAM_XPATH_LOGINID = '//*[@id="loginusr"]'
PARAM_XPATH_LOGINPASSWORD = '//*[@id="loginpwd"]'
PARAM_NAME_SESSIONID = ""

# Loginボタンのxpath
PARAM_XPATH_LOGINBUTTON = '//*[@id="login"]/div/p[1]/a'

# Loginページ
PARAM_LOGIN_PAGE = ""

# Logoutページ
PARAM_LOGOUT_PAGE = ""

# 取得対象のURL
PARAM_LST_PAGES = [
    "basic_main.php",
    "amgr_mape.php",
    "air_basic_main2.php",
    "air24g_main_pri.php",
    "air5g_main_pri.php",
    "mac_filter_main.php",
    "wps_main.php",
    "wifi_notify.php",
    "info_mape_main.php"
]

# 取得対象のスクリプト(js, css)
PARAM_LST_SCRIPTS = []

# ホスト名が書かれたWebページ
PARAM_HOST_PAGE = ""
PARAM_XPATH_HOSTNAME = '//*[@id="device"]'

# ネットワーク機器に応じて変更するパラメーター End

# 変わることのない固定文字 Start
# ログインID
CNST_LOGIN_ID = "admin"
# 出力する対象のHTMLタグを指定。通常は"body" or "html"。
CNST_TARGET_HTMLTAG = "body"
# 変わることのない固定文字 End

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


def getFullUrl(argUrlServer, argPath, argParam, argValue):
    # Hostnameを取得
    if argParam == "":
        fullUrl = argUrlServer + argPath
    else:
        fullUrl = argUrlServer + argPath + "?" + argParam + "=" + argValue

    return fullUrl


if __name__ == '__main__':
    # 引数の取得
    args = sys.argv

    # 必須引数の数を確認
    if len(args) <= 2:
        print("引数が足りません")
        exit(1)

    # 必須引数の取得
    argServer = args[1]
    argPassword = args[2]

    # オプション引数の確認と取得
    argSleepTime = 1

    if len(args) > 3 and str.isdigit(args[3]):
        argSleepTime = int(args[3])

    # argServer = "192.168.0.1"
    # argPassword = "Password"

    # 機器のRoot URL
    urlServer = PARAM_PROTOCOL + argServer + "/"

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
        fullUrl = getFullUrl(urlServer, PARAM_LOGIN_PAGE, "", "")
        driver.get(fullUrl)

        # Login IDを入力
        if CNST_LOGIN_ID != "":
            formLoginId = driver.find_element(by=By.XPATH, value=PARAM_XPATH_LOGINID)
            formLoginId.send_keys(CNST_LOGIN_ID)

        # Login Passwordを入力
        formPassword = driver.find_element(by=By.XPATH, value=PARAM_XPATH_LOGINPASSWORD)
        formPassword.send_keys(argPassword)

        # ログインボタンを押下
        loginButton = driver.find_element(by=By.XPATH, value=PARAM_XPATH_LOGINBUTTON)
        loginButton.click()

        # ボタンを押下したのでSleep処理が必要
        time.sleep(argSleepTime)

        # Session ID取得 Start
        if PARAM_NAME_SESSIONID != "":
            elem = driver.find_element(by=By.NAME, value=PARAM_NAME_SESSIONID)
            session_id = elem.get_attribute("value")
        # Session ID取得 End

        # ホスト名の取得 Start
        fullUrl = getFullUrl(urlServer, PARAM_HOST_PAGE, PARAM_NAME_SESSIONID, session_id)
        print(fullUrl)
        driver.get(fullUrl)

        elem = driver.find_element(by=By.XPATH, value=PARAM_XPATH_HOSTNAME)
        hostname = elem.text
        
        if hostname == "":
            print("Failed to get the hostname")
            exit(1)
        # ホスト名の取得 End

        # 出力先フォルダの作成 Start
        if not os.path.exists(PARAM_OUTDIR):
            os.mkdir(PARAM_OUTDIR)

        os.chdir(PARAM_OUTDIR)
        # 出力先フォルダの作成 End

        # HTMLファイルの取得 Start
        for itemPage in PARAM_LST_PAGES:
            # 取得対象HTMLファイルを取得
            fullUrl = getFullUrl(urlServer, itemPage, PARAM_NAME_SESSIONID, session_id)
            driver.get(fullUrl)
            time.sleep(argSleepTime)

            # BeautifulSoupを利用して<body>タグを取得
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            soBody = soup.find(CNST_TARGET_HTMLTAG)

            # URL内のファイル名を取得
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
        for itemPage in PARAM_LST_SCRIPTS:
            # 取得対象スクリプトファイルを取得
            fullUrl = getFullUrl(urlServer, itemPage, "", "")
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
            if PARAM_LOGOUT_PAGE != "":
                urlLogout = getFullUrl(urlServer, PARAM_LOGOUT_PAGE, PARAM_NAME_SESSIONID, session_id)
                print(urlLogout)
                driver.get(urlLogout)
                time.sleep(argSleepTime)

        # Webブラウザの終了処理
        driver.quit()
        print("webdriver is closed")

