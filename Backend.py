import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pymysql
import json
import re


class create_dict(dict):

    # __init__ function
    def __init__(self):
        self = dict()

    # Function to add key:value
    def add(self, key, value):
        self[key] = value


class backend:

    def __init__(self) -> None:
        self.db = self.connect_database()
        self.mycursor = self.db.cursor()
        self.ratings, self.users, self.lawyers = self.get_values_database()
        self.df = self.prepare_data_frame()

    def connect_database(self):
        try:
            mydb = pymysql.connect(
                host="e-aosc.c22w4tvcurpv.us-west-2.rds.amazonaws.com",
                user="admin",
                password="25tolife",
                database="EAOSC"
            )

            return mydb

        except Exception as err:
            print("Something went wrong: {}".format(err))

    def get_values_database(self):

        ############################# FOR RATING #####################################
        # execute your query
        self.mycursor.execute("SELECT * FROM ratings")

        # fetch all the matching rows
        result = self.mycursor.fetchall()

        # loop through the rows
        user_IDS = []
        lawyer_IDS = []
        user_ratings = []
        for row in result:
            user_IDS.append(row[0])
            lawyer_IDS.append(row[1])
            user_ratings.append(row[2])

        ratings = {'USER_ID': user_IDS,
                   'LAWYER_ID': lawyer_IDS, 'RATING': user_ratings}
        rating_df = pd.DataFrame(ratings)

        ############################# FOR USERS #####################################

        # execute your query
        self.mycursor.execute("SELECT * FROM users")

        # fetch all the matching rows
        result = self.mycursor.fetchall()

        # loop through the rows
        ids = []
        names = []
        emails = []
        numbers = []
        passwords = []
        registered_time = []
        country = []
        city = []

        for row in result:
            ids.append(row[0])
            names.append(row[1])
            emails.append(row[2])
            numbers.append(row[3])
            passwords.append(row[4])
            registered_time.append(row[5])
            country.append(row[6])
            city.append(row[7])

        users = {'USER_ID': ids, 'NAME': names, 'EMAIL': emails, 'NUMBER': numbers,
                 'PASSWORD': passwords, 'REGISTERED_AT': registered_time, 'COUNTRY': country, 'CITY': city}
        users_df = pd.DataFrame(users)

        ############################# FOR LAWYERS #####################################

        # execute your query
        self.mycursor.execute("SELECT * FROM lawyers")

        # fetch all the matching rows
        result = self.mycursor.fetchall()

        # loop through the rows
        ids = []
        names = []
        emails = []
        numbers = []
        passwords = []
        registered_time = []
        country = []
        city = []
        profile_pic = []
        area_of_practice = []
        orders_completed = []

        for row in result:
            ids.append(row[0])
            names.append(row[1])
            emails.append(row[2])
            numbers.append(row[3])
            passwords.append(row[4])
            registered_time.append(row[5])
            country.append(row[6])
            city.append(row[7])
            profile_pic.append(row[8])
            area_of_practice.append(row[9])
            orders_completed.append(row[10])

        lawyers = {'LAWYER_ID': ids, 'NAME': names, 'EMAIL': emails, 'NUMBER': numbers, 'PASSWORD': passwords, 'REGISTERED_AT': registered_time,
                   'COUNTRY': country, 'CITY': city, 'PROFILE_PIC': profile_pic, 'AREA_OF_PRACTICE': area_of_practice, 'ODERS_COMPLETED': orders_completed}
        lawyers_df = pd.DataFrame(lawyers)

        return rating_df, users_df, lawyers_df

    def prepare_data_frame(self):
        ratings_with_names = self.ratings.merge(self.lawyers, on='LAWYER_ID')
        df = ratings_with_names.pivot_table(
            index='LAWYER_ID', columns='USER_ID', values='RATING')
        df.fillna(0, inplace=True)
        return df

    def add_lawyer(self, lawyer_name, lawyer_email, lawyer_phone, lawyer_password, registered_time, country, city, profile_pic, area_of_practice):
        try:
            verification = self.verify(
                lawyer_email, lawyer_phone, lawyer_password, lawyer=True)
            if verification == "True":
                query = "INSERT INTO lawyers (NAME, EMAIL, NUMBER, PASSWORD, REGISTERED_AT,COUNTRY,STATE,PROFILE_PIC,AREA_OF_PRACTICE,ODERS_COMPLETED)  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (lawyer_name, lawyer_email, lawyer_phone,
                          lawyer_password, registered_time, country, city, profile_pic, area_of_practice, 0)
                self.mycursor.execute(query, values)
                self.db.commit()
                return "Lawyer Added Successfully"
            else:
                return verification
        except Exception as err:
            return("Something went wrong: {}".format(err))

    def add_user(self, user_name, user_email, user_phone, user_password, registered_time, country, city):
        try:
            verification = self.verify(
                user_email, user_phone, user_password, user=True)
            if verification == "True":
                query = "INSERT INTO users (NAME, EMAIL, NUMBER, PASSWORD, REGISTERED_AT,COUNTRY,CITY)  VALUES (%s, %s, %s, %s, %s, %s, %s)"
                values = (user_name, user_email, user_phone,
                          user_password, registered_time, country, city)
                self.mycursor.execute(query, values)
                self.db.commit()
                return "User Added Successfully"
            else:
                return verification
        except Exception as err:
            return("Something went wrong: {}".format(err))

    def add_rating(self, user_id, lawyer_id, rating):
        try:
            query = "INSERT INTO ratings (USER_ID, LAWYER_ID, RATING)  VALUES (%s, %s, %s)"
            values = (user_id, lawyer_id, rating)
            self.mycursor.execute(query, values)
            self.db.commit()
            self.cal_avg_rating(lawyer_id)
            return "Rating Added Successfully"
        except Exception as err:
            return("Something went wrong: {}".format(err))

    def delete_lawyer(self, lawyer_id):
        try:
            self.mycursor.execute(
                f"DELETE FROM lawyers WHERE LAWYER_ID = '{lawyer_id}'")
            self.db.commit()
            return "Record Deleted Successfully"
        except Exception as err:
            return("Something went wrong: {}".format(err))

    def delete_user(self, user_id):
        try:
            self.mycursor.execute(
                f"DELETE FROM users WHERE USER_ID = '{user_id}'")
            self.db.commit()
            return "Record Deleted Successfully"
        except Exception as err:
            return("Something went wrong: {}".format(err))

    def delete_rating(self, user_id):
        try:
            self.mycursor.execute(
                f"DELETE FROM rating WHERE USER_ID = '{user_id}'")
            self.db.commit()
            return "Record Deleted Successfully"
        except Exception as err:
            return("Something went wrong: {}".format(err))

    def delete_order(self, order_id):
        try:
            self.mycursor.execute(
                f"DELETE FROM orders WHERE ODER_ID = '{order_id}'")
            self.db.commit()
            return "Record Deleted Successfully"
        except Exception as err:
            return("Something went wrong: {}".format(err))

    def update_user_password(self, user_id, new_password):
        try:
            query = "UPDATE users SET PASSWORD = %s WHERE USER_ID = %s"
            values = (new_password, user_id)
            self.mycursor.execute(query, values)
            self.db.commit()
            return "Password Updated Successfully"
        except Exception as err:
            return("Something went wrong: {}".format(err))

    def update_lawyer_password(self, lawyer_id, new_password):
        try:
            query = "UPDATE lawyers SET PASSWORD = %s WHERE LAWYER_ID = %s"
            values = (new_password, lawyer_id)
            self.mycursor.execute(query, values)
            self.db.commit()
            return "Password Updated Successfully"
        except Exception as err:
            return("Something went wrong: {}".format(err))

    def increment_oders_completed(self, lawyer_id):
        try:
            query = "UPDATE lawyers SET lawyers.ODERS_COMPLETED = lawyers.ODERS_COMPLETED + 1 WHERE lawyers.LAWYER_ID = %s"
            values = (lawyer_id)
            self.mycursor.execute(query, values)
            self.db.commit()
            return "Increment Successfully"
        except Exception as err:
            return("Something went wrong: {}".format(err))

    def get_user(self, user_id):
        try:
            self.mycursor.execute(
                f"SELECT * FROM users WHERE USER_ID = '{user_id}'")
            data = self.mycursor.fetchall()
            mydict = create_dict()
            for row in data:
                mydict.add(row[0], ({"id": row[0], "name": row[1], "email": row[2], "phone": row[3],
                           "password": row[4], "created_at": row[5], "country": row[6], "city": row[7]}))
            #payload = json.dumps(mydict, indent=4)
            return mydict
        except Exception as e:
            return e

    def get_orders(self, user_id):
        try:
            self.mycursor.execute(
                f"SELECT * from ratings where USER_ID='{user_id}'")
            data = self.mycursor.fetchall()
            mydata = []
            for row in data:
                mydata.append(
                    {"user_id": row[0], "lawyer_id": row[1], "Rating": row[2]})
            return mydata
        except Exception as e:
            return e

    def get_user_orders(self, user_id):
        try:
            self.mycursor.execute(
                f"SELECT * from orders where USER_ID='{user_id}' ORDER BY ODER_ID DESC")
            data = self.mycursor.fetchall()
            mydata = []
            for row in data:
                mydata.append({"order_id": row[0], "user_id": row[1], "lawyer_id": row[2],
                              "lawyer_name": row[3], "field": row[4], "status": row[5]})
            return mydata
        except Exception as e:
            return e

    def get_all_users(self):
        try:
            self.mycursor.execute(f"SELECT * FROM users")
            data = self.mycursor.fetchall()
            mylist = []
            for row in data:
                mylist.append({"id": row[0], "name": row[1], "email": row[2], "phone": row[3],
                               "password": row[4], "created_at": row[5], "country": row[6], "city": row[7]})
            #payload = json.dumps(mydict, indent=4)
            return mylist

        except Exception as e:
            return e

    def get_lawyer(self, lawyer_id):
        try:
            self.mycursor.execute(
                f"SELECT * FROM lawyers WHERE LAWYER_ID = '{lawyer_id}'")
            data = self.mycursor.fetchall()
            mydict = create_dict()

            for row in data:
                mydict = {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "password": row[4],
                    "created_at": row[5],
                    "country": row[6],
                    "city": row[7],
                    "profile_picture": row[8],
                    "speciality": row[9],
                    "orders_completed": row[10],
                    "Rating": row[11]
                }
           # payload = json.dumps(mydict, indent=4)
            return mydict
        except Exception as e:
            return e

    def get_all_lawyers(self):
        try:
            self.mycursor.execute(f"SELECT * FROM lawyers")
            data = self.mycursor.fetchall()
            mydict = []
            for row in data:
                mydict.append({"id": row[0], "name": row[1], "email": row[2], "phone": row[3], "password": row[4], "created_at": row[5],
                               "country": row[6], "city": row[7], "profile_picture": row[8], "speciality": row[9], "oders_completed": row[10], "Rating": row[11]})
            #payload = json.dumps(mydict, indent=4)
            return mydict
        except Exception as e:
            return e

    def get_all_orders(self):
        try:
            self.mycursor.execute(f"SELECT * FROM orders")
            data = self.mycursor.fetchall()
            mydict = []
            for row in data:
                mydict.append({"order_id": row[0], "user_id": row[1], "lawyer_id": row[2],
                              "lawyer_name": row[3], "field": row[4], "status": row[5]})
            #payload = json.dumps(mydict, indent=4)
            return mydict
        except Exception as e:
            return e

    def get_lawyers_by_practice(self, speciality):
        try:
            self.mycursor.execute(
                f"SELECT * FROM lawyers WHERE AREA_OF_PRACTICE = '{speciality}'")
            data = self.mycursor.fetchall()
            mydict = create_dict()
            for row in data:
                mydict.add(row[0], ({"id": row[0], "name": row[1], "email": row[2], "phone": row[3], "password": row[4], "created_at": row[5],
                           "country": row[6], "city": row[7], "profile_picture": row[8], "speciality": row[9], "oders_completed": row[10], "Rating": row[11]}))
            #payload = json.dumps(mydict, indent=4)
            return mydict
        except Exception as e:
            return e

    def recommend(self, lawyer_id, similar_score):
        # index fetch
        index = np.where(self.df.index == lawyer_id)[0][0]
        similar_items = sorted(
            list(enumerate(similar_score[index])), key=lambda x: x[1], reverse=True)[1:4]
        items = []
        for i in similar_items:
            items.append(self.get_lawyer(self.df.index[i[0]]))
        return items

    # def KNN_recommend(self, lawyer_id):
    #     lawyer_id = lawyer_id - 1
    #     df_matrix = csr_matrix(self.df.values)
    #     model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    #     model_knn.fit(df_matrix)
    #     distances, indices = model_knn.kneighbors(
    #         self.df.iloc[lawyer_id, :].values.reshape(1, -1), n_neighbors=4)
    #     lawyer_ids = list(indices[0])[1:]
    #     items = []
    #     print(distances, indices)
    #     for id in lawyer_ids:
    #         items.append(self.get_lawyer(id))
    #     return items

    def get_recommendations(self, lawyer_id):
        similar_score = cosine_similarity(self.df)
        return self.recommend(lawyer_id, similar_score)

    def get_average_rating(self, lawyer_id):
        ratings = self.df.T[lawyer_id].tolist()
        count = 0
        total_rating = 0
        for rate in ratings:
            if rate != 0.0:
                total_rating += rate
                count += 1
        avg_rating = total_rating/count
        return avg_rating

    def cal_avg_rating(self, lawyer_id):
        self.mycursor.execute(
            f"UPDATE lawyers SET lawyers.Rating = Round((Select AVG(RATING) from ratings where ratings.LAWYER_ID = lawyers.LAWYER_ID),1) where lawyers.LAWYER_ID={lawyer_id}")
        self.db.commit()

    def verify_password(self, user_email, user_password):
        try:
            self.mycursor.execute(
                f"SELECT USER_ID FROM users WHERE EMAIL = '{user_email}' and PASSWORD = '{user_password}'")
            data = self.mycursor.fetchone()
            if data == None:
                return "No Record Found"
            else:
                return data[0]

        except Exception as e:
            return e

    def get_lawyers_by_rating(self):
        try:
            self.mycursor.execute(
                f"SELECT * FROM lawyers ORDER BY RATING DESC LIMIT 4")
            data = self.mycursor.fetchall()
            mydict = []
            for row in data:
                mydict.append({"id": row[0], "name": row[1], "email": row[2], "phone": row[3], "password": row[4], "created_at": row[5],
                               "country": row[6], "city": row[7], "profile_picture": row[8], "speciality": row[9], "oders_completed": row[10], "Rating": row[11]})

            return mydict
        except Exception as e:
            return e

    def get_highest_rating_lawyer(self, user_id):
        try:
            self.mycursor.execute(
                f"SELECT * FROM ratings WHERE USER_ID = {user_id}")
            data = self.mycursor.fetchall()
            l = sorted(list(data), key=lambda x: x[2])
            l.reverse()
            return l[0][1]

        except Exception as e:
            return e

    def placeOrder(self, user_id, lawyer_id, lawyer_name, field, status):
        try:
            query = "INSERT INTO orders (USER_ID, LAWYER_ID, LAWYER_NAME, AREA_OF_PRACTICE, STATUS)  VALUES (%s, %s, %s, %s, %s)"
            values = (user_id, lawyer_id, lawyer_name, field, status)
            self.mycursor.execute(query, values)
            self.db.commit()
            return "Order Placed"
        except Exception as e:
            return e

    def order_completed(self, order_id):
        try:
            self.mycursor.execute(
                f"UPDATE orders SET orders.STATUS = \'Completed\' where orders.ODER_ID={order_id}")
            self.db.commit()
            return "Order Completed"
        except Exception as e:
            return e

    def search(self, searchstr):
        try:
            searchstr = searchstr.lower()
            self.mycursor.execute(f"SELECT * FROM lawyers")
            data = self.mycursor.fetchall()
            mydict = []
            for row in data:
                if searchstr == row[1].lower() or searchstr == row[6].lower() or searchstr == row[7].lower() or searchstr == row[9].lower():
                    mydict.append({"id": row[0], "name": row[1], "email": row[2], "phone": row[3], "password": row[4], "created_at": row[5],
                                   "country": row[6], "city": row[7], "profile_picture": row[8], "speciality": row[9], "oders_completed": row[10], "Rating": row[11]})
            #payload = json.dumps(mydict, indent=4)
            if len(mydict) > 0:
                return mydict
            return "No Results Found"
        except Exception as e:
            return e

    def verify(self, email, number, password, lawyer=False, user=False):
        try:
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not(re.fullmatch(regex, email)):
                return "Invalid Email"
            elif len(number) < 8 or not(number.isdigit()):
                return "Invalid Phone Number"

            elif len(password) < 8:
                return "Password must be 8 characters long"

            if user:
                self.mycursor.execute(
                    f"SELECT * from users where EMAIL = '{email}' or NUMBER = {number}")
                results = self.mycursor.fetchall()
                if len(results) != 0:
                    return 'This email or number already exist'
                else:
                    return "True"

            elif lawyer:
                self.mycursor.execute(
                    f"SELECT * from lawyers where EMAIL = '{email}' or NUMBER = {number}")
                results = self.mycursor.fetchall()
                if len(results) != 0:
                    return 'This email or number already exist'
                else:
                    return "True"

        except Exception as err:
            return err

    def verify_admin(self, admin_email, admin_password):
        try:
            self.mycursor.execute(
                f"SELECT ADMIN_ID FROM admin WHERE EMAIL = '{admin_email}' and PASSOWRD = '{admin_password}'")
            data = self.mycursor.fetchone()
            if data == None:
                return "No Record Found"
            else:
                return data[0]

        except Exception as e:
            return e
