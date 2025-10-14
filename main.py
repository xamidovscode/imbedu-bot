from fastapi import FastAPI

app = FastAPI(
    title="My FastAPI App",
    description="Oddiy FastAPI loyihasi",
    version="1.0.0",
)

@app.get("/")
async def root():
    return {"message": "FastAPI loyihasi ishlayapti 🚀"}

@app.get("/hello/{name}")
async def hello(name: str):
    return {"message": f"Salom, {name}!"}
