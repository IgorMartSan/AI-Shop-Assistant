from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from colorama import Fore, Style
import os

from db.database import engine, get_db, Base
from db.initializer import initializer_inserts
from routes.coil_router import router as routerCoil
from routes.coil_segment_router import router as routerCoilSegment
from routes.coil_segment_border_router import router as routerCoilSegmentBorder
from routes.coil_segment_annotator_seg_router import router as routerSegmentation
from routes.coil_segment_annotator_bbox_router import router as routerBBoxes
from routes.annotator_router import router as routerAnnotator
from routes.annotator_defect_class_router import router as routerAnnotatorDefectClass
from routes.handle_image_router import router as routerHandleImage
from routes.user_router import router as routerUser, auth_router as routerAuth
from routes.ws import router as routerWS
from routes.cam_router import router as routerCam

Base.metadata.create_all(bind=engine)
get_db()
initializer_inserts()

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
    "http://192.168.15.14:8010",
    "http://192.247.168.43:8010",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    execution_time = end_time - start_time
    log_message = f"Tempo de execução para {request.method} {request.url.path}: {execution_time} segundos"
    print(f"{Fore.BLUE}INFO: {log_message}{Style.RESET_ALL}")
    current_directory = os.getcwd()
    print(f"O diretório relativo do projeto é: {current_directory}")
    return response


@app.get("/")
async def root():
    return {"message": "Bem-vindo ao SISAT - sistema de inspeção de superfície Aperam"}


app.include_router(router=routerCoil)
app.include_router(router=routerCoilSegment)
app.include_router(router=routerCoilSegmentBorder)
app.include_router(router=routerSegmentation)
app.include_router(router=routerBBoxes)
app.include_router(router=routerAnnotator)
app.include_router(router=routerAnnotatorDefectClass)
app.include_router(router=routerWS)
app.include_router(router=routerUser)
app.include_router(router=routerAuth)
app.include_router(router=routerCam)
app.include_router(router=routerHandleImage)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8010, workers=1)
