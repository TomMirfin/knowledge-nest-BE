from typing import Optional, List
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId
from bson.errors import InvalidId
import motor.motor_asyncio
from pymongo import ReturnDocument
from decouple import config


app = FastAPI()

MONGO_DETAILS = config("MONGO_DETAILS")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client.skillshare

user_collection = db.get_collection("users")

PyObjectId = Annotated[str, BeforeValidator(str)]

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(...)
    skills: str = Field(...)
    interests: str = Field(...)

class UserCollection(BaseModel):
    users: List[UserModel]

@app.post('/user',response_description="Add new user",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,)

async def create_user(user: UserModel = Body(...)):
    new_user = await user_collection.insert_one(
        user.model_dump(by_alias=True, exclude=['id'])
    )
    created_user = await user_collection.find_one(
        {'_id': new_user.inserted_id}
    )
    return created_user


@app.get('/users', response_model=UserCollection,
    response_model_by_alias=False,)

async def list_users():
    return UserCollection(users=await user_collection.find().to_list(1000))


@app.get('/users/{id}',response_model=UserModel,
    response_model_by_alias=False)


async def show_user(id: str):
    try:
        user_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail='Invalid id format')


    try:
        if (user := await user_collection.find_one({"_id": ObjectId(id)})) is not None:
            return user
        else:
            raise HTTPException(status_code=404, detail='User not found')
    except Exception as err:
        raise HTTPException(status_code=404, detail='User not found')
