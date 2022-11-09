"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

def generate_users():
    """Creates 2 users to use for tests."""
    
    u1 = User(
        email="test1@test.com",
        username="testuser1",
        password="HASHED_PASSWORD1"
    )
    
    u2 = User(
        email="test2@test.com",
        username="testuser2",
        password="HASHED_PASSWORD2"
    )

    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    
    return [u1, u2]

def generate_user():
    """Create a user based on User model."""
    
    u = User(
        email="test@test.com",
        username="testuser",
        password="HASHED_PASSWORD"
    )

    db.session.add(u)
    db.session.commit()
    
    return u

class UserModelTestCase(TestCase):
    """Test User model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        
    def tearDown(self):
        
        db.session.rollback()

    def test_create_user(self):
        """Does basic model work?"""

        u = generate_user()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertTrue(u.id)
    
    def test_create_user_unique(self):
        """Fail to create user for duplicate username"""

        u = generate_user()

        db.session.add(u)
        db.session.commit()
        
        u2 = User(
            email="test2@test.com",
            username="testuser", #Same username as u.username
            password="HASHED_PASSWORD2"
        )
        
        db.session.add(u2)

        self.assertRaisesRegex(IntegrityError, 
                               'duplicate key value violates unique constraint',
                               db.session.commit)
    
    def test_user_is_following_true(self):
        """Does is_following track when user is following other_user?"""
        
        users = generate_users()
        
        uf = Follows(user_following_id = users[0].id,
                      user_being_followed_id = users[1].id)
        
        db.session.add(uf)
        db.session.commit()
        
        self.assertTrue(users[0].is_following(users[1]))
        
        
    def test_user_is_following_false(self):
        """Does is_following track when user is not following other_user?"""
        
        users = generate_users()
        
        self.assertFalse(users[0].is_following(users[1]))
        
    def test_user_is_followed_by_true(self):
        """Does is_followed_by track when user is followed by other_user?"""
        
        users = generate_users()
        
        uf = Follows(user_following_id = users[0].id,
                      user_being_followed_id = users[1].id)
        
        db.session.add(uf)
        db.session.commit()
        
        self.assertTrue(users[1].is_followed_by(users[0]))
        
    def test_user_is_followed_by_false(self):
        """Does is_followed_by track when user is not followed by other_user?"""
        
        users = generate_users()
        
        self.assertFalse(users[1].is_followed_by(users[0]))
        
    def test_authenticate_user(self):
        """Test if returns user if valid username and password."""
        
        u = User.signup('testuser',
                        'test@test.com',
                        'HASHED_PASSWORD',
                        'image_url')
        
        auth_user = User.authenticate(u.username,
                                      'HASHED_PASSWORD')
        
        self.assertEqual(auth_user.id, u.id)
        self.assertIsInstance(auth_user, User)
        
    def test_authenticate_username_fail(self):
        """Test if doesn't returns user if not valid username."""
        
        User.signup('testuser',
                        'test@test.com',
                        'HASHED_PASSWORD',
                        'image_url')
        
        auth_user = User.authenticate('testuse',
                                      'HASHED_PASSWORD')
        
        self.assertFalse(auth_user)
        self.assertNotIsInstance(auth_user, User)
        
    def test_authenticate_password_fail(self):
        """Test if doesn't returns user if not valid password."""
        
        u = User.signup('testuser',
                        'test@test.com',
                        'HASHED_PASSWORD',
                        'image_url')
        
        auth_user = User.authenticate(u.username,
                                      'HASHED_PASSWOR')
        
        self.assertFalse(auth_user)
        self.assertNotIsInstance(auth_user, User)