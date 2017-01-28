from django.db import models
from django.contrib.auth.models import User
from djchoices import DjangoChoices, ChoiceItem


# Create your models here.
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

    def __str__(self):
        return "%s (%s)" % (self.slack_name, self.team)


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
