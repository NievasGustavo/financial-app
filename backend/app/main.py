from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routes import user_routes, auth_routes


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)
app.include_router(auth_routes.router)

@app.get("/")
async def root(request: Request):
    base_url = request.base_url
    return {"message": f"Docs available at {base_url}docs or {base_url}redoc 🚀"}
