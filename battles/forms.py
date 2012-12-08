from django import forms
from battles.models import Room, Ranking
import datetime
    
class BattleForm(forms.ModelForm):
       
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('player1')
        super(BattleForm, self).__init__(*args, **kwargs)
        
        self.fields['start'].widget.format = '%d.%m.%Y %H:00'
        self.fields['end'].widget.format = '%d.%m.%Y %H:00'
        self.fields['start'].input_formats = ['%d.%m.%Y %H:00']
        self.fields['end'].input_formats = ['%d.%m.%Y %H:00']
        
    def clean(self):
        super(BattleForm,self).clean()
        if 'start' in self.cleaned_data and 'end' in self.cleaned_data:
            start = self.cleaned_data['start']
            end = self.cleaned_data['end']
            now = datetime.datetime.now() + datetime.timedelta(hours=1)
            future = datetime.datetime.now() + datetime.timedelta(hours=2, days=14)
            duration_min = start + datetime.timedelta(hours=1)
            duration_max = start + datetime.timedelta(hours=48)
            
            if start < now:
                earliest = datetime.datetime.now() + datetime.timedelta(hours=2)
                earliest_date = "%s.%s.%s %s:00" % (earliest.day, earliest.month, earliest.year, earliest.hour)
                self._errors['start'] = [u'At the earliest: %s' % earliest_date]
            elif start > future:
                latest = datetime.datetime.now() + datetime.timedelta(hours=2, days=14)
                latest_date = "%s.%s.%s %s:00" % (latest.day, latest.month, latest.year, latest.hour)
                self._errors['start'] = [u'At the latest: %s' % latest_date]
            elif end < duration_min:
                najmniej = "%s.%s.%s %s:00" % (duration_min.day, duration_min.month, duration_min.year, duration_min.hour)
                self._errors['end'] = [u'Minimum 1 hour: %s' % najmniej]
            elif end > duration_max:
                najwiecej = "%s.%s.%s %s:00" % (duration_max.day, duration_max.month, duration_max.year, duration_max.hour)
                self._errors['end'] = [u'Maximum 48 hours: %s' % najwiecej]
                
        foo = Ranking.objects.get(player=self.user)
        if foo.rank == 0:
            raise forms.ValidationError('Your rank must be higher than 0, if you want create battle! Upload your records and you get rank!')
        elif foo.slots == 0:
            raise forms.ValidationError('You can play in three battles max!')
                
        return self.cleaned_data
    
    class Meta:
        model = Room
        exclude = ('player1', 'elo1', 'player2', 'elo2', 'password', 'history', 'accept', 'result1', 'result2', 'is_official',)

    """
    https://docs.djangoproject.com/en/1.4/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
    def clean(self):
        cleaned_data = super(Battle2Form, self).clean()
        speed = cleaned_data.get("speed")
        gravity = cleaned_data.get("gravity")

        if speed and gravity:
            # Only do something if both fields are valid so far.
            if "Normal" not in gravity:
            raise forms.ValidationError("Sorry, only game with normal gravity!")

        # Always return the full collection of cleaned data.
        return cleaned_data
    """

class UploadForm(forms.Form):
    replay = forms.FileField()
    
    def clean_replay(self):
        max_size = 5*10**4
        file_name = self.cleaned_data['replay'].name
        
        if file_name.split('.')[1] != 'itr':
            self._errors['replay'] = [u'You can only upload files with the .itr extension!']
        elif self.cleaned_data['replay'].size > max_size:
            self._errors['replay'] = [u'Max. file size: 50 kB']
            
        return self.cleaned_data['replay']
