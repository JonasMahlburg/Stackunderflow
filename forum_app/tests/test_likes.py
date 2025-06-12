from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from forum_app.models import Question, Like


class LikeTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user= self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION= 'Token ' + self.token.key)
   
    def create_question(self):
        return Question.objects.create(
            title='Testfrage',
            content='Testinhalt',
            author=self.user,
            category='frontend'
        )

    def post_like(self, question):
        url = reverse('like-list')
        data = {'question': question.id}
        return self.client.post(url, data, format='json')
    
    def test_get_like(self):
        url = reverse('like-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_is_created(self):
        question = self.create_question()
        response = self.post_like(question)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        like = Like.objects.first()
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.question, question)

    def test_like_already_exists(self):
        question = self.create_question()
        Like.objects.create(user=self.user, question=question)
        response = self.post_like(question)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_like_delete(self):
        question = self.create_question()
        like = Like.objects.create(user=self.user, question=question)

        url = reverse('like-detail', kwargs={'pk': like.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Like.objects.count(), 0)
