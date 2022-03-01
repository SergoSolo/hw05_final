from django.core.paginator import Paginator


def pages(request, posts, POSTS_NUM):
    paginator = Paginator(posts, POSTS_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def assertequal_test(self, value, expected_value):
    self.assertEqual(value.text, expected_value.text)
    self.assertEqual(value.id, expected_value.id)
    self.assertEqual(value.author.username, expected_value.author.username)
    self.assertEqual(value.group.slug, expected_value.group.slug)
    self.assertEqual(value.group.title, expected_value.group.title)
    self.assertEqual(value.group.description, expected_value.group.description)
    self.assertEqual(value.image, expected_value.image)
