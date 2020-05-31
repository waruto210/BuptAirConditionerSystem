# BUPT软工大作业
中央空调管控系统
# 运行
注意,先在项目根目录下创建logs目录再运行
```python
pip install -r ./requirements.txt
python manage.py runserver
```
# 目前创建的账号
wmc314@outlook.com
123456
会跳转manager/index.html

dym@outlook.com
123456
会跳转adm/index.html

myc@outlook.com
123456
会跳转director/index.html
# 日志
- 05-14
新增master app，里面保存全局唯一的machine对象，是主机的当前状态集合，准备把以后的调度队列写进去，在adm/views.py下新增了settemp接口，用于管理员设置主机默认参数
对customer页面前端js代码做了些修改
- 05-15
基本完成customer前端逻辑
- 05-17
修缮customer前端逻辑，开始写后端调度
增加了新的项目依赖
APScheduler==3.6.3
django-apscheduler==0.3.0