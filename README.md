# delta_force-self_defense-django
Django middleware to provide self defense from attack various blind attacks such as SQL injection. Upon fatal errors the middleware generates regular expressions to block requests that cause errors.


# Manual Install

1. Run `pip install -r requirements.txt` to install dependencies
2. Drop secure_app into root of Django application
2. Add secure_app to INSTALLED_APPS in settings.py
3. Add secure_app.middlewares.Repair to MIDDLEWARE_CLASSES in settings.py
