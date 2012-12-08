from django.conf.urls import patterns, include, url
from battles.views import PlayerRanking, JoinList, ShowList, ArchiveList, BattleCreate
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^$', 'battles.views.index', name='index'),
    url(r'^ranking/$', PlayerRanking.as_view(), name='ranking'),
    url(r'^level/$', 'battles.views.level', name='level'),
    url(r'^search/$', 'battles.views.search', name='search'),
    url(r'^join/$', login_required(JoinList.as_view()), name='join_list'),
    url(r'^show/$', ShowList.as_view(), name='show_list'),
    url(r'^archive/$', ArchiveList.as_view(), name='archive_list'),
    url(r'^new/$', login_required(BattleCreate.as_view()), name='new_battle'),
    url(r'^manage/$', 'battles.views.manage', name='manage'),
    url(r'^(?P<room_id>\d+)/join/$', 'battles.views.join', name='join'),
    url(r'^(?P<room_id>\d+)/show/$', 'battles.views.show', name='show'),
    url(r'^(?P<room_id>\d+)/archive/$', 'battles.views.archive', name='archive'),
    url(r'^(?P<room_id>\d+)/accept/$', 'battles.views.accept', name='accept'),
    url(r'^(?P<room_id>\d+)/reject/$', 'battles.views.reject', name='reject'),
    url(r'^(?P<room_id>\d+)/cancel/$', 'battles.views.cancel', name='cancel'),
    url(r'^(?P<room_id>\d+)/delete/$', 'battles.views.delete', name='delete'),
    url(r'^upload/$', 'battles.views.upload', name='upload'),
    url(r'^upload/status/$', 'battles.views.upload_status', name='upload_status'),
    url(r'^profil/(?P<user_id>\d+)/$', 'battles.views.profil', name='profil'),
    url(r'^register/$', 'battles.views.register', name='register'),
    url(r'^login/$',  'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/itb/battles/'}, name='logout'),
)
