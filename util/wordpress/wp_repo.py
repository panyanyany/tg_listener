import hashlib
import logging
from datetime import datetime
from typing import List

from wordpress import API
from beeprint import pp, config, constants

logger = logging.getLogger(__name__)


class WpRepo:
    def __init__(self, endpoint, username, password):
        self.client = API(
            url=endpoint,
            api="wp-json",
            version='wp/v2',
            wp_user=username,
            wp_pass=password,
            consumer_key='',  # settings.get('WP_API_KEY'),
            consumer_secret='',  # settings.get('WP_API_SECRET'),
            basic_auth=True,
            user_auth=True,
        )

    def add_seo_meta(self, post_id, description, keywords):
        response = self.client.post('yoast', data={
            'post_id': post_id,
            'metadesc': description,
            'focuskw': keywords,
        })
        # pp(response.json())

    def create_tag(self, name):
        response = self.client.post('tags', data={
            'name': name
        }, handle_status_codes=[400])
        if response.status_code == 400:
            return response.json()['data']['term_id']
        return response.json()['id']

    def create_category(self, name):
        response = self.client.post('categories', data={
            'name': name
        }, handle_status_codes=[400])
        if response.status_code == 400:
            return response.json()['data']['term_id']
        return response.json()['id']

    def create_user(self, name, username=None):
        username = username or hashlib.sha1(name.encode("utf8")).hexdigest()[:6]
        password = hashlib.sha1((name + str(datetime.now())).encode("utf8")).hexdigest()[:16]

        # print('-' * 20, username)
        response = self.client.get('users/', params={
            'search': username
        }, handle_status_codes=[404], timeout=30)
        users = response.json()
        if users:
            return users[0]['id']

        response = self.client.post('users', data={
            'name': name,
            'username': username,
            'email': username + '@example.com',
            'password': password,
        }, handle_status_codes=[500])
        # pp(response.json())
        return response.json()['id']

    def create_post(self, title, content, excerpt, category_names: List, author, tag_names: List = None):
        """
        https://developer.wordpress.org/rest-api/reference/posts/#create-a-post
        """
        tag_names = tag_names or []
        tags = []
        for name in tag_names:
            tags.append(self.create_tag(name))

        categories = []
        for name in category_names:
            categories.append(self.create_category(name))

        response = self.client.post('posts', data={
            # 不要加 date 否则会变成 schedule
            # 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'title': title,
            'content': content,
            'excerpt': excerpt,
            'tags': tags,
            'status': 'publish',
            'categories': categories,
            'author': author,
        }, handle_status_codes=[400])
        # pp(response.json())
        logger.debug('create post: %s, %s', response.status_code, response.text)
        if response.status_code == 201:
            return response.json()['id']
        return False
