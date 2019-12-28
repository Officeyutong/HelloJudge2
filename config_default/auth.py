# 发信SMTP服务器
SMTP_SERVER = "smtp.qwq.com"
# 发信SMTP服务器端口
SMTP_PORT = 25
# SMTP账号
SMTP_USER = "qwqqwq"
# SMTP密码
SMTP_PASSWORD = "password"
# 发信账号
EMAIL_SENDER = "qwq@qwq.com"
# 重置密码邮件格式
RESET_PASSWORD_EMAIL = "请前往 http://[此处替换为网站地址]/reset_password/{reset_token} 重置密码。此链接仅有效一次。"
# 注册时需要验证邮箱
REQUIRE_REGISTER_AUTH = False
REGISTER_AUTH_EMAIL = "请前往 http://[此处替换为网站地址]/auth_email/{auth_token} 激活账号。此链接仅有效一次。"

# 用以加密验证密钥的密码
# 长度必须得16,24,或者32bytes
AUTH_PASSWORD = b"11223344556677889900aabbccddeeff"
# 验证密钥中的随机token
# 请勿泄露
AUTH_TOKEN = "d2c25808-28b2-11ea-acf5-9cda3efd56be"

# 重置密码邮件过期时间 秒
RESET_PASSWORD_EXPIRE_SECONDS = 30*60

# 注册验证邮箱过期时间 秒
REGISTER_EMAIL_AUTH_EXPIRE_SECONDS = 30*60
