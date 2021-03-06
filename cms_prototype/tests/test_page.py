from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from cms_prototype.tests.common import TestCase
from cms_prototype.models.site import Site, Page, UrlKey, Url


class PageloadTest(TestCase):

    def setUp(self):
        super(PageloadTest, self).setUp()
        self.config = testing.setUp()
        self.db = Site._get_collection().database

        self.db.site.remove()
        self.db.versioned_site.remove()
        self.db.page.remove()
        self.db.versioned_page.remove()
        self.db.url.remove()
        self.db.versioned_url.remove()

        site = Site(name='test', unique_name='test')
        site.save()
        page = Page()
        page.save()
        urlKey = UrlKey(site=site, url='index.html')
        url = Url(key=urlKey, page=page)
        url.save()

        from cms_prototype import main
        app = main()

    def test_missing_project(self):
        from cms_prototype.views.page import page

        request = testing.DummyRequest(matchdict={'unique_name': 'somerandomprojectthatdoesnotexist'})

        with self.assertRaises(HTTPNotFound):
            page(request)

    def test_missing_page(self):
        from cms_prototype.views.page import page
        request = testing.DummyRequest(matchdict={'unique_name': 'test', 'url': 'somerandompagethatdoesnotexist.html'})

        with self.assertRaises(HTTPNotFound):
            page(request)

    def test_page_load(self):
        from cms_prototype.views.page import page
        request = testing.DummyRequest(matchdict={'unique_name': 'test', 'url': 'index.html'})
        response = page(request)

        self.assertEquals(response.status_code, 200)
