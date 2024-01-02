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
    interests: list = Field(...)

class UpdateUserModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """
    skills: Optional[str] = None
    interests: Optional[list] = None

class UserCollection(BaseModel):
    users: List[UserModel]

@app.post('/users',response_description="Add new user",
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

@app.delete("/users/{id}", response_description="Delete a user")
async def delete_student(id: str):
    try:
        delete_result = await user_collection.delete_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid id format')

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"User {id} not found")


@app.put(
    "/users/{id}",
    response_description="Update a user",
    response_model=UserModel,
    response_model_by_alias=False,
)
async def update_student(id: str, user: UpdateUserModel = Body(...)):
    user = {
        k: v for k, v in user.model_dump(by_alias=True).items() if v is not None
    }

    if len(user) >= 1:
        update_result = await user_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": user},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"User {id} not found")
    if len(user) == 0:
        raise HTTPException(status_code=404, detail=f"Bad request")

    if (existing_user := await user_collection.find_one({"_id": id})) is not None:
        return existing_user
 
    raise HTTPException(status_code=404, detail=f"User {id} not found")