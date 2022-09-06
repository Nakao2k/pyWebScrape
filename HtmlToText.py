import csv
import os
import re
import sys
from lxml import html


def getOutputFile(argPath, argExt):
    cDir = os.path.dirname(argPath)
    lstSplit = os.path.splitext(os.path.basename(argPath))

    basename = lstSplit[0]

    if len(lstSplit) >= 2:
        ext = lstSplit[1]
    else:
        ext = ""

    if argExt == ext:
        ext += ext
    elif argExt != "":
        ext = argExt

    fullName = cDir + "/" + basename + ext

    return fullName


if __name__ == '__main__':
    # 引数の取得
    args = sys.argv

    # 必須引数の数を確認
    if len(args) <= 2:
        print("引数が足りません")
        exit(1)

    # 必須引数の取得
    argParamTxt = args[1]
    argInDir = args[2]
    argInRegFile = args[3]

    # argParamTxt = "Netgear/Netgear_sysInfo.dat"
    # argInDir = "Netgear"
    # argInRegFile = "^[^_]+_[^_]+_sysInfo\.html$"

    # 設定ファイルの存在チェック
    if not os.path.isfile(argParamTxt):
        print(argParamTxt + " doesn't exist")
        exit(1)

    dictConfig = []

    # 設定ファイルの読込
    with open(argParamTxt, encoding='utf8', newline='') as f:
        csvReader = csv.DictReader(f, delimiter="\t")

        dictConfig = [row for row in csvReader]

    # 1行ずつ取得することができます.
    for row in dictConfig:
        print(row)

    lstTgtFiles = []
    files = os.listdir(argInDir)

    for file in files:
        ma = re.match(argInRegFile, file)

        if ma is None:
            continue

        lstTgtFiles.append(file)

    dictOutput = []

    for file in lstTgtFiles:
        print("Input: " + file)

        with open(argInDir + "/" + file, encoding='utf-8') as f:
            lines = f.read()

        dom = html.fromstring(lines)

        dictRowOutput = {}

        # 1行ずつ取得することができます.
        for row in dictConfig:
            lstElem = dom.xpath(row["xpath"])
            elem = lstElem[0]
            keyAttr = row["attribute"]

            if keyAttr == "text":
                value = elem.text_content()
            else:
                value = elem.attrib.get(keyAttr)

            value = value.strip()

            dictRowOutput[row['name']] = value

        # ファイル名を末列に追加
        dictRowOutput['File'] = file

        dictOutput.append(dictRowOutput)

    # cOutFile = getOutputFile(argParamTxt, ".txt")
    cOutFile = argParamTxt + ".txt"

    print("Output: " + cOutFile)
    with open(cOutFile, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=dictOutput[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(dictOutput)
