# alastair
The Alastair Cooking App is a tool that can help you to organize the food for events. Through a consistent database and an easy to use frontend, you will never have to struggle with food cost estimations and no ideas about the shopping list again!

# Installation
To install it, you will need python-django (at least 1.8) and python-django-crispy-forms. Check your distributions packet manager on how to install them. Alternatively you can just run
```
pip install django
pip install django-crispy-forms
```

Alastair should run both with python 2 and 3, no guarantee though. Also, I recommend you to install a mysql-server for better performance.

As Python modules, you will need to install mysqlclient:
```
pip install msqlclient
```

To set everything up, modify alastair_cookie/settings.py to fit your needs. If you use mysql, you will need to set another database, dbuser and dbpassword. If you want to run in production mode, which I can not recommend as everything is not really stable yet, change DEBUG to False.

You are strongly advised to change the secret key; I left that one in there so you can run it out of the box.

Then you should be able to run the command
```
python manage.py syncdb
```
And your system should be ready.


# Running

To start the server, simply type
```
python manage.py runserver
```

You can also pass a port and an IP where it will listen to
```
python manage.py runserver 0.0.0.0:8000
```

You should now have a working copy of alastair at localhost:8000, the django admin is reachable via localhost:8000/admin
But as you still read these lines, obviously something went wrong. So don't hesitate to contact me or open an issue on github!