import unittest

from portfolio_manager.tests.windows_profile_owner import OwnedProfiles


class FakeProfiles:
    def __init__(self, fail_create=None):
        self.created = []
        self.deleted = []
        self.fail_create = fail_create
        self.fail_delete = set()

    def CreateAppContainerProfile(self, name, _display, _description, _caps, _count, sid):
        if self.fail_create is not None and len(self.created) == self.fail_create:
            return 0x800700b7
        self.created.append(name)
        sid._obj.value = 123
        return 0

    def DeleteAppContainerProfile(self, name):
        self.deleted.append(name)
        return 5 if name in self.fail_delete else 0

    def FreeSid(self, _sid):
        return None


class ProfileOwnershipTests(unittest.TestCase):
    def test_only_successfully_created_profiles_are_deleted(self):
        fake = FakeProfiles(fail_create=1)
        with self.assertRaises(OSError):
            OwnedProfiles(_api=(fake, fake), _identifier='a' * 32)
        self.assertEqual(fake.deleted, fake.created)
        self.assertEqual(len(fake.deleted), 1)

    def test_failed_deletion_remains_owned_and_can_be_retried(self):
        fake = FakeProfiles()
        owner = OwnedProfiles(_api=(fake, fake), _identifier='b' * 32)
        first, second = fake.created
        fake.fail_delete.add(second)
        with self.assertRaises(RuntimeError):
            owner.close()
        self.assertEqual(owner._created, [second])
        fake.fail_delete.clear()
        owner.close()
        self.assertEqual(owner._created, [])
        self.assertEqual(fake.deleted.count(first), 1)
        self.assertEqual(fake.deleted.count(second), 2)

    def test_invalid_identifier_never_touches_profiles(self):
        fake = FakeProfiles()
        with self.assertRaises(ValueError):
            OwnedProfiles(_api=(fake, fake), _identifier='../other')
        self.assertEqual(fake.created, [])
        self.assertEqual(fake.deleted, [])


if __name__ == '__main__':
    unittest.main()
