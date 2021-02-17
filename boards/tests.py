from django.test import TestCase
from django.shortcuts import reverse
from django.urls import resolve
from .views import home, board_topics, new_topic
from boards.models import Board, Topic, Post
from django.contrib.auth.models import User
from boards.forms import NewTopicForm

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

    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse("board_topics", kwargs={'pk':1})
        response = self.client.get(board_topics_url)

        #get the url of home page
        home_url = reverse('home')

        #get the url of new topic button
        new_topic_url = reverse('new_topic', kwargs={'pk':1})

        #check the page contains the above links
        self.assertContains(response, f'href="{home_url}"')
        self.assertContains(response, f'href="{new_topic_url}"')


class NewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')
        User.objects.create_user(username='john', email='john@doe.com', password='123')


    def test_new_topic_view_success_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


    def test_new_topic_view_not_found_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)


    def test_new_topic_url_resolves_new_topic_view(self):
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, new_topic)


    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))


    def test_csrf(self):
        new_topic_url = reverse('new_topic', kwargs={'pk':1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'csrfmiddlewaretoken')


    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': 'Test title',
            'message': 'Lorem ipsum dolor sit amet'
        }
        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_contains_form(self):  # <- new test
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_invalid_post_data(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)


    def test_new_topic_invalid_post_data_empty_fields(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())