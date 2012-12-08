from django.contrib.auth.models import User
from django.db import models

GAME_CATEGORY = (
    ('Combo', 'combo'),
    ('Floor', 'floor'),
    ('NML', 'nml'),
    ('CC1', 'cc1'),
    ('CC2', 'cc2'),
    ('CC3', 'cc3'),
    ('CC4', 'cc4'),
    ('CC5', 'cc5'),
    ('JS1', 'js1'),
    ('JS2', 'js2'),
    ('JS3', 'js3'),
    ('JS4', 'js4'),
    ('JS5', 'js5'),
)

GAME_FLOOR_SIZE = (
    ('Wide', 'wide'),
    ('Normal', 'normal'),
    ('Shorter', 'shorter'),
    ('Shortest', 'shortest'),
    ('Tiny', 'tiny'),
)

GAME_SPEED = (
    ('Insane', 'insane'),
    ('Fastest', 'fastest'),
    ('Faster', 'faster'),
    ('Fast', 'fast'),
    ('Hasty', 'hasty'),
    ('Normal', 'normal'),
)

GAME_GRAVITY = (
    ('Helium', 'helium'),
    ('Normal', 'normal'),
    ('Heavy', 'heavy'),
)

GAME_SKILLS = (
    (0, 'no rank'),
    (1200, 'over 1200'),
    (1350, 'over 1350'),
    (1500, 'over 1500'),
    (1650, 'over 1650'),
    (1800, 'over 1800'),
    (1950, 'over 1950'),
    (2100, 'over 2100'),
)

class Room(models.Model):
    player1 = models.ForeignKey(User, related_name="player1")
    player2 = models.ForeignKey(User, related_name="player2")
    elo1 = models.IntegerField()
    elo2 = models.IntegerField(default=0)
    category = models.CharField(max_length=30, choices=GAME_CATEGORY)
    accept = models.IntegerField(default=0)
    start = models.DateTimeField()
    end = models.DateTimeField()
    password = models.CharField(max_length=6)
    skills = models.IntegerField(default=1200, choices=GAME_SKILLS)
    floorsize = models.CharField(max_length=30, choices=GAME_FLOOR_SIZE, default='Normal')
    speed = models.CharField(max_length=30, choices=GAME_SPEED, default='Normal')
    gravity = models.CharField(max_length=30, choices=GAME_GRAVITY, default='Normal')
    result1 = models.IntegerField(default=0)
    result2 = models.IntegerField(default=0)
    is_official = models.IntegerField(default=0)
    history = models.TextField()
    
    def __unicode__(self):
        return u'%s %s' % (self.id, self.elo1)
    
class Ranking(models.Model):
    player = models.ForeignKey(User, related_name="player")
    slots = models.IntegerField(default=3)
    rank = models.IntegerField(default=0)
    matches = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    lose = models.IntegerField(default=0)
    draw = models.IntegerField(default=0)
    escape = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u'%s %s %s %s' % (self.player, self.rank)
        
    class Meta:
        verbose_name_plural = 'Ranking'
    
class Records(models.Model):
    player = models.ForeignKey(User, related_name="player_records")
    level = models.CommaSeparatedIntegerField(default='0,0,0', max_length=10)
    combo = models.IntegerField(default=0)
    floor = models.IntegerField(default=0)
    nml = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u'%s %s' % (self.id, self.combo)
        
    class Meta:
        verbose_name_plural = 'Records'
    
class TopRecords(models.Model):
    player_combo = models.CharField(max_length=32)
    combo = models.IntegerField(default=0)
    player_floor = models.CharField(max_length=32)
    floor = models.IntegerField(default=0)
    player_nml = models.CharField(max_length=32)
    nml = models.IntegerField()
    
    def __unicode__(self):
        return u'%s %s' % (self.id, self.combo)
        
    class Meta:
        verbose_name_plural = 'Top Records'
        
class Archive(models.Model):
    tmp_battle_id = models.IntegerField()
    player1 = models.ForeignKey(User, related_name="player1_archive")
    player2 = models.ForeignKey(User, related_name="player2_archive")
    elo1 = models.IntegerField()
    elo2 = models.IntegerField()
    elo1_after = models.IntegerField()
    elo2_after = models.IntegerField()
    category = models.CharField(max_length=30, choices=GAME_CATEGORY)
    start = models.DateTimeField()
    end = models.DateTimeField()
    password = models.CharField(max_length=6)
    skills = models.IntegerField(default=0, choices=GAME_SKILLS)
    floorsize = models.CharField(max_length=30, choices=GAME_FLOOR_SIZE, default='Normal')
    speed = models.CharField(max_length=30, choices=GAME_SPEED, default='Normal')
    gravity = models.CharField(max_length=30, choices=GAME_GRAVITY, default='Normal')
    result1 = models.IntegerField(default=0)
    result2 = models.IntegerField(default=0)
    history = models.TextField()

    def __unicode__(self):
        return u'%s %s' % (self.id, self.tmp_battle_id)
