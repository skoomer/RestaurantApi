# import time
# import environ

# env = environ.Env(
#     # set casting, default value
#     DEBUG=(bool, False)
# )
# # reading .env file
# environ.Env.read_env()
# from app.doctorweb.config import settings
# from locust import HttpUser, task, between


# class DoctorLocust(HttpUser):
#     """ "testing doctor with locust"""

#     wait_time = between(1, 5)
#     login_token = ""

#     def on_start(self):
#         self.login()

#     def login(self):
#         response = self.client.get("/accounts/login/")

#         csrftoken = response.cookies.get_dict()["csrftoken"]
#         self.login_token = csrftoken

#         response = self.client.post(
#             "/accounts/login/",
#             {
#                 "username": settings.LOCUST_PROFILE,
#                 "password": settings.LOCUST_PASSWORD,
#                 "csrfmiddlewaretoken": csrftoken,
#             },
#         )

#     @task(4)
#     def create_appoint(self):

#         resp = self.client.get("/appoint/")
#         token = resp.cookies.get_dict()["csrftoken"]
#         data = {
#             "patient_full_name": "Test",
#             "doctor": "13",
#             "arrival_date": "2022-07-04 15:00:00",
#             "reason": "ahah",
#             "user": "8",
#             "csrfmiddlewaretoken": token,
#         }

#         self.client.post("/appoint/", data)

#         time.sleep(1)

#     @task
#     def search_doctor(self):
#         self.client.get("/doctors/?doctor_search=g")
