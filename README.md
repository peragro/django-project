django-project
==============

Project management with tasks, milestones, follow and activity-stream


    git clone https://github.com/peragro/django-project.git
    virtualenv env
    source env/bin/activate
    cd django_project
    pip install -r requirements
    python manage.py migrate --run-syncdb
    Set the superuser for django using python manage.py createsuperuser    
    python manage.py loaddata django_project/fixtures/initial_data.json
    python manage.py runserver
