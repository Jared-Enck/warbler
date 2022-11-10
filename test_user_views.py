import os
from unittest import TestCase

from models import db, User, Message

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY
from test_user_model import generate_user


db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):
    """Test User view routes"""
    
    def setUp(self):
        
        User.query.delete()
        Message.query.delete()
        
        self.client = app.test_client()
        
        u = generate_user()
        
        self.user_id = u.id
    
    def tearDown(self):
        
        db.session.rollback()
    
    def test_logged_in_homepage(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
                
            resp = c.get('/')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Log out', html)
            
    def test_logged_in_followers(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
                
            resp = c.get(f'/users/{self.user_id}/followers')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('users-following', html)
            
    def test_not_logged_in_followers(self):
        with self.client as c:
                
            resp = c.get(f'/users/{self.user_id}/followers',
                         follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
            
    def test_logged_in_add_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
        
            msg = {
                'text': 'test message.',
                'user_id': f'{self.user_id}'
            }
                
            resp = c.post('/messages/new',
                        data=msg,
                        follow_redirects=True)

            html = resp.get_data(as_text=True)        
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'{self.user_id}', html)
            self.assertIn(msg['text'], html)
            
    def test_not_logged_in_add_message(self):
        with self.client as c:
                
            resp = c.post('/messages/new',
                         follow_redirects=True)
            
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
            
    def test_logged_in_delete_msg(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
            
            msg = Message(text='test message.',
                        user_id=self.user_id)
            
            db.session.add(msg)
            db.session.commit()
            
            resp = c.post(f'/messages/{msg.id}/delete',
                        follow_redirects=True)

            html = resp.get_data(as_text=True)        

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'{self.user_id}', html)
            self.assertNotIn(msg.text, html)
        
    def test_not_logged_in_delete_message(self):
        with self.client as c:
        
            msg = Message(text='test message.',
                    user_id=self.user_id)
            
            db.session.add(msg)
            db.session.commit()
            
            resp = c.post(f'/messages/{msg.id}/delete',
                            follow_redirects=True)
            
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)