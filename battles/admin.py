from django.contrib import admin
from battles.models import Room, Archive, Ranking, Records, TopRecords

class RoomAdmin(admin.ModelAdmin):
    list_display = ('player1', 'category', 'start', 'end', 'password',)
    #search_fields = ('player1', 'player2')
    list_filter = ('end',)
    
class RankingAdmin(admin.ModelAdmin):
    list_display = ('player', 'rank', 'slots',)
    
class RecordsAdmin(admin.ModelAdmin):
    list_display = ('player', 'level', 'combo', 'floor', 'nml',)
    
class TopRecordsAdmin(admin.ModelAdmin):
    list_display = ('player_combo', 'combo', 'player_floor', 'floor', 'player_nml', 'nml',)
    
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ('player1', 'category', 'start', 'end', 'password',)

admin.site.register(Room, RoomAdmin)
admin.site.register(Archive, ArchiveAdmin)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(Records, RecordsAdmin)
admin.site.register(TopRecords, TopRecordsAdmin)
