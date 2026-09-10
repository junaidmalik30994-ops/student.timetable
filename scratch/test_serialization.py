import unittest
from bson import ObjectId
from app import create_app
from app.utils.db import serialize_mongo

class TestMongoSerialization(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_serialize_mongo_helper(self):
        obj_id = ObjectId()
        doc = {
            '_id': obj_id,
            'name': 'Test Timetable',
            'nested': {
                '_id': ObjectId(),
                'item_id': ObjectId()
            },
            'list_ids': [ObjectId(), ObjectId()]
        }
        serialized = serialize_mongo(doc)
        
        # Verify _id converted to str
        self.assertIsInstance(serialized['_id'], str)
        self.assertEqual(serialized['_id'], str(obj_id))
        
        # Verify nested _id and ObjectId converted to str
        self.assertIsInstance(serialized['nested']['_id'], str)
        self.assertIsInstance(serialized['nested']['item_id'], str)
        
        # Verify list items converted to str
        self.assertIsInstance(serialized['list_ids'][0], str)
        self.assertIsInstance(serialized['list_ids'][1], str)

    def test_admin_timetable_publish_serialization(self):
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 'admin_test_id'
            sess['admin_role'] = 'admin'

        payload = {
            'course': 'B.Tech CS',
            'department': 'Computer Science & Technology',
            'year': '3rd Year',
            'section': 'Section A',
            'weekly_schedule': {
                'Monday': [
                    {'id': 'm1', 'subject': 'Python', 'teacher': 'Prof A', 'type': 'Lecture', 'start': '09:00', 'end': '10:00'}
                ]
            }
        }

        # 1. Test Publish Endpoint
        response = self.client.post('/admin/api/timetable/publish', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('timetable', data)
        self.assertIn('_id', data['timetable'])
        self.assertIsInstance(data['timetable']['_id'], str)

        # 2. Test Save Draft Endpoint
        response_save = self.client.post('/admin/api/timetable/save', json=payload)
        self.assertEqual(response_save.status_code, 200)
        data_save = response_save.get_json()
        self.assertTrue(data_save['success'])
        self.assertIn('_id', data_save['timetable'])
        self.assertIsInstance(data_save['timetable']['_id'], str)

        # 3. Test Load Endpoint
        response_load = self.client.get('/admin/api/timetable/load?course=B.Tech+CS&department=Computer+Science+%26+Technology&year=3rd+Year&section=Section+A')
        self.assertEqual(response_load.status_code, 200)
        data_load = response_load.get_json()
        self.assertTrue(data_load['success'])

if __name__ == '__main__':
    unittest.main()
