from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Member

class MembersTestCase(TestCase):
    def setUp(self):
        self.user_a = get_user_model().objects.create_user(username='user_a@user.com', first_name='user_a', last_name='user')
        self.user_b = get_user_model().objects.create_user(username='user_b@user.com', first_name='user_b', last_name='user')
        self.user_c = get_user_model().objects.create_user(username='user_c@user.com', first_name='user_c', last_name='user', is_active=False)

        self.member_a = Member.objects.create(user=self.user_a)

    def testMemberName(self):
        self.assertEqual(str(self.member_a), 'user_a user')

    def testCreateMemberExistingUser(self):
        new_member = Member.create_member(first_name='user_b', last_name='user', email='user_b@user.com')

        self.assertEqual(new_member.user, self.user_b)

    def testCreateMemberExistingUserWithPassword(self):
        raise NotImplementedError

    def testCreateMemberExistingInactiveUser(self):
        new_member = Member.create_member(first_name='user_c', last_name='user', email='user_c@user.com')
        self.user_c.refresh_from_db()

        self.assertEqual(new_member.user, self.user_c)
        self.assertTrue(self.user_c.is_active)

    def testCreateMemberNewUser(self):
        new_member = Member.create_member(first_name='user_d', last_name='user', email='user_d@user.com')

        self.assertIsNotNone(get_user_model().objects.get(username='user_d@user.com'))
        self.assertEqual(new_member.user, get_user_model().objects.get(username='user_d@user.com'))
        self.assertTrue(new_member.notes.startswith("Initial password:"))

    def testCreateMemberNewUserWithPassword(self):
        raise NotImplementedError

    def testCreateMemberWithMember(self):
        raise NotImplementedError

    def testCreateMemberWithMemberWithPassword(self):
        raise NotImplementedError

    def testDeleteMember(self):
        self.member_a.delete()
        self.user_a.refresh_from_db()

        self.assertFalse(self.user_a.is_active)
        with self.assertRaises(get_user_model().member.RelatedObjectDoesNotExist):
            self.assertIsNone(self.user_a.member)