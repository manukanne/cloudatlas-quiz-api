import uvicorn
from fastapi import FastAPI

from routers import categories, quizzes, users

# FastAPI entry point, include routes and start server
app = FastAPI()
app.include_router(categories.router)
app.include_router(quizzes.router)
app.include_router(users.router)

if __name__ == "__main__":
    # noinspection PyTypeChecker
    uvicorn.run(app, host="127.0.0.1", port=8000)
