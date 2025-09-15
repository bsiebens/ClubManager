# Create your tests here.
import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import create_default_season, team_season_file_path, Team, Season, TeamPicture, TeamRole, TeamMembership
from .rules import is_team_admin, is_a_team_admin


class CreateDefaultSeasonTests(TestCase):
    @patch("teams.models.timezone.now")
    def testStartsPreviousYearIfBeforeSeasonStart(self, mock_now):
        mock_now.return_value = timezone.make_aware(datetime.datetime(2025, 8, 31, 12, 0, 0))
        start, end = create_default_season(day=1, month=9, duration="1y")
        self.assertEqual(start, datetime.date(2024, 9, 1))
        expected_end = datetime.date(2025, 8, 31)
        self.assertEqual(end, expected_end)

    @patch("teams.models.timezone.now")
    def testStartsCurrentYearOnOrAfterSeasonStart(self, mock_now):
        mock_now.return_value = timezone.make_aware(datetime.datetime(2025, 9, 1, 0, 0, 0))
        start, end = create_default_season(day=1, month=9, duration="1y")
        self.assertEqual(start, datetime.date(2025, 9, 1))
        self.assertEqual(end, datetime.date(2026, 8, 31))

    @patch("teams.models.timezone.now")
    def testMonthDurationSixMonthsMinusOneDay(self, mock_now):
        mock_now.return_value = timezone.make_aware(datetime.datetime(2024, 3, 1, 0, 0, 0))
        start, end = create_default_season(day=29, month=2, duration="6m")
        self.assertEqual(start, datetime.date(2024, 2, 29))
        self.assertEqual(end, datetime.date(2024, 8, 28))

    @patch("teams.models.timezone.now")
    def testDayDurationMinusOneDay(self, mock_now):
        mock_now.return_value = timezone.make_aware(datetime.datetime(2025, 1, 1, 0, 0, 0))
        start, end = create_default_season(day=1, month=1, duration="10d")
        self.assertEqual(start, datetime.date(2025, 1, 1))
        self.assertEqual(end, datetime.date(2025, 1, 10))

    @patch("teams.models.timezone.now")
    def testWeekDurationTwoWeeksMinusOneDay(self, mock_now):
        mock_now.return_value = timezone.make_aware(datetime.datetime(2025, 1, 1, 0, 0, 0))
        start, end = create_default_season(day=1, month=1, duration="2w")
        self.assertEqual(start, datetime.date(2025, 1, 1))
        self.assertEqual(end, datetime.date(2025, 1, 14))

    @patch("teams.models.timezone.now")
    def testInvalidDurationUnitRaises(self, mock_now):
        mock_now.return_value = timezone.make_aware(datetime.datetime(2025, 9, 1, 0, 0, 0))
        with self.assertRaises(ValueError):
            create_default_season(day=1, month=9, duration="3x")

    @patch("teams.models.timezone.now")
    def testNoInput(self, mock_now):
        mock_now.return_value = timezone.make_aware(datetime.datetime(2025, 9, 1, 0, 0, 0))
        start, end = create_default_season()
        self.assertEqual(start, datetime.date(2025, 8, 1))
        self.assertEqual(end, datetime.date(2026, 7, 31))


class TeamSeasonFilePathTests(TestCase):
    def testGeneratesExpectedPath(self):
        team = Team.objects.create(name="Toronto Maple Leafs")
        season = Season.objects.create(start_date=datetime.date(2024, 9, 1), end_date=datetime.date(2025, 8, 31))
        picture = TeamPicture(team=team, season=season)
        result = team_season_file_path(picture, "roster.png")
        self.assertEqual(result, f"teams/picture/{team.slug}/2024/roster.png")


class IsTeamAdminRuleTest(TestCase):
    def setUp(self):
        start_date, end_date = create_default_season()

        self.member = get_user_model().objects.create(first_name="John", last_name="Doe", email="johndoe@test.com", username="johndoe").member
        self.member2 = get_user_model().objects.create(first_name="Jane", last_name="Doe", email="janedoe@test.com", username="janedoe").member
        self.team = Team.objects.create(name="Test Team")
        self.season = Season.objects.get_or_create(start_date=start_date, end_date=end_date)[0]
        self.admin_role = TeamRole.objects.create(name="Admin Role", abbreviation="AR", admin_role=True, sort_order=1)
        self.member_role = TeamRole.objects.create(name="Member Role", abbreviation="MR", admin_role=False, sort_order=2)

    def testIsTeamAdminWithAdminRole(self):
        TeamMembership.objects.create(team=self.team, member=self.member, role=self.admin_role, season=self.season)
        self.assertFalse(is_team_admin(self.member.user, None))

    def testIsTeamAdminWithTeamMembershipAndAdminRole(self):
        team_membership = TeamMembership.objects.create(team=self.team, member=self.member, role=self.admin_role, season=self.season)
        self.assertTrue(is_team_admin(self.member.user, team_membership))

    def testIsTeamAdminWithMemberRole(self):
        TeamMembership.objects.create(team=self.team, member=self.member, role=self.member_role, season=self.season)
        self.assertFalse(is_team_admin(self.member.user, None))

    def testIsTeamAdminNoMembership(self):
        self.assertFalse(is_team_admin(self.member.user, None))

    def testIsTeamAdminWithNoneUser(self):
        self.assertFalse(is_team_admin(None, None))

    def testIsTeamAdminWrongTeam(self):
        second_team = Team.objects.create(name="Second Team")
        TeamMembership.objects.create(team=second_team, member=self.member, role=self.admin_role, season=self.season)
        team_membership_first_team = TeamMembership.objects.create(team=self.team, member=self.member, role=self.member_role, season=self.season)

        self.assertFalse(is_team_admin(self.member.user, team_membership_first_team))


class IsATeamAdminRuleTest(TestCase):
    def setUp(self):
        start_date, end_date = create_default_season()

        self.member = get_user_model().objects.create(first_name="John", last_name="Doe", email="johndoe@test.com", username="johndoe").member
        self.member2 = get_user_model().objects.create(first_name="Jane", last_name="Doe", email="janedoe@test.com", username="janedoe").member
        self.team = Team.objects.create(name="Test Team")
        self.season = Season.objects.get_or_create(start_date=start_date, end_date=end_date)[0]
        self.admin_role = TeamRole.objects.create(name="Admin Role", abbreviation="AR", admin_role=True, sort_order=1)
        self.member_role = TeamRole.objects.create(name="Member Role", abbreviation="MR", admin_role=False, sort_order=2)

    def testIsATeamAdminWithAdminRole(self):
        TeamMembership.objects.create(team=self.team, member=self.member, role=self.admin_role, season=self.season)
        self.assertTrue(is_a_team_admin(self.member.user))

    def testIsATeamAdminWithMemberRole(self):
        TeamMembership.objects.create(team=self.team, member=self.member, role=self.member_role, season=self.season)
        self.assertFalse(is_a_team_admin(self.member.user))

    def testIsATeamAdminWithNoneUser(self):
        self.assertFalse(is_a_team_admin(None))


class SeasonTest(TestCase):
    def setUp(self):
        self.start_date, self.end_date = create_default_season()
        self.season = Season.objects.get_or_create(start_date=self.start_date, end_date=self.end_date)[0]

    def testName(self):
        self.assertEqual(str(self.season), f"Season '{self.start_date.strftime("%y")} - '{self.end_date.strftime("%y")}")

    def testDateRange(self):
        self.assertEqual(self.season.date_range, (self.start_date, self.end_date))

    def testIsCurrent(self):
        self.assertTrue(self.season.is_current)

        season2 = Season.objects.create(start_date=datetime.date(2020, 9, 1), end_date=datetime.date(2021, 8, 31))
        self.assertFalse(season2.is_current)

    def testForDate(self):
        self.assertEqual(Season.for_date(self.start_date), self.season)
        self.assertEqual(Season.for_date(), self.season)
        self.assertEqual(Season.for_date(values_only=True), (self.start_date, self.end_date))


class TeamRoleTest(TestCase):
    def testName(self):
        team_role = TeamRole.objects.create(name="Test Role", abbreviation="TR", admin_role=False, sort_order=1)
        self.assertEqual(str(team_role), "Test Role (TR)")


class TeamTest(TestCase):
    def setUp(self):
        self.team_a = Team.objects.create(name="Test Team A", short_name="Team A")
        self.team_b = Team.objects.create(name="Test")

    def testName(self):
        self.assertEqual(str(self.team_a), "Test Team A")

    def testInitials(self):
        self.assertEqual(self.team_a.initials, "TT")
        self.assertEqual(self.team_b.initials, "T")

    def testGetShortName(self):
        self.assertEqual(self.team_a.get_short_name(), "Team A")
        self.assertEqual(self.team_b.get_short_name(), "Test")

    def testMemberCount(self):
        self.assertEqual(self.team_a.member_count, 0)

        start_date, end_date = create_default_season()
        season = Season.objects.get_or_create(start_date=start_date, end_date=end_date)[0]
        role = TeamRole.objects.create(name="Test Role", abbreviation="TR", admin_role=False, sort_order=1)
        member_a = get_user_model().objects.create(first_name="John", last_name="Doe", email="johndoe@test.com", username="johndoe@test.com").member
        TeamMembership.objects.create(team=self.team_a, member=member_a, role=role, season=season)
        self.assertEqual(self.team_a.member_count, 1)

        member_b = get_user_model().objects.create(first_name="John", last_name="Doe", email="johndoeb@test.com", username="johndoeb@test.com").member
        TeamMembership.objects.create(team=self.team_a, member=member_b, role=role, season=season)
        self.assertEqual(self.team_a.member_count, 2)

        member_b.delete()
        self.assertEqual(self.team_a.member_count, 1)


class TeamMembershipTest(TestCase):
    def testName(self):
        team = Team.objects.create(name="Test Team")
        start_date, end_date = create_default_season()
        season = Season.objects.get_or_create(start_date=start_date, end_date=end_date)[0]
        role = TeamRole.objects.create(name="Test Role", abbreviation="TR", admin_role=False, sort_order=1)
        member = get_user_model().objects.create(first_name="John", last_name="Doe", email="johndoe@test.com", username="johndoe@test.com").member

        team_membership = TeamMembership.objects.create(team=team, member=member, role=role, season=season)
        self.assertEqual(str(team_membership), f"Test Team - {member.user.get_full_name()} (TR)")


class TeamPictureTest(TestCase):
    def testName(self):
        team = Team.objects.create(name="Test Team")
        start_date, end_date = create_default_season()
        season = Season.objects.get_or_create(start_date=start_date, end_date=end_date)[0]

        picture = TeamPicture(team=team, season=season, picture="test.png")
        self.assertEqual(str(picture), f"Test Team - {start_date.year}")
