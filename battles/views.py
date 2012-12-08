from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import ListView, CreateView
from django.contrib.auth.decorators import login_required

from battles.models import Room, Ranking, Records, TopRecords, Archive
from battles.forms import BattleForm, UploadForm
from battles.tools import random_string, check_slowdown, handle_uploaded_file

from django.contrib import messages
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User

from django import forms
from django.contrib.auth.forms import UserCreationForm

import datetime
import struct

class PlayerRanking(ListView):
    paginate_by = 5
    queryset=Ranking.objects.filter(rank__gt=1000).order_by('-rank')
    context_object_name='ranking'
    template_name='battles/ranking.html'
    
class JoinList(ListView):
    paginate_by = 5
    queryset=Room.objects.filter(is_official=0, start__gt=datetime.datetime.now()).order_by('start')
    context_object_name='latest_room_list'
    template_name='battles/join_list.html'
    
    def get_context_data(self, **kwargs):
        context = super(JoinList, self).get_context_data(**kwargs)
        opponent = Ranking.objects.get(player=self.request.user)
        context['opponent_slots'] = opponent.slots
        context['opponent_rank'] = opponent.rank
        return context
        
class ShowList(ListView):
    paginate_by = 5
    queryset=Room.objects.filter(is_official=1, end__gt=datetime.datetime.now()).order_by('start')
    context_object_name='official_room_list'
    template_name='battles/show_list.html'
    
    def get_context_data(self, **kwargs):
        context = super(ShowList, self).get_context_data(**kwargs)
        get_time = datetime.datetime.now()
        context['now'] = get_time
        return context
        
class ArchiveList(ListView):
    paginate_by = 5
    queryset=Archive.objects.all().order_by('-end')
    context_object_name='archives_room_list'
    template_name='battles/archive_list.html'
    
class BattleCreate(CreateView):
    model = Room
    template_name = 'battles/new.html'
    success_url = '/itb/battles/join'
    form_class = BattleForm
        
    def get_initial(self):
        initial = super(BattleCreate, self).get_initial()
        earliest = datetime.datetime.now() + datetime.timedelta(hours=2)
        earliest_date = "%s.%s.%s %s:00" % (earliest.day, earliest.month, earliest.year, earliest.hour)
        latest = datetime.datetime.now() + datetime.timedelta(hours=8)
        latest_date = "%s.%s.%s %s:00" % (latest.day, latest.month, latest.year, latest.hour)
        initial['start'] = earliest_date
        initial['end'] = latest_date
        return initial
    
    """
    http://stackoverflow.com/questions/5806224/sending-request-user-object-to-modelform-from-class-based-generic-view-in-django
    """
    def get_form_kwargs(self):
        kwargs = super(BattleCreate, self).get_form_kwargs()
        kwargs.update({'player1': self.request.user})
        return kwargs
    
    def form_valid(self, form):
        decrease = Ranking.objects.get(player=self.request.user)
        form.instance.player1 = self.request.user
        form.instance.player2 = self.request.user
        form.instance.elo1 = decrease.rank
        form.instance.password = random_string(6)
        decrease.slots -=1
        decrease.save()
        return super(BattleCreate, self).form_valid(form)
        
    def get_context_data(self, **kwargs):
        context = super(BattleCreate, self).get_context_data(**kwargs)
        player_can_play = Ranking.objects.get(player=self.request.user)
        context['had_free_slots'] = player_can_play.slots
        context['had_rank'] = player_can_play.rank
        return context

@login_required
def join(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    opponent = Ranking.objects.get(player=request.user)
    now = datetime.datetime.now()
    
    if room.player1 == request.user:
        messages.error(request, 'Do you want to play with yourself?')
    elif opponent.slots == 0:
        messages.error(request, 'You can play in three battles max!')
    elif room.accept > 0:
        messages.error(request, 'Sorry, someone has just joined!')
    elif opponent.rank == 0:
        messages.error(request, 'Only players with rank can play! Upload your records to get rank!')
    elif opponent.rank < room.skills:
        messages.error(request, 'Only players with rank over %s can join, you had %s!' % (room.skills, opponent.rank))
    elif room.start < now:
        messages.error(request, 'This battle will be removed soon!')
    else:
        opponent.slots -=1
        opponent.save()
        
        room.player2 = request.user
        room.elo2 = opponent.rank
        room.accept = 1
        room.save()
        
    return render_to_response('battles/join.html', {'room': room}, context_instance=RequestContext(request))

def show(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    now = datetime.datetime.now()
    
    html = []
    if room.history != '':
        history = room.history.split(",")
        foo = len(history)

        for i in range(0, foo, 3):
            html.append('[%s]: %s %s [%s]' % (history[i], history[i+1], room.category, history[i+2]))

    return render_to_response('battles/show.html', {'room': room, 'now': now, 'html': html}, context_instance=RequestContext(request))

def archive(request, room_id):
    archive = get_object_or_404(Archive, pk=room_id)
    now = datetime.datetime.now()
    
    html = []
    if archive.history != '':
        history = archive.history.split(",")
        foo = len(history)

        for i in range(0, foo, 3):
            html.append('[%s]: %s %s [%s]' % (history[i], history[i+1], archive.category, history[i+2]))
            
    return render_to_response('battles/archive.html', {'room': archive, 'now': now, 'html': html}, context_instance=RequestContext(request))
        
@login_required
def accept(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    now = datetime.datetime.now()
    
    if room.player1 != request.user:
        messages.error(request, 'You cant accept battles of another players!')
    elif room.accept == 0:
        messages.error(request, 'Do you want to play with yourself?')
    elif room.is_official == 1:
        messages.error(request, 'You have already accepted this battle!')
    elif room.start < now:
        messages.error(request, 'This battle will be removed soon!')
    else:
        room.is_official = 1
        room.save()
    
    return render_to_response('battles/accept.html', {'room': room}, context_instance=RequestContext(request))

@login_required
def reject(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    opponent = Ranking.objects.get(player=room.player2)
    now = datetime.datetime.now()
    
    if room.player1 != request.user:
        messages.error(request, 'You cant reject battles of another players!')
    elif room.accept == 0:
        messages.error(request, 'You are waiting still for second player!')
    elif room.is_official == 1:
        messages.error(request, 'This battle has official status, so you cant reject request from player!')
    elif room.start < now:
        messages.error(request, 'This battle will be removed soon!')
    else:
        opponent.slots +=1
        opponent.save()
        
        room.player2 = room.player1
        room.elo2 = 0
        room.accept = 0
        room.save()
    
    return render_to_response('battles/reject.html', {'room': room}, context_instance=RequestContext(request))

@login_required
def cancel(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    opponent = Ranking.objects.get(player=room.player2)
    now = datetime.datetime.now()
    
    if room.player2 != request.user:
        messages.error(request, 'You cant cancel battles of another players!')
    elif room.accept == 0:
        messages.error(request, 'Access denied')
    elif room.is_official == 1:
        messages.error(request, 'This battle has official status, so you cant cancel this battle!')
    elif room.start < now:
        messages.error(request, 'This battle will be removed soon!')
    else:
        opponent.slots +=1
        opponent.save()
        
        room.player2 = room.player1
        room.elo2 = 0
        room.accept = 0
        room.save()
        
    return render_to_response('battles/cancel.html', {'room': room}, context_instance=RequestContext(request))

@login_required
def delete(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    opponent = Ranking.objects.get(player=room.player1)
    now = datetime.datetime.now()
    
    if room.player1 != request.user:
        messages.error(request, 'You cant delete battles of another players!')
    elif room.is_official == 1:
        messages.error(request, 'This battle has official status, so you cant delete this battle!')
    elif room.accept == 1:
        messages.error(request, 'First reject request from second player, later you can delete this battle!')
    elif room.start < now:
        messages.error(request, 'This battle will be removed soon!')
    else:
        opponent.slots +=1
        opponent.save()
        
        room.delete()
        
    return render_to_response('battles/delete.html', {'room': room}, context_instance=RequestContext(request))

@login_required
def manage(request):
    get_battles = Room.objects.filter(Q(player1=request.user) | Q(player2=request.user), is_official=0)
    return render_to_response('battles/manage.html', {'manage_battles': get_battles}, context_instance=RequestContext(request))

def profil(request, user_id):
    user_ranking = get_object_or_404(Ranking, player=user_id)
    user_records = Records.objects.get(player=user_id)
    level = user_records.level.split(",")
    level_sum = int(level[0])+int(level[1])+int(level[2])
    user_archives = Archive.objects.filter(Q(player1=user_id) | Q(player2=user_id)).order_by('-end')
    paginator = Paginator(user_archives, 5)

    page = request.GET.get('page')
    try:
        archives = paginator.page(page)
    except PageNotAnInteger:
        archives = paginator.page(1)
    except EmptyPage:
        archives = paginator.page(paginator.num_pages)
    is_paged = paginator.num_pages > 1
    
    return render_to_response('battles/profil.html', {'ranking': user_ranking, 'records': user_records, 'level': level_sum, 'archive': archives, 'is_paginated' : is_paged}, context_instance=RequestContext(request))

def level(request):
    top_records = TopRecords.objects.get(id=1)
        
    combo = []
    floor = []
    nml = []
    
    one_part_combo = round(top_records.combo)/10
    one_part_floor = round(top_records.floor)/10
    one_part_nml = round(top_records.nml)/10
    
    for i in range(1, 11):
        if i == 1:
            range_begin = 0
            range_end = round(one_part_combo)
            combo.append(str(int(range_begin))+' - '+str(int(range_end)))
        else:
            range_begin = range_end+1
            range_end = round(one_part_combo*i)
            combo.append(str(int(range_begin))+' - '+str(int(range_end)))
            
    for i in range(1, 11):
        if i == 1:
            range_begin = 0
            range_end = round(one_part_floor)
            floor.append(str(int(range_begin))+' - '+str(int(range_end)))
        else:
            range_begin = range_end+1
            range_end = round(one_part_floor*i)
            floor.append(str(int(range_begin))+' - '+str(int(range_end)))
            
    for i in range(1, 11):
        if i == 1:
            range_begin = 0
            range_end = round(one_part_nml)
            nml.append(str(int(range_begin))+' - '+str(int(range_end)))
        else:
            range_begin = range_end+1
            range_end = round(one_part_nml*i)
            nml.append(str(int(range_begin))+' - '+str(int(range_end)))
        
    return render_to_response('battles/level.html', {'combo': combo, 'floor': floor, 'nml': nml}, context_instance=RequestContext(request))

def search(request):
    error = False
    if 'u' in request.GET:
        u = request.GET['u']
        if not u:
            error = True
        else:
            player = get_object_or_404(User, username=u)
            return render_to_response('battles/search_results.html', {'player': player, 'query': u}, context_instance=RequestContext(request))
            
    return render_to_response('battles/search.html', {'error': error}, context_instance=RequestContext(request))

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/itb/battles/")
    else:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                new_user = form.save()
                add_to_rank = Ranking(player=new_user)
                add_to_rank.save()
                add_to_records = Records(player=new_user)
                add_to_records.save()
                messages.success(request, 'Your account was created! Now you can login!')
                return HttpResponseRedirect("/itb/battles/login/")
        else:
            form = UserCreationForm()
        
    return render_to_response("registration/register.html", {'form': form}, context_instance=RequestContext(request))

@login_required
def upload(request):
    
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            
            replay = request.FILES['replay'].read()
            it_version = replay[0:0+6]
            player_name_length = len(request.user.username)
            player_name = replay[10:10+player_name_length]
            player_name_lower = player_name.lower()
            logged_user_lower = request.user.username.lower()
            is_cheater = check_slowdown(replay)
    
            if it_version != 'ITR140':
                messages.error(request, 'Sorry, only replays from Icy Tower 1.4/1.5 are accepted! Try again!')
            elif player_name_lower != logged_user_lower:
                messages.error(request, 'Sorry, the username in the replay is not the same as your username! Try again!')
            elif is_cheater > 0:
                messages.error(request, 'Sorry, slowdown has been detected in this replay! Try again!')
            else:
        
                floor = int(struct.unpack('i', replay[78:78+4])[0])
                combo = int(struct.unpack('i', replay[82:82+4])[0])
                cc1 = int(struct.unpack('i', replay[94:94+4])[0])
                cc2 = int(struct.unpack('i', replay[98:98+4])[0])
                cc3 = int(struct.unpack('i', replay[102:102+4])[0])
                cc4 = int(struct.unpack('i', replay[106:106+4])[0])
                cc5 = int(struct.unpack('i', replay[110:110+4])[0])
                js1 = int(struct.unpack('i', replay[114:114+4])[0])
                js2 = int(struct.unpack('i', replay[118:118+4])[0])
                js3 = int(struct.unpack('i', replay[122:122+4])[0])
                js4 = int(struct.unpack('i', replay[126:126+4])[0])
                js5 = int(struct.unpack('i', replay[130:130+4])[0])
                floor_size = int(struct.unpack('b', replay[138:138+1])[0])
                speed = int(struct.unpack('b', replay[142:142+1])[0])
                gravity = int(struct.unpack('b', replay[150:150+1])[0])
        
                if combo == 0:
                    nml = floor
                else:
                    nml = 0

                replay_password = replay[162:162+6]
                can_upload_replay = False
        
                if floor_size == 1 and speed == 5 and gravity == 1:
            
                    player_records = Records.objects.get(player=request.user)
                    top_records = TopRecords.objects.get(id=1)
                    
                    points_combo = 0
                    points_floor = 0
                    points_nml = 0
            
                    if combo > player_records.combo:
                        one_part = round(top_records.combo)/10
                        for i in range(1, 11):
                            if i == 1:
                                range_begin = 0
                                range_end = round(one_part)
                                if combo >= range_begin and combo <= range_end:
                                    points_combo = i
                            else:
                                range_begin = range_end+1
                                range_end = round(one_part*i)
                                if combo >= range_begin and combo <= range_end:
                                    points_combo = i
            
                        player_records.combo = combo
                        player_records.save()
                        messages.success(request, 'Congratulations! This is your new combo record!')
                        can_upload_replay = True
                        full_name = player_name+'_best_combo.itr'
                        handle_uploaded_file(request.FILES['replay'], 'records', full_name)
                
                    if floor > player_records.floor:
                        one_part = round(top_records.floor)/10
                        for i in range(1, 11):
                            if i == 1:
                                range_begin = 0
                                range_end = round(one_part)
                                if floor >= range_begin and floor <= range_end:
                                    points_floor = i
                            else:
                                range_begin = range_end+1
                                range_end = round(one_part*i)
                                if floor >= range_begin and floor <= range_end:
                                    points_floor = i
            
                        player_records.floor = floor
                        player_records.save()
                        messages.success(request, 'Congratulations! This is your new floor record!')
                        can_upload_replay = True
                        full_name = player_name+'_best_floor.itr'
                        handle_uploaded_file(request.FILES['replay'], 'records', full_name)
                
                    if nml > player_records.nml:
                        one_part = round(top_records.nml)/10
                        for i in range(1, 11):
                            if i == 1:
                                range_begin = 0
                                range_end = round(one_part)
                                if nml >= range_begin and nml <= range_end:
                                    points_nml = i
                            else:
                                range_begin = range_end+1
                                range_end = round(one_part*i)
                                if nml >= range_begin and nml <= range_end:
                                    points_nml = i
            
                        player_records.nml = nml
                        player_records.save()
                        messages.success(request, 'Congratulations! This is your new nml record!')
                        can_upload_replay = True
                        full_name = player_name+'_best_nml.itr'
                        handle_uploaded_file(request.FILES['replay'], 'records', full_name)
                
                    old_level = player_records.level.split(",")
                    old_level_sum = int(old_level[0])+int(old_level[1])+int(old_level[2])
        
                    if points_combo > int(old_level[0]):
                        old_level[0] = str(points_combo)
                    if points_floor > int(old_level[1]):
                        old_level[1] = str(points_floor)
                    if points_nml > int(old_level[2]):
                        old_level[2] = str(points_nml)
            
                    new_level_sum = int(old_level[0])+int(old_level[1])+int(old_level[2])
                    new_level = ",".join(old_level)
            
                    if new_level_sum > old_level_sum:
                        player_records.level = new_level
                        player_records.save()
                        messages.success(request, 'Your level has been successfully updated!')
            
                        j = 0
                        for i in range(1, 31, 3):
                            if old_level_sum == 0:
                                range_tmp1 = 0
                            elif old_level_sum in (i,i+1,i+2):
                                range_tmp1 = j
                            j += 1
                
                        k = 0
                        for i in range(1, 31, 3):
                            if new_level_sum in (i, i+1, i+2):
                                range_tmp2 = k
                            k += 1
            
                        if old_level_sum == 0 and range_tmp2 == 0:
                            player_ranking = Ranking.objects.get(player=request.user)
                            player_ranking.rank = 1200
                            player_ranking.save()
                            messages.success(request, 'Your rank has been updated to 1200!')
                
                        if range_tmp2 > range_tmp1:
                            player_ranking = Ranking.objects.get(player=request.user)
                            old_rank = player_ranking.rank
                            new_rank = 1200+range_tmp2*100
                
                            if new_rank > old_rank:
                                player_rooms_count = Room.objects.filter(Q(player1=request.user) | Q(player2=request.user)).count()
                                player_room = Room.objects.filter(Q(player1=request.user) | Q(player2=request.user))
                                for i in range(0, player_rooms_count):
                                    if player_room[i].player1 == player_room[i].player2:
                                        room_again = Room.objects.get(id=player_room[i].id)
                                        room_again.elo1 = new_rank
                                        room_again.save()
                                    else:
                                        if player_room[i].player1 == request.user:
                                            room_again = Room.objects.get(id=player_room[i].id)
                                            room_again.elo1 = new_rank
                                            room_again.save()
                                        elif player_room[i].player2 == request.user:
                                            room_again = Room.objects.get(id=player_room[i].id)
                                            room_again.elo2 = new_rank
                                            room_again.save()
                                
                                player_ranking.rank = new_rank
                                player_ranking.save()
                                messages.success(request, 'Your rank has been updated to %s' % new_rank)
        
                # Battle
                room_exist = True
                try:
                    check_room = Room.objects.get(password=replay_password, is_official=1)
                except Room.DoesNotExist:
                    room_exist = False
            
                if room_exist:
                    can_upload_replay = True
            
                    if check_room.player1 == request.user:
                        player_result = check_room.result1
                    elif check_room.player2 == request.user:
                        player_result = check_room.result2
                    else:
                        player_result = 'Neuer'

                    battle_category = check_room.category
                    battle_floorsize = check_room.floorsize
                    battle_speed = check_room.speed
                    battle_gravity = check_room.gravity

                    if battle_floorsize == 'Wide':
                        battle_set_floorsize = 0
                    elif battle_floorsize == 'Normal':
                        battle_set_floorsize = 1
                    elif battle_floorsize == 'Shorter':
                        battle_set_floorsize = 2
                    elif battle_floorsize == 'Shortest':
                        battle_set_floorsize = 3
                    elif battle_floorsize == 'Tiny':
                        battle_set_floorsize = 4
                
                    if battle_speed == 'Insane':
                        battle_set_speed = 0
                    elif battle_speed == 'Fastest':
                        battle_set_speed = 1
                    elif battle_speed == 'Faster':
                        battle_set_speed = 2
                    elif battle_speed == 'Fast':
                        battle_set_speed = 3
                    elif battle_speed == 'Hasty':
                        battle_set_speed = 4
                    elif battle_speed == 'Normal':
                        battle_set_speed = 5
                
                    if battle_gravity == 'Helium':
                        battle_set_gravity = 0
                    elif battle_gravity == 'Normal':
                        battle_set_gravity = 1
                    elif battle_gravity == 'Heavy':
                        battle_set_gravity = 2
                
                    if floor_size == battle_set_floorsize and speed == battle_set_speed and gravity == battle_set_gravity:
                        
                        if battle_category == 'Combo':
                            new_player_result = combo
                        elif battle_category == 'Floor':
                            new_player_result = floor
                        elif battle_category == 'NML':
                            new_player_result = nml
                        elif battle_category == 'CC1':
                            new_player_result = cc1
                        elif battle_category == 'CC2':
                            new_player_result = cc2
                        elif battle_category == 'CC3':
                            new_player_result = cc3
                        elif battle_category == 'CC4':
                            new_player_result = cc4
                        elif battle_category == 'CC5':
                            new_player_result = cc5
                        elif battle_category == 'JS1':
                            new_player_result = js1
                        elif battle_category == 'JS2':
                            new_player_result = js2
                        elif battle_category == 'JS3':
                            new_player_result = js3
                        elif battle_category == 'JS4':
                            new_player_result = js4
                        elif battle_category == 'JS5':
                            new_player_result = js5
                
                        if player_result == 'Neuer':
                            messages.error(request, 'Only Neuer knows about this bug! ;)')
                        elif new_player_result > player_result:
                            now_date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
                
                            if check_room.history == '':
                                check_room.history += now_date+','+str(new_player_result)+','+player_name
                            else:
                                check_room.history += ','+now_date+','+str(new_player_result)+','+player_name
                    
                            if check_room.player1 == request.user:
                                check_room.result1 = new_player_result
                                check_room.save()
                            elif check_room.player2 == request.user:
                                check_room.result2 = new_player_result
                                check_room.save()
                    
                            messages.success(request, 'OK, your replay was uploaded! :)')
                            full_name = player_name+'_battle'+str(check_room.id)+'.itr'
                            handle_uploaded_file(request.FILES['replay'], 'replays', full_name)
                        else:
                            messages.error(request, 'Sorry, you can only upload results higher than those you already have! Try again')
                    else:
                        messages.error(request, 'The password is correct, but the category is wrong!')
            
                if can_upload_replay == False:
                    messages.error(request, 'Sorry, you can only upload replays if they are your records (in Combo, Floor or NML) or you are playing in a battle (and the password is correct!) Try again!')
    
            return HttpResponseRedirect('/itb/battles/upload/status')
        
    else:
        form = UploadForm()
    
    return render_to_response('battles/upload_form.html', {'form': form}, context_instance=RequestContext(request))

def upload_status(request):
    return render_to_response('battles/upload_status.html', context_instance=RequestContext(request))

def index(request):
    return render_to_response('battles/index.html', context_instance=RequestContext(request))
