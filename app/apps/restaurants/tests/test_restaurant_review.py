import factory
from django.test import TestCase
from django.urls import reverse
from apps.restaurants.factories import (
    RestaurantFactory,
    ReviewFactory,
)
from apps.accounts.factories import UserFactory
from apps.restaurants.models import Review
from django.core import mail


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

    def test_get_restaurant_reviews(self):
        self.review.create_batch(
            reviewer=self.user, restaurant=self.restaurant1, size=3
        )
        response = self.client.get(self.url_restaurants)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["results"][0]["message"], self.review.message)
        self.assertEqual(
            response.data["results"][0]["reviewer"]["email"], self.user.email
        )

    def test_post_review_to_restaurant(self):
        self.client.force_login(self.user)
        data_review = {"message": "test message post"}
        response = self.client.post(self.url_restaurants, data_review)
        self.assertEqual(response.status_code, 201)

        response = self.client.get(self.url_restaurants)
        self.assertEqual(response.data["results"][0]["message"], data_review["message"])

    def test_destroy_with_owner(self):
        self.client.force_login(self.user)
        review = ReviewFactory(restaurant=self.restaurant1, reviewer=self.user)

        del_url = reverse(
            "restaurants:restaurant-review-detail",
            args=[self.restaurant1.pk, review.pk],
        )

        response = self.client.delete(del_url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

        # Check if an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Your review has been deleted")
        self.assertEqual(
            mail.outbox[0].body,
            f"Your review message test of {self.restaurant1.title} has been deleted.",
        )
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_check_destroy_permission_user(self):
        review = ReviewFactory(restaurant=self.restaurant1, reviewer=self.user)

        del_url = reverse(
            "restaurants:restaurant-review-detail",
            args=[self.restaurant1.pk, review.pk],
        )

        response = self.client.delete(del_url)

        self.assertEqual(response.status_code, 403)
