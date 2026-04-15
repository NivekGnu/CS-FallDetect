from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/video_feed")
async def video_feed():
    return {"message": "Video feed"}

@app.get("/status")
async def status():
    return {"message": "Status"}