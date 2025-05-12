# #!/bin/bash
# set -e

# # Optional: Create a Django project if it doesn't exist.
# # If you already have a Django project in this repo, remove or adjust this section.
# if [ ! -f "/usr/src/app/treevaq/manage.py" ]; then
#     django-admin startproject treevaq
# fi

# cd treevaq

# # If you'd like to automatically configure the DB settings, you can add sed commands here.
# # For now, we assume you're manually configuring settings.py to use PostgreSQL.

# # Run migrations
# python manage.py migrate                                                                                                                                                                            

# # Start Django dev server
# exec python manage.py runserver 0.0.0.0:8000

#!/bin/bash
set -e

cd /usr/src/app/treevaq

# Run migrations
python manage.py migrate

# Start Django dev server
exec python manage.py runserver 0.0.0.0:8000