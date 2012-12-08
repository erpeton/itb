#!/usr/local/bin/python2.7

from django.core.management import setup_environ
from itb import settings
setup_environ(settings)

from django.contrib.auth.models import User
from battles.models import Ranking, Records, TopRecords

"""
this works fine, but it's noobish ;p 
i should use signal: https://code.djangoproject.com/wiki/Signals
and post_syncdb
i will do it this in the future... maybe...
"""

first_user = User.objects.get(id=1)

add_to_ranking = Ranking(player=first_user)
add_to_ranking.save()

add_to_records = Records(player=first_user)
add_to_records.save()

add_toprecords = TopRecords(player_combo='Jacob', combo=1430, player_floor='cubeoOr', floor=2390, player_nml='cubeoOr', nml=1955)
add_toprecords.save()

print 'Status: OK'
