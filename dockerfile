# 使用官方Python基础镜像
FROM python:3.9

# 设置工作目录为/code
WORKDIR /code

#复制模型文件

# 将requirements.txt文件复制到容器中
COPY requirements.txt .

# 安装requirements.txt中的依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码到容器中
COPY . .

COPY /home/ubuntu/data/model_data/blip-image-captioning-base .
COPY /home/ubuntu/data/model_data/m3e-base .
# 启动命令
CMD ["uvicorn", "image_processor:app", "--host", "0.0.0.0", "--port", "9999"]