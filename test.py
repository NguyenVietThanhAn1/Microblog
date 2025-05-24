import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timezone, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    def test_password_hashing(self):
        u = User(username='hung', email='hung@example.com')
        u.set_password('123')
        self.assertFalse(u.check_password('345'))
        self.assertTrue(u.check_password('123'))
    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))
    def test_follow(self):
        u1 = User(username = 'an', email = 'annguyn@example.com')
        u2 = User(username ='hung', email = 'hung@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        following = db.session.scalars(u1.following.select()).all()
        followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(following, [])
        self.assertEqual(followers, [])
        
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)
        u1_following = db.session.scalars(u1.following.select()).all()
        u2_followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(u1_following[0].username, 'hung')
        self.assertEqual(u2_followers[0].username, 'an')
        
        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u2.followers_count(), 0)
        
    def test_follow_posts(self):
        #create 5 users
        u1 = User(username='an', email='an@example.com')
        u2 = User(username='zang', email='zang@example.com')
        u3 = User(username = 'lem', email='lem@example.com')
        u4 = User(username='chou', email = 'chouchou@exmple.com')
        u5 = User(username = 'tra', email = 'tra@example.com')
        db.session.add_all([u1, u2, u3, u4, u5])
        
        #create 5 posts
        now = datetime.now(timezone.utc)
        p1 = Post(body ="dit me chon", author = u1, timestamp = now +timedelta(seconds=1))
        p2 = Post(body ="tran tam trang ham loz", author = u2, timestamp = now + timedelta(seconds=4))
        p3 = Post(body = "hard for shrek", author = u3, timestamp = now + timedelta(seconds=3))
        p4 = Post(body = "tao da vao dau may bay gio?", author = u4, timestamp = now+timedelta(seconds=2))
        p5 = Post(body = "f5 bantumlum", author = u5, timestamp = now + timedelta(seconds=5))
        db.session.add_all([p1, p2, p3, p4, p5])
        db.session.commit
        
        #setup the followers
        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u1)
        u4.follow(u5)
        u5.follow(u3)
        db.session.commit()
        
        #check the following posts of each user
        f1 = db.session.scalars(u1.following_post()).all()
        f2 = db.session.scalars(u2.following_post()).all()
        f3 = db.session.scalars(u3.following_post()).all()
        f4 = db.session.scalars(u4.following_post()).all()
        f5 = db.session.scalars(u5.following_post()).all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p1])
        self.assertEqual(f4, [p5, p4])
        self.assertEqual(f5, [p5, p3])
        
if __name__ == "__main__":
    unittest.main(verbosity=2)