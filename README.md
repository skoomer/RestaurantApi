Create a "Restaurants API" application. Start project using the company’s django-template 
https://git.steelkiwi.com/python/django-template  - see README
 
1. Restaurants must be added by admin (superuser) from admin site
   admin should has a possibility to add fields: name, description, location (geo point), image, status, creation date, email
   admin can add dishes to the restaurant. Each dish must have fields: title, description, cuisine, price
   admin can edit list of cuisines

2. Endpoints for register, login and logout users.
   Provide email + password registration + login. Send email confirmation after registration with a custom template. 
   Provide social networks registration (facebook or google). Save first, last name, email provided by a social network.

3. Endpoint with list of all restaurants with
   Fields: name, description, location, image, had order
   filtering by cuisines, average price + 
   ordering by distance, average price + 
   searching by title and description +
   available for all users (even unauthorized)

4. Endpoint with restaurant detail information
   Fields: name, description, location, image, creation date, number of reviews, number of dishes in menu, average price, had order
   Available for all users

5. Endpoint with menu of a certain restaurant
   list of all available dishes in menu
   add filters by cuisine
   search by title and description
   ordering by price
   available only for logged in users
   Leave a like to a dish
  
6. Endpoint to leave a review about a restaurant
   required fields -  text of an comment
   add possibility to leave anonymous reviews 
   user can delete own review. Send notification to the user after deleted review

7. Endpoint with all reviews for a certain restaurant
   list of all active reviews
   user can see text of the review, author information and creation date. If review is anonymous author must be None

8. Endpoint with user profile
   user can change password
   Change First,  Last Name, avatar
 
9. Orders API for a logged in user
   List of orders with fields: customer name, date, total price, number of dishes, status
   Order details with fields: customer name, address, date, total price, number of orders, status, list of dishes.
   Create an order with fields: list of dishes, address, customer name
   Payments. Complete an order with a payment.
 
10. Admin must has a possibility to:
    See users in the system, restaurants, orders
    All dishes of a restaurant. On the restaurant detail page
    All reviews. On the restaurant detail page. And on separate reviews list page 
    Block inappropriate reviews (one or multiple). Send notification to the user after deleted review (Your review was deleted)
    Send one time email notification to all the customers. 

# Write tests and factories
Add API documentation (Make sure the documentation corresponds with backend serializers)
Use S3 bucket for static and media files
