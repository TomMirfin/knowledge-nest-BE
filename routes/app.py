from datetime import datetime
from typing import Optional, List
from fastapi import Body, HTTPException, status, APIRouter
from fastapi.responses import Response
from pydantic import BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument
from config.database import user_collection, article_collection, review_collection, login_collection

router = APIRouter()

PyObjectId = Annotated[str, BeforeValidator(str)]


# Users
# ------------------------------------------------------------------

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(...)
    token: Optional[str] = None
    skills: Optional[list] = Field([])
    interests: Optional[list] = Field([])
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    img_url: Optional[str] = Field("https://i.imgur.com/z7eiLjV.png")

class UpdateUserModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """
    skills: Optional[list] = None
    interests: Optional[list] = None
    img_url: Optional[str] = None
    bio: Optional[str] = None

class UserCollection(BaseModel):
    users: List[UserModel]

@router.post('/users',response_description="Add new user",
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


@router.get('/users', response_model=UserCollection,
    response_model_by_alias=False,)

async def list_users():
    return UserCollection(users=await user_collection.find().to_list(1000))


@router.get('/users/{id}',response_model=UserModel,
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
    
@router.get('/users/username/{username}',response_model=UserModel,
    response_model_by_alias=False)

async def show_user(username: str):
    try:
        if (user := await user_collection.find_one({"username": username})) is not None:
            return user
        else:
            raise HTTPException(status_code=404, detail='User not found')
    except Exception as err:
        raise HTTPException(status_code=404, detail='User not found')

@router.delete("/users/{id}", response_description="Delete a user")
async def delete_student(id: str):
    try:
        delete_result = await user_collection.delete_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid id format')

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"User {id} not found")


@router.put(
    "/users/{username}",
    response_description="Update a user",
    response_model=UserModel,
    response_model_by_alias=False,
)
async def update_student(username: str, user: UpdateUserModel = Body(...)):
    user = {
        k: v for k, v in user.model_dump(by_alias=True).items() if v is not None
    }

    if len(user) >= 1:
        update_result = await user_collection.find_one_and_update(
            {"username": username},
            {"$set": user},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"User {username} not found")
    if len(user) == 0:
        raise HTTPException(status_code=404, detail=f"Bad request")

    if (existing_user := await user_collection.find_one({"_id": id})) is not None:
        return existing_user
 
    raise HTTPException(status_code=404, detail=f"User {username} not found")

# ------------------------------------------------------------------

# Articles

# ------------------------------------------------------------------


def get_current_timestamp():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def get_current_timestamp_sorting():
    return datetime.now()


class ArticleModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(...)
    title: str = Field(...)
    topic: str = Field(...)
    body: str = Field(...)
    created_at: Optional[str] = Field(default_factory=get_current_timestamp)
    created_at_sorting: Optional[datetime] = Field(default_factory=get_current_timestamp_sorting)

class UpdateArticleModel(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    body: Optional[str] = None

class ArticleCollection(BaseModel):
    articles: List[ArticleModel]

@router.post('/articles',response_description="Add new articles",
    response_model=ArticleModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,)

async def create_article(article: ArticleModel = Body(...)):
    new_article = await article_collection.insert_one(
        article.model_dump(by_alias=True, exclude=['id'])
    )
    created_article = await article_collection.find_one(
        {'_id': new_article.inserted_id}
    )
    return created_article

@router.get('/articles', response_model=ArticleCollection,
    response_model_by_alias=False,)

async def list_articles(sortby: str = "DESC"):
    if sortby == "DESC":
        return ArticleCollection(articles=await article_collection.find().sort("created_at_sorting", -1).to_list(1000))
    elif sortby == "ASC":
        return ArticleCollection(articles=await article_collection.find().sort("created_at_sorting", 1).to_list(1000))
    else:
        raise HTTPException(status_code=400, detail='Invalid param')

@router.get('/articles/{id}',response_model=ArticleModel,
    response_model_by_alias=False)


async def show_article(id: str):
    try:
        article_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail='Invalid id format')


    try:
        if (article := await article_collection.find_one({"_id": ObjectId(id)})) is not None:
            return article
        else:
            raise HTTPException(status_code=404, detail='Article not found')
    except Exception as err:
        raise HTTPException(status_code=404, detail='Article not found')

@router.delete("/articles/{id}", response_description="Delete an article")
async def delete_article(id: str):
    try:
        delete_result = await article_collection.delete_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid article format')

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Article {id} not found")


@router.put(
    "/articles/{id}",
    response_description="Update an article",
    response_model=ArticleModel,
    response_model_by_alias=False,
)
async def update_article(id: str, article: UpdateArticleModel = Body(...)):
    article = {
        k: v for k, v in article.model_dump(by_alias=True).items() if v is not None
    }

    if len(article) >= 1:
        try:
            update_result = await article_collection.find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": article},
                return_document=ReturnDocument.AFTER,
            )
        except:
            raise HTTPException(status_code=404, detail=f"Article id incorrect")
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"article {id} not found")
    if len(article) == 0:
        raise HTTPException(status_code=400, detail=f"Bad request")

    if (existing_article := await article_collection.find_one({"_id": id})) is not None:
        return existing_article
 
    raise HTTPException(status_code=404, detail=f"article {id} not found")

#---------------------------------------------------

class ReviewModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(...)
    title: str = Field(...)
    body: str = Field(...)
    rating: int = Field(None, ge=0, le=5)
    created_at: Optional[str] = Field(default_factory=get_current_timestamp)
    created_at_sorting: Optional[datetime] = Field(default_factory=get_current_timestamp_sorting)

class ReviewCollection(BaseModel):
    reviews: List[ReviewModel]


@router.post('/reviews',response_description="Add new review",
    response_model=ReviewModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,)

async def create_review(review: ReviewModel = Body(...)):
    new_review = await review_collection.insert_one(
        review.model_dump(by_alias=True, exclude=['id'])
    )
    created_review = await review_collection.find_one(
        {'_id': new_review.inserted_id}
    )
    return created_review


@router.get('/reviews', response_model=ReviewCollection,
    response_model_by_alias=False,)



async def list_reviews(sortby: str = "DESC"):
    if sortby == "DESC":
        return ReviewCollection(reviews=await article_collection.find().sort("created_at_sorting", -1).to_list(1000))
    elif sortby == "ASC":
        return ReviewCollection(reviews=await article_collection.find().sort("created_at_sorting", 1).to_list(1000))
    else:
        raise HTTPException(status_code=400, detail='Invalid param')


@router.get('/reviews/{id}',response_model=ReviewModel,
    response_model_by_alias=False)


async def show_review(id: str):
    try:
        review_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail='Invalid id format')


    try:
        if (review := await review_collection.find_one({"_id": ObjectId(id)})) is not None:
            return review
        else:
            raise HTTPException(status_code=404, detail='Review not found')
    except Exception as err:
        raise HTTPException(status_code=404, detail='Review not found')
    

@router.delete("/reviews/{id}", response_description="Delete a review")
async def delete_review(id: str):
    try:
        delete_result = await review_collection.delete_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid id format')

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Review {id} not found")
