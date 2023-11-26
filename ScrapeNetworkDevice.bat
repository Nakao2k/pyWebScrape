
@echo off
set /p strPassword="対象ネットワーク機器のパスワードを入力してください(Default=%strPassword%)："

@echo on
010_ScrapeNetworkDevice.py 192.168.0.239 "" %strPassword% Netgear_XS512EM.json Netgear 1
:: 010_ScrapeNetworkDevice.py 192.168.0.1 admin %strPassword% Nec_AtermWX3000HP.json NEC 3

pause
