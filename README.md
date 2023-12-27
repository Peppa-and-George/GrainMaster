# GrainMaster
粮油系统后端


## 项目配置
1. 项目默认监听地址：`0.0.0.0`
2. 项目默认监听端口：`8080`

## 部署
### 1）本地部署
+ 安装`python 3.10`
+ 安装依赖
```shell
# 进入项目根目录，运行
pip install -r requirements.txt
# 使用清华源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
+ 启动服务
```shell
# 进入项目根目录，运行
python main.py
```

### 2）Docker部署
+ 安装`Docker`
+ 构建镜像
```shell
# 进入项目根目录，运行
docker bulid -t grain .
```
+ 启动容器
```shell
docker run -d -p 8080:8080 grain
```

