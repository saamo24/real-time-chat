from fastapi import FastAPI, Depends
from .auth import auth_router
from .db import Base, engine
from fastapi_jwt_auth import AuthJWT

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/hello")
def hello(Authorize: AuthJWT = Depends()):

    try:
        # Require JWT token
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        return {"message": f"Hello {current_user}!"}
    except Exception as e:
        return {"detail": str(e)}, 401
    

app.include_router(auth_router, prefix="/api")

