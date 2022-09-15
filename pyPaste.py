import os
import sys
import pandas as pd

if __name__ == "__main__":
    # 引数の取得
    args = sys.argv

    # 必須引数の数を確認
    if len(args) <= 3:
        print("引数が足りません")
        exit(1)

    # 必須引数の取得
    arg_a_file = args[1]
    arg_b_file = args[2]
    arg_out_file = args[3]

    # arg_a_file = "Netgear_XS512EM_sysInfo.conf.txt"
    # arg_b_file = "Netgear_XS512EM_vlan_pvidsetting.conf.txt"

    # 入力ファイルの存在チェック
    if not os.path.isfile(arg_a_file):
        print(arg_a_file + " doesn't exist")
        exit(1)

    if not os.path.isfile(arg_b_file):
        print(arg_b_file + " doesn't exist")
        exit(1)

    #https://life-freedom888.com/python-csv-ketugou-yoko/
    print("Input: " + arg_a_file)
    df1 = pd.read_csv(arg_a_file, sep='\t')

    print("Input: " + arg_b_file)
    df2 = pd.read_csv(arg_b_file, sep='\t')

    # 入力ファイルを横方向に結合
    df_concat = pd.concat([df1, df2], axis=1)
    #df_concat.to_csv("gousei.csv", index = None)

    # データ内の改行コードを削除
    #df_concat = df_concat.replace('\r', '', regex=True)

    # 出力ファイルに結合結果を出力
    print("Output: " + arg_out_file)
    df_concat.to_csv(arg_out_file, index=None, sep='\t')

    # 標準出力に結合結果を出力
    df_concat.to_csv(sys.stdout, index=None, sep='\t')
    #df1.to_csv(sys.stdout, index=None, sep='\t')

    exit(0)