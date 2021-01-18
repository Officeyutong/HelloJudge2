# 迁移指南

2021年1月12日，HJ2发生了大规模重构以至于不兼容旧版数据库，请参考此指南将数据库迁移至新版。

## 步骤

- 为新的版本初始化一个新的数据库，并修改```config.py```中的数据库URI为新建的数据库。
- 复制```migrate_config.sample.py```为```migrate_config.py```，并按照其中的指示修改内容
- 运行```migrate.py```
- 运行```python3 manage.py recache_allproblems```