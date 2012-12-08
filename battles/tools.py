from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import struct
import random

def random_string(n):
    code = ''.join([random.choice('abcdefghijklmnoprstuvwyxz0123456789') for i in range(n)])
    return code

def handle_uploaded_file(f, path, replay_name):
    with open('/home/kuba/html/media/'+path+'/'+replay_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
def check_slowdown(text):
    
    sd = 0
    qpc1 = 198
    qpc2 = 199
    tme1 = 202
    tme2 = 203
    dns1 = 206
    dns2 = 207
    flr1 = 209
    flr2 = 210
    flr3 = 211
    cheater = 0
    
    for i in range(214, 960, 20):
        foo = int(struct.unpack('b', text[i:i+1])[0])
        if foo == 72:
            sd +=1

    for i in range(1, sd+1):
    
        qpc1 += 20
        qpc2 += 20
        tme1 += 20
        tme2 += 20
        dns1 += 20
        dns2 += 20
        flr1 += 20
        flr2 += 20
        flr3 += 20
    
        qpc11 = int(struct.unpack('b', text[qpc1:qpc1+1])[0])
        tme11 = int(struct.unpack('b', text[tme1:tme1+1])[0])
        dns11 = int(struct.unpack('b', text[dns1:dns1+1])[0])
        qpc22 = int(struct.unpack('b', text[qpc2:qpc2+1])[0])
        tme22 = int(struct.unpack('b', text[tme2:tme2+1])[0])
        dns22 = int(struct.unpack('b', text[dns2:dns2+1])[0])
    
        # qpc
        if qpc22 == 66 and qpc11 < 128:
            qpc = 32 + (qpc11/4.0) + 0.24
        elif qpc22 == 66 and qpc11 > 127:
            qpc = (qpc11/2) + 0.49
        else:
            qpc = 0
    
        # tme 
        if tme22 == 66 and tme11 < 128:
            tme = 32 + (tme11/4.0)
        elif tme22 == 66 and tme11 > 127:
            tme = (tme11/2)
        else:
            tme = 0
        
        # dns
        if dns22 == 66 and dns11 < 128:
            dns = 32 + (dns11/4.0) + 0.24
        elif dns22 == 66 and dns11 > 127:
            dns = (dns11/2) + 0.49
        else:
            dns = 0
    
        if qpc > 55:
            cheater += 1
        if tme > 55:
            cheater += 1
        if dns > 55:
            cheater += 1
    
        """
        flr values (not required)
        flra = int(struct.unpack('B', text[flr1:flr1+1])[0])
        flrb = int(struct.unpack('B', text[flr2:flr2+1])[0])
        flrc = int(struct.unpack('B', text[flr3:flr3+1])[0])
    
        if flrc == 66:
            flr = flrb/2
        elif flrc == 67:
            if flrb < 128:
                flr = flrb + 128
            else:
                if flra == 128:
                    flr = (flrb*2)+1
                else:
                    flr = (flrb*2)
        elif flrc == 68:
            if flrb < 128:
                if flra == 64:
                    flr = 512 + (4*flrb) + 1
                elif flra == 128:
                    flr = 512 + (4*flrb) + 2
                elif flra == 192:
                    flr = 512 + (4*flrb) + 3
                else:
                    flr = 512 + (4*flrb)
            else:
                if flra == 32:
                    flr = (flrb*8) + 1
                elif flra == 64:
                    flr = (flrb*8) + 2
                elif flra == 96:
                    flr = (flrb*8) + 3
                elif flra == 128:
                    flr = (flrb*8) + 4
                elif flra == 160:
                    flr = (flrb*8) + 5
                elif flra == 192:
                    flr = (flrb*8) + 6
                elif flra == 224:
                    flr = (flrb*8) + 7
                else:
                    flr = frlb*8
        elif flrc == 69:
            if flrb < 128:
                if flra == 16:
                    flr = 2048 + (16*flrb) + 1
                elif flra == 32:
                    flr = 2048 + (16*flrb) + 2
                elif flra == 48:
                    flr = 2048 + (16*flrb) + 3
                elif flra == 64:
                    flr = 2048 + (16*flrb) + 4
                elif flra == 80:
                    flr = 2048 + (16*flrb) + 5
                elif flra == 96:
                    flr = 2048 + (16*flrb) + 6
                elif flra == 112:
                    flr = 2048 + (16*flrb) + 7
                elif flra == 128:
                    flr = 2048 + (16*flrb) + 8
                elif flra == 144:
                    flr = 2048 + (16*flrb) + 9
                elif flra == 160:
                    flr = 2048 + (16*flrb) + 10
                elif flra == 176:
                    flr = 2048 + (16*flrb) + 11
                elif flra == 192:
                    flr = 2048 + (16*flrb) + 12
                elif flra == 208:
                    flr = 2048 + (16*flrb) + 13
                elif flra == 224:
                    flr = 2048 + (16*flrb) + 14
                elif flra == 240:
                    flr = 2048 + (16*flrb) + 15
                else:
                    flr = 2048 + (16*flrb)
        """
        
    return cheater
