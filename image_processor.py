import base64
import hashlib
import io
import re
from PIL import Image as PILImage
from sqlalchemy.orm import Session
from urllib.parse import urlparse, parse_qs
import httpx
import os 

from fastapi import FastAPI, Depends
from fastapi import HTTPException
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from io import BytesIO
from fastapi.responses import StreamingResponse

from models import Image
from database import get_db

app = FastAPI()

# 定义schema
from pydantic import BaseModel
from load_env import *

class ImageSchema(BaseModel):
    url: str
    # 可选参数
    title: Optional[str] = None

BASE_URL = os.getenv('SERVER_ROOT_URL', 'http://localhost:9999')


def image_to_base64(image_content, ext):
    # 将图片内容转换为Base64编码
    return 'data:image/{};base64,{}'.format(ext, base64.b64encode(image_content).decode())


def extract_extension(url):
    # 解析URL并提取查询参数
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # 检查是否存在'wx_fmt'查询参数，并获取它的值
    fmt = query_params.get('wx_fmt')
    if fmt and fmt!='svg':
        ext = fmt[0]
        # 返回相应的扩展名，确保它以'.'开头
        return f'.{ext}' if not ext.startswith('.') else ext

    # 如果没有找到'wx_fmt'参数或值为空，则尝试从路径中提取扩展名
    match = re.search(r'\.(jpg|jpeg|png|gif|svg)$', parsed_url.path, re.IGNORECASE)
    if match:
        return match.group(0).lower()
    
    # 如果仍然无法确定扩展名，返回默认值
    return '.jpg'


async def download_image(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.content
    return None


async def save_image_to_database(id, content, format, url, db):
    result = db.query(Image).filter_by(id=id).first()
    if not result:
        new_image = Image(
            id=id,
            image_data=content,
            format=format,
            source_url=url,
        )
        db.add(new_image)
        db.commit()
    return True


@app.get("/image/{image_name}")
async def get_image(image_name: str, db: Session = Depends(get_db)):
    id, format = image_name.split(".")

    image = db.query(Image).filter_by(id=id).first()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    # Convert the binary data to a file-like object
    file_like = BytesIO(image.image_data)

    # Determine the MIME type from the format
    mime_type = f"image/{image.format.lower()}"
    # Stream the image back to the client
    # 添加Cache-Control头部
    headers = {
        "Cache-Control": "public, max-age=31536000",  # 例如，这里设置缓存有效期为一年
        "ETag": id  # 使用图片的md5值作为ETag，确保图片更新时缓存也会更新
    }
    return StreamingResponse(file_like, media_type=mime_type, headers=headers)



@app.post("/replace_image")
async def replace_image_route(background_tasks: BackgroundTasks, image: ImageSchema, db: Session = Depends(get_db)):
    url = image.url
    ext = extract_extension(url)
    if ext:  # 确保扩展名存在
        image_content = await download_image(url)
        if image_content:
            # 准备上传图像并保存到数据库
            image_content_file = io.BytesIO(image_content)
            md5_hash = hashlib.md5()
            md5_hash.update(image_content)
            id = md5_hash.hexdigest()
            try:
                image_format = PILImage.open(image_content_file).format
            except IOError:
                raise HTTPException(status_code=400, detail="Unable to open image file")

            format = image_format.lower()
            # 保存图像到数据库
            await save_image_to_database(id, image_content, format, url, db)
            # 将创建向量索引的函数添加到后台任务
            # background_tasks.add_task(create_vector_index, image_content)
            
            # 返回新图像的URL
            new_url = f'{BASE_URL}/image/{id}.{format}'
            return new_url
    else:
        raise HTTPException(status_code=400, detail=f"Could not determine the image extension for {url}")

async def create_vector_index(image_content):
    # 图像识别和向量化
    pass

    
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=9999)

    



   
        


    




