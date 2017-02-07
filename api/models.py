from django.db import models
from djchoices import DjangoChoices, ChoiceItem


class Tournament(models.Model):
    name = models.CharField(max_length=300)
    isActive = models.BooleanField(default=False)

    def __str__(self):
        return "Tournament: %s" % self.name


class Team(models.Model):
    name = models.CharField(max_length=20, blank=False)
    real_name = models.CharField(max_length=200)
    slug = models.CharField(max_length=3, default='non')

    def __str__(self):
        return self.name


class Profile(models.Model):
    team = models.OneToOneField(Team)
    slack_name = models.CharField(max_length=120)
    points = 0
    goals_scored = 0
    goals_conceded = 0
    played = 0

    def __str__(self):
        return "%s (%s)" % (self.slack_name, self.team)

    def inc_points(self, points):
        self.points += points

    def inc_goals_scored(self, goals):
        self.goals_scored += goals

    def inc_goals_conceded(self, goals):
        self.goals_conceded += goals

    def goal_diference(self):
        return int(self.goals_scored - self.goals_conceded)

    def inc_played(self):
        self.played += 1


class MatchStatus(DjangoChoices):
    scheduled = ChoiceItem('scheduled', 'SCHEDULED')
    active = ChoiceItem('active', 'ACTIVE')
    completed = ChoiceItem('completed', 'COMPLETED')


class Match(models.Model):
    home = models.ForeignKey(Profile, related_name='home')
    away = models.ForeignKey(Profile, related_name='away')
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=MatchStatus.choices, validators=[MatchStatus.validator],
                              default=MatchStatus.scheduled)
    tournament = models.ForeignKey(Tournament, blank=False, null=False)

    def __str__(self):
        return "%s - %s (%d - %d) - %s" % (self.home, self.away, self.home_score, self.away_score, self.status)

    def get_score(self):
        return "%s %d - %d %s" % (self.home, self.home_score, self.away_score, self.away)

    def get_score_only_nums(self):
        return "%d-%d" % (self.home_score, self.away_score)

    def get_match_names(self):
        return "%s vs %s" % (self.home, self.away)
