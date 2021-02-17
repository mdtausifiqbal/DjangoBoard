from django.test import TestCase
from django.shortcuts import reverse
from django.urls import resolve
from .views import home, board_topics
from boards.models import Board

class HomeTests(TestCase):

    def setUp(self):
        self.board = Board.objects.create(name="Django", description="Django discussion board.")
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEqual(view.func, home)

    def test_home_view_contains_link_to_board_topics_page(self):
        url = reverse('board_topics', kwargs={'pk':self.board.pk})
        self.assertContains(self.response, f'href="{url}"')


class BoardTopicTests(TestCase):

    def setUp(self):
        Board.objects.create(name="Django", description="Django discussion board.")

    def test_board_topics_view_success_status_code(self):
        url = reverse('board_topics', kwargs={'pk':1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        url = reverse('board_topics', kwargs={'pk':99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_board_topics_url_resolved_board_topics_views(self):
        view = resolve('/boards/1')
        self.assertEquals(view.func, board_topics)