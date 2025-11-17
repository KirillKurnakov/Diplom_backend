import uvicorn
from starlette.middleware.cors import CORSMiddleware
from authorize import authorizeModule
from db import querytable
from fastapi import FastAPI
from authorize.authorizeModule import router as authorize_router
from db.querytable import router as querytable_router

from flask import Flask

app = FastAPI()

# from fastapi.middleware.cors import CORSMiddleware
#
# from api import all_routers
# from loaded_env import get_variables
#
# app = FastAPI(
#     title=get_variables().app_name,
#     summary=get_variables().app_description,
# )
#
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#
# for router in all_routers:
#     app.include_router(router)

app.include_router(authorize_router)
app.include_router(querytable_router)

if __name__ == "__main__":
    authorizeModule.check_user_pass('Kurnakov', '123')


    #password = 'Kirill11'
    #print(authorizeModule.hash_func(bytes(password, 'utf-8')))

    # запуск сервера
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=7778,
        #reload=get_variables().reload,
    )
