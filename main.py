from datetime import date
from fastapi import FastAPI
from Backend import backend
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union


class VerifyUser(BaseModel):
    email: str
    password: str


class VerifyAdmin(BaseModel):
    email: str
    password: str


class User(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    country: str
    city: str


class Lawyer(BaseModel):
    name: str
    email: str
    contact_no: str
    password: str
    country: str
    city: str
    area_of_practice: str


class Order(BaseModel):
    user_id: int
    lawyer_id: int
    lawyer_name: str
    field: str
    status: Union[str, None] = None


class Rating(BaseModel):
    user_id: int
    lawyer_id: int
    rating: int


app = FastAPI()
connection = backend()

##################### GET ####################
origins = [
    "http://localhost:3000",
    "https://e-aosc.herokuapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return "Waiting for the query"


@app.get("/user/{user_id}")
async def get_user(user_id: int):
    return connection.get_user(user_id)


@app.post('/verify/')
async def verify_user(verifyuser: VerifyUser):
    return connection.verify_password(verifyuser.email, verifyuser.password)


@app.post('/verify_admin/')
async def verify_admin(VerifyAdmin: VerifyAdmin):
    return connection.verify_admin(VerifyAdmin.email, VerifyAdmin.password)


@app.get("/lawyer/{lawyer_id}")
async def get_lawyer(lawyer_id: int):
    return connection.get_lawyer((lawyer_id))


@app.get("/all_users")
async def get_all_users():
    return connection.get_all_users()


@app.get("/orders/{user_id}")
async def get_user_orders(user_id: int):
    return connection.get_orders(user_id)

@app.get("/orders")
async def get_all_orders():
    return connection.get_all_orders()


@app.get("/user-orders/{user_id}")
async def get_orders_users(user_id: int):
    return connection.get_user_orders(user_id)


@app.get("/order_completed/{order_id}")
async def order_completed(order_id: int):
    return connection.order_completed(order_id)


@app.get("/all_lawyers")
async def get_all_lawyers():
    return connection.get_all_lawyers()


@app.get("/lawyers/speciality/{area_of_practice}")
async def get_lawyers_by_practice(area_of_practice):
    return connection.get_lawyers_by_practice(area_of_practice)


@app.get("/lawyers/rating/")
async def get_lawyers_by_rating():
    return connection.get_lawyers_by_rating()


@app.get('/inc_orders/{lawyer_id}')
async def increment_order(lawyer_id: int):
    return connection.increment_oders_completed(lawyer_id)


# @app.get("/recommend/{lawyer_id}")
# async def fetch_recommendation(lawyer_id: int):
#     return connection.get_recommendations(lawyer_id)


@app.get("/highest_rated/{user_id}")
async def get_highest_rated_lawyer(user_id: int):
    lawyer_id = connection.get_highest_rating_lawyer(user_id)
    if str(lawyer_id).isnumeric():
        return connection.KNN_recommend(lawyer_id)
    return "No Recomendations Found"


@app.get("/search/{searchstr}")
async def search(searchstr: str):
    return connection.search(searchstr)


@app.get('/recommend/{lawyer_id}')
async def KNN_recommend(lawyer_id: int):
    return connection.KNN_recommend(lawyer_id)

################ POST ########################


@app.post("/new_user/")
async def insert_user(user: User):
    today = date.today()
    registered_at = today.strftime('%Y-%m-%d %H:%M:%S')
    return connection.add_user(user.name, user.email, user.phone, user.password, registered_at, user.country, user.city)


@app.post("/new_lawyer/")
async def insert_lawyer(lawyer: Lawyer):
    today = date.today()
    registered_at = today.strftime('%Y-%m-%d %H:%M:%S')
    profile_pic = 'https://st3.depositphotos.com/6672868/13701/v/600/depositphotos_137014128-stock-illustration-user-profile-icon.jpg'
    return connection.add_lawyer(lawyer.name, lawyer.email, lawyer.contact_no, lawyer.password, registered_at, lawyer.country, lawyer.city, profile_pic, lawyer.area_of_practice)


@app.post("/place_order/")
async def place_order(order: Order):
    status = "pending"
    return connection.placeOrder(order.user_id, order.lawyer_id, order.lawyer_name, order.field, status)


@app.post("/add_rating/")
async def insert_rating(user_rating: Rating):
    return connection.add_rating(user_rating.user_id, user_rating.lawyer_id, user_rating.rating)


################# UPDATE ###########################


@app.get("/update_user_password/")
async def update_user_password(user_id: int, password: str):
    return connection.update_user_password(user_id, password)


@app.get("/update_lawyer_password/")
async def update_lawyer_password(lawyer_id: int, password: str):
    return connection.update_lawyer_password(lawyer_id, password)

############## DELETE ######################


@app.get('/delete_user/{user_id}')
async def delete_user(user_id: int):
    return connection.delete_user(user_id)


@app.get('/delete_lawyer/{lawyer_id}')
async def delete_lawyer(lawyer_id: int):
    return connection.delete_lawyer(lawyer_id)


@app.get('/delete_rating/{user_id}')
async def delete_rating(user_id: int):
    return connection.delete_rating(user_id)

@app.get('/delete_order/{order_id}')
async def delete_order(order_id: int):
    return connection.delete_order(order_id)
