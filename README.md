# alastair
The Alastair Cooking App is a tool that can help you to organize the food for events. Through a consistent database and an easy to use frontend, you will never have to struggle with food cost estimations and no ideas about the shopping list again!

# Installation
To install it, you will need python-django and python-django-crispy-forms. It should run both with python 2 and 3, no guarantee though. Also, you will need to install a mysql-server.

To install, at first modify alastair_cookie/settings.py to fit your needs. You will need to set another database, dbuser and dbpassword, and maybe you may disable debug mode (Yeah, I know, I forgot to remove the password from the settings.py, but don't worry, I changed mine ^^)

Then you should be able to run the command
```
python manage.py syncdb
```

This should create some database tables in the db and ask you to set up a superuser for the system. After this is done, import the create_views.sql into your Database (do this through phpmyadmin, the command line mysql client or whatever you prefer)

Then you should be able to run
```
python manage.py runserver
```

This starts the server, you can also pass a port and an IP where it will listen to
```
python manage.py runserver 0.0.0.0:8080
```

And you are done, you should have a working copy of alastair. You can reach the admin panel over localhost:8000/admin
