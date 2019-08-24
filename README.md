# HelloJudge2

## 简介
用于算法竞赛的评测系统。

## 架构
Web端和评测端。
Web端采取前后端分离，前端与后端之间通过AJAX获取数据。

评测采用Celery+Redis作为消息队列，评测端通过消息队列获取评测任务，并通过HTTP上报评测结果。

## 架设
### Web端
#### 前置需求
- Python3.6或者以上版本
- MySQL(可选)
- Redis
- git
#### 部署指南
1. ```git clone https://gitee.com/yutong_java/HelloJudge2```，下载本项目至本地
2. 使用pip安装requirements.txt中的依赖包(```pip3 install -r requirements.txt```)。
3. 将```config_default.py```复制为```config.py```。
4. 参考下一部分修改配置文件
5. 初始化数据库，依次执行```python3.6 manage.py db init```,```python3.6 manage.py db migrate```,```python3.6 manage.py db upgrade```
6. 直接使用```python3.6 run.py```启动或者部署到uWSGI上运行。
#### 配置文件
##### SESSION_KEY
用来加密session的密钥，在第一次运行OJ之前，请填写一个随机滚键盘生成的字符串。
##### DATABASE_URI
数据库URI，如果使用SQLite请填写为```sqlite:///data.db```,其中```data.db```为数据库文件名。

如果使用MySQL，请填写为```mysql+mysqlconnector://username:password@host/database_name```。
##### DEBUG
Flask的调试模式
##### PORT
使用Flask内建服务器时监听端口。
##### HOST
同上，只不过是主机。
##### APP_NAME
站点名称。
##### PASSWORD_SALT
用于在前端加密密码的salt，请脸滚键盘生成一个字符串。

在OJ开始运行后请不要更改，否则所有密码都会失效。
##### USERNAME_REGEX 
所有用户的用户名必须满足这个正则表达式
##### REDIS_URI
Redis的URI。
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


如何添加语言请参考下文。

#### 部署方式
##### Flask内建服务器
不推荐采用，因为没有并发性。

直接运行```python3.6 run.py```即可。

关闭按```Ctrl+C```即可。

##### uWSGI
请把主文件指定为main.py,uWSGI实例指定为web_app。
#### 如何添加语言
在langs中新建```语言ID.py```，其中需要有以下七个字符串常量。


| 常量名 | 意义 | 例 |
| -- | - | -- |
|SOURCE_FILE|源文件名(包括后缀)|{filename}.cpp,{filename}.java等|
|OUTPUT_FILE|目标文件名(包括后缀)|{filename}.out,{filename}.class|
|COMPILE|编译命令行|使用{source}表示源文件,{output}表示目标文件|
|RUN|运行命令行||
#### 其他
评测端部署指南见[https://gitee.com/yutong_java/HelloJudge2-Judger]()