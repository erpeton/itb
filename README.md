# Icy Tower Battle v0.2

**Description**

Icy Tower Battle is a place where you can play with players from around the world. You can battle in any of the following categories: Combo, Floor, NML, CC1, CC2, CC3, CC4, CC5, JS1, JS2, JS3, JS4 or JS5, in all possible settings of floor size, speed and gravity! When you upload a replay, the script will check whether the game was slowed down and whether the password for the battle is correct. But first...

Get a rank!

After creating a new account and logging in, send us replays with your records in Combo, Floor and NML. This will allow us to assign you a rank depending on your skill. For each category, you can get up to 10 points, which makes 30 points in total. Ranks are assigned for meeting appropriate score ranges (Combo 1430, Floor 2390 and NML 1955 are world records - when someone beats them, the ranges will change accordingly).

(1200) (points: 1-3) (level: Good!) 
(1300) (points: 4-6) (level: Sweet!) 
(1400) (points: 7-9) (level: Great!) 
(1500) (points: 10-12) (level: Super!) 
(1600) (points: 13-15) (level: Wow!) 
(1700) (points: 16-18) (level: Amazing!) 
(1800) (points: 19-21) (level: Extreme!) 
(1900) (points: 22-24) (level: Fantastic!) 
(2000) (points: 25-27) (level: Splendid!) 
(2100) (points: 28-30) (level: No Way!)

Info! 

* you can participate in at most three battles at the same time 
* the minimum duration of a battle is one hour, the maximum - 48 hours 
* when you create a new battle, you can specify the floor size, speed and gravity, the category (Combo, Floor, NML, CC1-CC5, JS1-JS5) and the rank threshold (for example, if you set the threshold to "over 1500", players ranked below 1500 will be unable to join the battle) 
* created battles are visible in the "Join battle" section (the "waiting room"), where other logged in users can sign up 
* when the second player joins, the creator can accept (the "Accept" section) or reject (the "Reject" section) his request. The second player (the joining one) can sign out at any time (the "Cancel" section), but he can only cancel the match if the battle is still in the waiting room 
* if the first player accepts the request, the battle becomes official and is now visible in the "Show battles" section 
* the moment the battle begins, the players receive a six-character password in the "Show battles" section, which they'll have to put in the "comment" field of the replay. There will also be a link to the current state of the battle (the results, and when and by whom have the replays yet been sent) 
* when the round is over, the battle is moved to the archive (the "Archive" section) and the participants' new ranks are being calculated. There are four possibilities: a win, a loss, a draw and a quitting. A 0-0 score is not a draw, but a quitting. A quitting (= not sending a replay) means -40 points penalty for the quitting player. In the case of a draw, the player with a lower rank gains points and the one with a higher rank loses them.

**Requirements**

* Django 1.4.2 or higher (at the moment, 1.4.2 is the latest official version)

**Demo** (this site will be removed soon, so don't take it seriously ;p):

[Icy Tower Battle v0.2 - demo site](http://kuba.norma.uberspace.de/itb/battles/)

**Screenshots**

[Icy Tower Battle v0.2 - screenshots](https://github.com/erpeton/itb/tree/master/screenshots)

**Installation (on uberspace.de):**

    $ git clone git@github.com:erpeton/itb.git
    $ cd itb
    $ vim itb/settings.py (#set correctly: DATABASES, TIME_ZONE, MEDIA_ROOT, MEDIA_URL, STATIC_ROOT, STATIC_URL)

    $ mkdir /home/your_username/html/media
    $ mkdir /home/your_username/html/media/records
    $ mkdir /home/your_username/html/media/replays
    $ mkdir /home/your_username/html/static
    $ cp -a static/. /home/kuba/html/static/

    $ python2.7 manage.py syncdb
    $ python2.7 add_first_user.py
    $ chmod +x cron.py
    $ crontab -e 

    1 * * * * /home/your_username/itb/cron.py
