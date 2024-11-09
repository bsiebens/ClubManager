# ClubManager

__This is a rewrite of the original ClubManager that is now preserved under https://github.com/bsiebens/clubmanager2. This version should be fully
compatible with the old version (or at least we hope so).__

## Description
ClubManager is an open source sport club management software. It was created out of frustration at 
the lack of good quality tools that exists for managing sports clubs. There are a few tools but either
they are very expensive, slow and difficult to use or just don't work.

As a small and poor sport club we decided to rebuild our website, soon realizing we had quite some data already in our database
to power our website that we could in fact revamp this into something that might rival those expensive commercial tools. Since being
foolish is not a crime, just eats up all of your time, here we are and ClubManager was born.

## Under the hood
ClubManager is a Django powered web application. It should work wherever Django can work.

### Installation
Installation is still very much a manual process. We use poetry during development to track and maintain our development environment,
but any tool that can work with a `pyproject.toml` file should be fine.
1. Download and install the latest version of python and poetry
2. Download a copy of our source
3. Run `poetry install` to create a new virtual environment and install the necessary packages
4. Most configuration can be adjusted once the system is running except the following items (either to be set in `settings.py` or via an environment variable):
   * Secret Key
   * Debug mode (default = False)
   * Database settings
   * Settings for serving and storing static and media files
5. Run `python manage.py migrate`
6. Run `python manage.py createsuperuser`
7. Start the server (either via `python manage.py runserver` or a custom script/daemon)
8. If running via runserver, visit ClubManager via http://localhost:8000

In the future we will probably package this as a docker file, with proper support for environment variables, but we are not there yet (support is always welcome!).

## Support
If you like this and use this yourself, please let us know! We are keen to see if other people find this interesting!

If you like to help us develop this further: feel free to fork and launch a pull request!
