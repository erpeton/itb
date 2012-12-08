#!/usr/local/bin/python2.7

from django.core.management import setup_environ
from itb import settings
setup_environ(settings)

from battles.models import Room, Ranking, Archive
import datetime

"""
1. Delete nonactive rooms from 'Join battle' (start < now)
"""

now = datetime.datetime.now()

rooms_count = Room.objects.filter(is_official=0, start__lt=now).count()
room = Room.objects.filter(is_official=0, start__lt=now)

for i in range(0, rooms_count):
    print '1. Delete waiting room: '+str(room[i].id)
    
    if room[i].player1 == room[i].player2:
        room_creator = Ranking.objects.get(player=room[i].player1)
        room_creator.slots +=1
        room_creator.save()
    else:
        room_creator = Ranking.objects.get(player=room[i].player1)
        room_opponent = Ranking.objects.get(player=room[i].player2)
        room_creator.slots +=1
        room_opponent.slots +=1
        room_creator.save()
        room_opponent.save()
        
room.delete()
    
"""
2. Delete OFFICIAL rooms and move it to archive (end < now)
"""
rooms_count = Room.objects.filter(is_official=1, end__lt=now).count()
room = Room.objects.filter(is_official=1, end__lt=now)

for i in range(0, rooms_count):
    print '2. Delete official room: '+str(room[i].id)

    room_creator = Ranking.objects.get(player=room[i].player1)
    room_opponent = Ranking.objects.get(player=room[i].player2)
    
    old_rank_creator = room[i].elo1
    old_rank_opponent = room[i].elo2
    
    if old_rank_creator != room_creator.rank:
        old_rank_creator = room_creator.rank
        
    if old_rank_opponent != room_opponent.rank:
        old_rank_opponent = room_opponent.rank
        
    # points for battle
    if room[i].result1 > room[i].result2 and room[i].result2 > 0:
        # player1 win, player2 lose
        diff = old_rank_opponent-old_rank_creator
        we = 1/(1+10**(diff/700.0))
        diff2 = 1-we
        extra_points = round(32*diff2)
        
        new_rank_creator = old_rank_creator+extra_points
        new_rank_opponent = old_rank_opponent-extra_points
        
        room_creator.rank = new_rank_creator
        room_creator.matches += 1
        room_creator.win += 1
        room_creator.save()
        
        room_opponent.rank = new_rank_opponent
        room_opponent.matches += 1
        room_opponent.lose += 1
        room_opponent.save()
        
        #print new_rank_creator, new_rank_opponent
        
    elif room[i].result2 > room[i].result1 and room[i].result1 > 0:
        # player2 win, player1 lose
        diff = old_rank_creator-old_rank_opponent
        we = 1/(1+10**(diff/700.0))
        diff2 = 1-we
        extra_points = round(32*diff2)
        
        new_rank_creator = old_rank_creator-extra_points
        new_rank_opponent = old_rank_opponent+extra_points
        
        room_creator.rank = new_rank_creator
        room_creator.matches += 1
        room_creator.lose += 1
        room_creator.save()
        
        room_opponent.rank = new_rank_opponent
        room_opponent.matches += 1
        room_opponent.win += 1
        room_opponent.save()
        
    elif room[i].result1 == room[i].result2 and room[i].result1 > 0 and room[i].result2 > 0:
        # draw :|
        
        if old_rank_creator > old_rank_opponent:
            diff = old_rank_creator-old_rank_opponent
            we = 1/(1+10**(diff/700.0))
            diff2 = 1-we
            extra_points = round(32*diff2/2)
            
            new_rank_creator = old_rank_creator-extra_points
            new_rank_opponent = old_rank_opponent+extra_points
            
            room_creator.rank = new_rank_creator
            room_creator.matches += 1
            room_creator.draw += 1
            room_creator.save()
            
            room_opponent.rank = new_rank_opponent
            room_opponent.matches += 1
            room_opponent.draw += 1
            room_opponent.save()
            
        elif old_rank_opponent > old_rank_creator:
            diff = old_rank_opponent-old_rank_creator
            we = 1/(1+10**(diff/700.0))
            diff2 = 1-we
            extra_points = round(32*diff2/2)
            
            new_rank_creator = old_rank_creator+extra_points
            new_rank_opponent = old_rank_opponent-extra_points
            
            room_creator.rank = new_rank_creator
            room_creator.matches += 1
            room_creator.draw += 1
            room_creator.save()
            
            room_opponent.rank = new_rank_opponent
            room_opponent.matches += 1
            room_opponent.draw += 1
            room_opponent.save()
            
        else:
            
            new_rank_creator = old_rank_creator+8
            new_rank_opponent = old_rank_opponent+8
            
            room_creator.rank = new_rank_creator
            room_creator.matches += 1
            room_creator.draw += 1
            room_creator.save()
            
            room_opponent.rank = new_rank_opponent
            room_opponent.matches += 1
            room_opponent.draw += 1
            room_opponent.save()
            
    elif room[i].result1 > room[i].result2 and room[i].result2 == 0:
        # player1 win, player2 escape
        diff = old_rank_opponent-old_rank_creator
        we = 1/(1+10**(diff/700.0))
        diff2 = 1-we
        extra_points = round(32*diff2)
        
        new_rank_creator = old_rank_creator+extra_points
        new_rank_opponent = old_rank_opponent-40
        
        room_creator.rank = new_rank_creator
        room_creator.matches += 1
        room_creator.win += 1
        room_creator.save()
        
        room_opponent.rank = new_rank_opponent
        room_opponent.matches += 1
        room_opponent.escape += 1
        room_opponent.save()
        
    elif room[i].result2 > room[i].result1 and room[i].result1 == 0:
        # player2 win, player1 escape
        diff = old_rank_creator-old_rank_opponent
        we = 1/(1+10**(diff/700.0))
        diff2 = 1-we
        extra_points = round(32*diff2)
        
        new_rank_creator = old_rank_creator-40
        new_rank_opponent = old_rank_opponent+extra_points
        
        room_creator.rank = new_rank_creator
        room_creator.matches += 1
        room_creator.escape += 1
        room_creator.save()
        
        room_opponent.rank = new_rank_opponent
        room_opponent.matches += 1
        room_opponent.win += 1
        room_opponent.save()
        
    elif room[i].result1 == 0 and room[i].result2 == 0:
        # player1 escape, player2 escape
        new_rank_creator = old_rank_creator-40
        new_rank_opponent = old_rank_opponent-40
        
        room_creator.rank = new_rank_creator
        room_creator.matches += 1
        room_creator.escape += 1
        room_creator.save()
        
        room_opponent.rank = new_rank_opponent
        room_opponent.matches += 1
        room_opponent.escape += 1
        room_opponent.save()
        
    archive_battle = Archive(tmp_battle_id=room[i].id, 
                                player1=room[i].player1,
                                player2=room[i].player2,
                                elo1=old_rank_creator,
                                elo2=old_rank_opponent,
                                elo1_after=new_rank_creator,
                                elo2_after=new_rank_opponent,
                                category=room[i].category,
                                start=room[i].start,
                                end=room[i].end,
                                password=room[i].password,
                                skills=room[i].skills,
                                result1=room[i].result1,
                                result2=room[i].result2,
                                history=room[i].history,
                                floorsize=room[i].floorsize,
                                speed=room[i].speed,
                                gravity=room[i].gravity)
                                
    archive_battle.save()
                                
    room_creator.slots +=1
    room_opponent.slots +=1
    room_creator.save()
    room_opponent.save()
    
room.delete()

"""
3. Update all another battles (waiting and official)
"""

rooms_count = Room.objects.all().count()
room = Room.objects.all()

for i in range(0, rooms_count):
    if room[i].player1 == room[i].player2:
        room_creator = Ranking.objects.get(player=room[i].player1)
        foo = Room.objects.get(id=room[i].id)
        if room_creator.rank != room[i].elo1:
            foo.elo1 = room_creator.rank
            foo.save()
    else:
        room_creator = Ranking.objects.get(player=room[i].player1)
        room_opponent = Ranking.objects.get(player=room[i].player2)
        
        foo = Room.objects.get(id=room[i].id)
        
        if room_creator.rank != room[i].elo1:
            foo.elo1 = room_creator.rank
            foo.save()
            
        if room_opponent.rank != room[i].elo2:
            foo.elo2 = room_opponent.rank
            foo.save()
