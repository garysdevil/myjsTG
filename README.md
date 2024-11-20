# Telegram
```sh
# 更改配置文件
cp config/config.ini config/local.config.ini

# 添加TG账号数据
mkdir local
vi local/data.txt

# 保存TG账号的key
python login.py --start-line 1 --end-line 1 --data-file local/data.txt --key-folder local/keys
```


# 报错
## opentele
```log
telethon.errors.rpcerrorlist.AuthKeyUnregisteredError: The key is not registered in the system (caused by GetAuthorizationsRequest)
```
- 这个错误一般是因为账号不存在。（被封了）