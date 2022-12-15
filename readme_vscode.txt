
# Run PowerShell as administrator
Set-ExecutionPolicy RemoteSigned

# Installl python virtual environment
pip install virtualenv

# Make python virtual environment
python -m virtualenv env

# Install modules in (env)
pip install -r requirements.txt

OR

pip install webdriver_manager
pip install pyyaml
pip install bs4
pip install selenium

# debug option 1
Debug panel > BREAKPOINTS
Uncheck "Uncaught Exceptions" not to throw exceptions when "sys.exit(1)"

# debug option 2
Run > Open Configuration
=====
    "configurations": [
        {
            ........
            "justMyCode": true,
            "args" : [
                "192.168.0.1",
                "admin",
                "Password",
                "Nec_AtermWX3000HP.json",
                "NEC",
                "3"
            ]
        }
=====

