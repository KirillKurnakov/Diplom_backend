from authorize import authorizeModule

# import uvicorn
# from fastapi import FastAPI
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
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# for router in all_routers:
#     app.include_router(router)


if __name__ == "__main__":
    password = 'Kirill11'
    print(authorizeModule.hash_func(bytes(password, 'utf-8')))
    # uvicorn.run(
    #     app="main:app",
    #     host="0.0.0.0",
    #     port=7778,
    #     reload=get_variables().reload,
    # )
