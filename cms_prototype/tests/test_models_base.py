import os
import unittest

from mongoengine import StringField
from cms_prototype.models.base import VersionedDocument
from cms_prototype.tests.common import TestCase

class SomeTestDocument(VersionedDocument):
    some_key = StringField(max_length=50)

class VersionedDocumentTestCase(TestCase):
    def setUp(self):
        super(VersionedDocumentTestCase, self).setUp()
        self.db = SomeTestDocument._get_collection().database
        self.db.some_test_document.remove()
        self.db.versioned_some_test_document.remove()

    def test_base_fields(self):
        test_doc = SomeTestDocument(some_key='test')

        self.assertEquals(test_doc.id, None)

        test_doc.save()

        self.assertNotEquals(test_doc.id, None)
        self.assertNotEquals(test_doc._rev, None)
        self.assertNotEquals(test_doc._ts, None)
        self.assertEquals(test_doc._parent, None)

    def test_parent_history(self):
        test_doc = SomeTestDocument(some_key='test')
        test_doc.save()
        previous_rev = test_doc._rev
        test_doc.save()
        self.assertNotEquals(test_doc._rev, previous_rev)
        self.assertEquals(test_doc._parent, previous_rev)

    def test_single_revision(self):
        test_doc = SomeTestDocument(some_key='test value')
        test_doc.save()

        self.assertEqual(self.db.some_test_document.find().count(), 1)
        self.assertEqual(self.db.some_test_document.find({'_id': test_doc.id}).count(), 1)
        self.assertEqual(self.db.versioned_some_test_document.find().count(), 1)
        self.assertEqual(self.db.versioned_some_test_document.find({'_id.id': test_doc.id}).count(), 1)

    def test_double_revision(self):
    	test_doc = SomeTestDocument(some_key='test value')
        test_doc.save()
        test_doc.some_key = 'some other value'
        test_doc.save()

        self.assertEqual(self.db.some_test_document.find().count(), 1)
        self.assertEqual(self.db.some_test_document.find({'_id': test_doc.id}).count(), 1)
        self.assertEqual(self.db.versioned_some_test_document.find().count(), 2)
        self.assertEqual(self.db.versioned_some_test_document.find({'_id.id': test_doc.id}).count(), 2)

    def test_compound_key_revision(self):
    	from cms_prototype.models.site import Site, Url, UrlKey

    	site = Site(name='@UK', unique_name='uk-plc')
    	site.save()

    	url = Url(key=UrlKey(url='/index.html', site=site))
    	url.save()
