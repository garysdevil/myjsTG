import configparser


config = configparser.ConfigParser()
config.read('local/config.ini', encoding='utf-8')

account_api_id = config.getint('account','api_id')
account_api_hash = config['account']['api_hash']
account_password = config['account']['password']
account_oldpassword = config['account']['oldpassword']


test_phone = config['test']['phone']
test_code_url = config['test']['code_url']
test_proxy = config['test']['proxy']
test_sessionstr = config['test']['sessionstr']