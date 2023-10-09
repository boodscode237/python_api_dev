from typing import Optional
from fastapi import Body, FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class PostModel(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapidb",
            user="postgres",
            password="Ngoabel1",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connection was successfull")
        break
    except Exception as e:
        print("Connection failed this is the error")
        print(f"{e}")
        time.sleep(2)

my_posts = [
    {
        "title": "title of post 1",
        "content": "content of post 1",
        "published": True,
        "rating": 2,
        "id": 1,
    },
    {
        "title": "title of post 2",
        "content": "content of post 2",
        "published": True,
        "rating": 5,
        "id": 2,
    },
]


@app.get("/")
async def read_root():
    return {"Hello": "Welcome to FastAPI"}


@app.get("/posts")
async def get_posts():
    cursor.execute("""select * from posts""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: PostModel):
    cursor.execute(
        """insert into posts (title, content, published) values(%s, %s, %s) returning *""",
        (post.title, post.content, post.published),
    )
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""select * from posts where id=%s""", (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No post found with id {id}",
        )
    return {"post_detiail": f"Here is post {post}"}


def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post


def find_index_post(id):
    for index, post in enumerate(my_posts):
        if post["id"] == id:
            return index


# title str, content str, category, Boolean,


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("DELETE FROM posts WHERE id=%s returning *", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No post found with id {id}"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: PostModel):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, id),
    )
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No post found with id {id}"
        )
    return {"data": updated_post}
