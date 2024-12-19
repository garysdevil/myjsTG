import configparser

def config():
    config = configparser.ConfigParser()
    config.read('gconfig/local.config.ini')

    proxy = {
        'proxy_type': config['proxy']['proxy_type'],  # 'http' or 'socks5'
        'addr': config['proxy']['addr'],  # 代理地址
        'port': int(config['proxy']['port']),             # 代理端口
        'username': config['proxy']['username'], # 代理用户名 (可选)
        'password': config['proxy']['password'], # 代理密码 (可选)
    }
    account = {
        'password': config['account']['password'],
        'oldpassword': config['account']['oldpassword'],
        'session_folder': config['account']['session_folder'],
        'session_new_folder': config['account']['session_new_folder'],
        'key_folder': config['account']['key_folder']
    }
    dev = {
        'api_id': int(config['dev']['api_id']),
        'api_hash': config['dev']['api_hash'],
    }
    test = {
        'phone': config['test']['phone'],
        'code_url': config['test']['code_url'],
        'proxy': config['test']['proxy'],
        'key_path' : config['test']['key_path'],
    }
    return {'proxy': proxy, 'account': account, 'dev': dev, 'test': test}