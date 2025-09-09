from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase

User = get_user_model()


class MembersTestCase(TestCase):
    def setUp(self):
        self.user_a = User.objects.create(username="user_a", first_name="User", last_name="A", email="user_a@test.com")

    def testMemberName(self):
        self.assertEqual(str(self.user_a.member), "User A")

    def testMemberCreation(self):
        self.assertTrue(hasattr(self.user_a, "member"))

    def testMemberManager(self):
        self.assertFalse(self.user_a.has_perm("members.member_manager"))
        self.assertFalse(self.user_a.has_perm("members.add_member"))
        self.assertFalse(self.user_a.is_superuser)

        member_manager_permission = Permission.objects.get(codename="member_manager")

        self.user_a.user_permissions.add(member_manager_permission)
        self.user_a = User.objects.get(pk=self.user_a.pk)

        self.assertTrue(self.user_a.has_perm("members.member_manager"))
        self.assertTrue(self.user_a.has_perm("members.add_member"))
        self.assertFalse(self.user_a.is_superuser)
