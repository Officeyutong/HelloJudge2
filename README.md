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
- Python3.7或者以上版本
- MySQL(可选)
- Redis
- git
#### 部署指南
1. ```git clone https://gitee.com/yutong_java/HelloJudge2```，下载本项目至本地
2. 使用pip安装requirements.txt中的依赖包(```pip3 install -r requirements.txt```)。
3. 将```config_default.py```复制为```config.py```。
4. 修改config.py
5. 初始化数据库，参考下文
6. 直接使用```python3.7 run.py```启动或者部署到uWSGI上运行。
#### 初始化数据库
1. 运行```python3.7 manage.py db init```
2. 进入```migrations/script.py.mako```,在```import sqlalchemy as sa```的下一行写上```import ormtypes```
3. 运行```python3.7 manage.py db migrate```,```python3.7 manage.py db upgrade```
#### 配置文件
配置文件内容见config_default.py

如何添加语言请参考下文。

#### 运行方式
##### Flask内建服务器
直接运行```python3.7 run.py```即可。

##### uWSGI
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