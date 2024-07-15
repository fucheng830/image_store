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

from models import Image, ImageVectorIndex
from database import get_db
from image_caption import image_captioning
from embedding import embeddings

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


@app.get("/{image_url}")
async def replace_image_route(image_url: str, db: Session = Depends(get_db)):
    image = db.query(ImageVectorIndex).filter_by(source_url=image_url).first()
    if image is None:
        ext = extract_extension(image_url)
        if ext:  # 确保扩展名存在
            image_content = await download_image(image_url)
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
                await save_image_to_database(id, image_content, format, image_url, db)

                # 创建图像描述
                caption = image_captioning.generate_caption(image_content)
                image_vector = embeddings.embed_query(caption)
                
                # 创建图像向量索引
                create_vector_index(caption, 
                                    image_vector, 
                                    image_url, 
                                    id,
                                    db)
        else:
            raise HTTPException(status_code=400, detail="Invalid image URL")
    else:
        id = image.id
        image_obj = db.query(Image).filter_by(id=id).first()
        if image_obj is None:
            raise HTTPException(status_code=404, detail="Image not found")
        image_content = image_obj.image_data
        format = image_obj.format
    # Convert the binary data to a file-like object
    file_like = BytesIO(image_content)

    # Determine the MIME type from the format
    mime_type = f"image/{format}"
    # Stream the image back to the client
    # 添加Cache-Control头部
    headers = {
        "Cache-Control": "public, max-age=31536000",  # 例如，这里设置缓存有效期为一年
        "ETag": id  # 使用图片的md5值作为ETag，确保图片更新时缓存也会更新
    }
    return StreamingResponse(file_like, media_type=mime_type, headers=headers)



def create_vector_index(caption, image_vector, image_url, id, db):
    # 图像识别和向量化
    new_index = ImageVectorIndex(
        image_id=id,
        name=caption,
        embedding=image_vector,
        source_url=image_url
    )
    db.add(new_index)
    db.commit()

    
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=9999)

    



   
        


    




