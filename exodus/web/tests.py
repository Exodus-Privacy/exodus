from django.test import TestCase


class NextPageTests(TestCase):

    def test_next_page_lists_framalibre_among_alternatives(self):
        response = self.client.get('/en/info/next/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://framalibre.org/')
