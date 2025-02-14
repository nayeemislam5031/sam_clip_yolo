from fastapi import FastAPI, Response, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import PIL
from PIL import Image
import aiofiles
from io import BytesIO
import base64
import base64
import cv2
import PIL
from PIL import Image
from io import BytesIO
# import sys
from segmentAnything.segment import *

from detect import run
import os

PWD=os.getcwd() 

print(PWD)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware, 
    allow_credentials=True, 
    allow_origins=origins, 
    allow_methods=["*"], 
    allow_headers=["*"]
)



@app.post("/segmentIMG")
def segment(predicted_iou_threshold: float,
              stability_score_threshold: float,
              clip_threshold: float, query: str,
              file: UploadFile = File(...)
            ):
  mask_generator = load_mask_generator()
  image = file.file.read()
  image = Image.open(BytesIO(image)).save(PWD+"/saved/saved.png")
  image = adjust_image_size(cv2.imread(PWD+"/saved/saved.png"))
  masks = mask_generator.generate(image)
  masks = filter_masks(
        image,
        masks,
        predicted_iou_threshold,
        stability_score_threshold,
        query,
        clip_threshold,
    )
  image = draw_masks(image, masks)
  image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  image = PIL.Image.fromarray(image)

  image.save(PWD+"/segmentationResults/semented_image.png")

    
  buffer = BytesIO()
  image.save(buffer, format="PNG")
  imgstr = base64.b64encode(buffer.getvalue())

  return Response(content=imgstr, media_type="application/json")


@app.post("/yolo5_img")
def yolo5_img(file: UploadFile = File(...)):
    image = file.file.read()
    image = Image.open(BytesIO(image)).save(PWD+"/saved/saved_img.png")
    path = PWD+"/saved/saved_img.png"
    run(source = path)

    image = Image.open(PWD+"/runs/detect/exp/img_result.png")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    imgstr = base64.b64encode(buffer.getvalue())
    return Response(content=imgstr, media_type="application/json")


@app.post("/yolo5_vid")
async def yolo5_vid(file: UploadFile = File(...)):

    async with aiofiles.open(PWD+"/saved/saved_vid.mp4", 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    path = PWD+"/saved/saved_vid.mp4"
    run(source = path)


    return FileResponse(PWD+"/runs/detect/exp2/vid_result.mp4",media_type="video/mp4")
