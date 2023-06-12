import factory
from django.test import TestCase
from django.urls import reverse
from apps.restaurants.factories import (
    RestaurantFactory,
    ReviewFactory,
)
from apps.accounts.factories import UserFactory


class TestReviewRestaurant(TestCase):
    """unittest restaurant review"""

    def setUp(self):

        self.restaurant1 = RestaurantFactory()
        self.review = ReviewFactory
        self.url_restaurants = reverse(
            "restaurants:restaurant-review-list", args=[self.restaurant1.pk]
        )
        self.data_login = {
            "email": "testgmail@mail.com",
            "password": "password1245",
        }
        self.user = UserFactory(
            email=self.data_login["email"],
            password=factory.PostGenerationMethodCall(
                "set_password", self.data_login["password"]
            ),
        )
        self.user_login = self.client.login(
            username=self.data_login["email"], password=self.data_login["password"]
        )

    def test_get_restaurant_reviews(self):
        self.review.create_batch(
            reviewer=self.user, restaurant=self.restaurant1, size=3
        )
        response = self.client.get(self.url_restaurants)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)

    def test_post_review_to_restaurant(self):
        data_review = {"message": "test message post"}
        response = self.client.post(self.url_restaurants, data_review)
        self.assertEqual(response.status_code, 201)

        response = self.client.get(self.url_restaurants)
        self.assertEqual(response.data["results"][0]["message"], data_review["message"])
