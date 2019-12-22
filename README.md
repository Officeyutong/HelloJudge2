# HelloJudge2

## 简介
用于算法竞赛的评测系统。

## 架构
Web端和评测端。
Web端采取前后端分离，前端与后端之间通过AJAX获取数据。

评测采用Celery+Redis作为消息队列，评测端通过消息队列获取评测任务，并通过HTTP上报评测结果。
## 更新方式
在项目根目录下，直接执行```git pull```进行更新。

## 关于数据库
从2019.11.2开始，所有更新不再需要手动修改数据库。

每次更新后执行```python3.7 manage.py db upgrade```即可。

## 架设
### Web端
#### 前置需求
- Python3.7或者以上版本
- MySQL(可选)
- Redis
- git
#### 部署指南
1. ```git clone https://gitee.com/yutong_java/HelloJudge2```，下载本项目至本地
2. 使用pip安装requirements.txt中的依赖包(```pip3 install -r requirements.txt```)。
3. 将```config.sample.py```重命名为```config.py```
4. 修改config.py
5. 初始化数据库，参考下文
6. 直接使用```python3.7 run.py```启动或者部署到uWSGI上运行。
#### 初始化数据库

1. 运行```python3.7 manage.py db upgrade```

#### 配置文件主要内容

见```config.sample.py```。

##### SESSION_KEY
用来加密session的密钥，在第一次运行OJ之前，请填写一个随机滚键盘生成的字符串。
##### DATABASE_URI
数据库URI，如果使用SQLite请填写为```sqlite:///data.db```,其中```data.db```为数据库文件名。

如果使用MySQL，请填写为```mysql+mysqlconnector://username:password@host:port/database_name```。
##### DEBUG
Flask的调试模式
##### APP_NAME
站点名称。
##### PASSWORD_SALT
用于在前端加密密码的salt，请脸滚键盘生成一个字符串。

在OJ开始运行后请不要更改，否则所有数据库中的密码都会失效。
##### USERNAME_REGEX 
新建用户的用户名必须满足这个正则表达式
##### REDIS_URI
Redis的地址(用于评测队列)
##### CACHE_URL
Redis的地址(用于缓存) 
##### REMOTE_JUDGE_BROKER
Redis 的地址(用于远程评测队列)

如果不想在同一个评测机实例上同时进行远程评测和本地评测，请务必保证此项不与REDIS_URI相同。
##### JUDGERS
Web端认可的评测机列表。

每一个评测机都应该有一个唯一的UUID，Web端有这个评测机的UUID时，评测机才可以接到Web端发出的评测任务。
```python
{
    "一个评测机的UUID":"这个评测机在前端显示的名字"
}
```
##### PROBLEMS_PER_PAGE
每页显示的题目数量。
##### SUBMISSIONS_PER_PAGE
每页显示的提交记录数量。
##### DISCUSSION_PER_PAGE
每页显示的讨论数量。
##### COMMENTS_PER_PAGE
每页显示的评论数量。
##### COMPILE_TIME_LIMIT
编译程序的时间上限(ms)。
##### COMPILE_RESULT_LENGTH_LIMIT
发送给前端的编译结果的大小上限(bytes)
##### SPJ_EXECUTE_TIME_LIMIT
SPJ的执行时间上限(ms)

其他配置说明见```config_default.py```

如何添加语言请参考下文。

#### 运行方式
##### Flask内建服务器
直接运行```python3.7 run.py```即可。

##### uWSGI\Gunicorn   
先咕着

#### 如何添加语言
在langs中新建```语言ID.py```，其中需要有以下七个字符串常量。


| 常量名 | 意义 | 例 |
| -- | - | -- |
|SOURCE_FILE|源文件名(包括后缀)|{filename}.cpp,{filename}.java等|
|OUTPUT_FILE|目标文件名(包括后缀)|{filename}.out,{filename}.class|
|COMPILE|编译命令行|使用{source}表示源文件,{output}表示目标文件|
|RUN|运行命令行||
|DISPLAY|语言显示名|C++ 17|
|VERSION|版本|G++ 8.3|
|ACE_MODE|用于ACE.js的代码样式，见static/ace/mode-xxx.js|c_cpp|
#### 其他
评测端部署指南见[https://gitee.com/yutong_java/HelloJudge2-Judger](https://gitee.com/yutong_java/HelloJudge2-Judger)

## 权限管理


使用manage.py进行部分权限管理(用户添加\删除权限，设置管理员).

- setadmin 用户名 - 设置管理员 (将用户移动到admin组并添加permission.manage权限,然后刷新缓存)
- addperm 用户名 权限字符串 - 用户添加权限(会刷新缓存)
- removeperm 用户名 权限字符串 - 用户删除权限(会刷新缓存)

## 代码行数统计(已忽略static文件夹)
```plain
     163 text files.
     144 unique files.
      64 files ignored.

github.com/AlDanial/cloc v 1.74  T=7.03 s (14.5 files/s, 1688.3 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
HTML                            29            217             33           5180
Python                          63            556           1573           3569
Markdown                         3            134              0            434
C++                              2              4              2             59
INI                              2             11              0             42
Mako                             2             14              0             36
JSON                             1              0              0              3
-------------------------------------------------------------------------------
SUM:                           102            936           1608           9323
-------------------------------------------------------------------------------
```
## TodoList
- RemoteJudge
- 题目集
- 新的统一上传文件API


## 捐助
如果您觉得此项目对您有帮助，欢迎通过以下方式对作者进行捐助。

![](images/alipay.jpg)

如果您在捐助时注明了您的姓名，那么您将会出现在下面的列表上。
- 2019.10.20 黑白棋子 微信 0.01
- 2019.10.20 Crystal 微信 5.20

