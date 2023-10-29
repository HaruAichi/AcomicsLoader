# AcomicsLoader

Acomics serial image grabber v.0.6

One more picture loader for acomics.ru :)

## Usage: 

Acomics_Loader.py [-h] [-r] [-b FIRST_PAGE] [-e LAST_PAGE] URL [DIR]


## Positional arguments:
-  **URL** : Comic URL https://acomics.ru/~NAME or just NAME

-  **DIR** : Optional directory path to save pages

## Optional arguments:
-  **-h**, **--help**  : Show this help message and exit

-  **-r**, **--rewrite** :  Rewrite existing files

-  **-b FIRST_PAGE**, **--first-page FIRST_PAGE** : First page number

-  **-e LAST_PAGE**,  **--last-page LAST_PAGE** : Last page number

-  **-n**,  **--new** : Load new pictures only

## Change log:

- Version 0.6 (2023-10-29) : Minor fixes, README update

- Version 0.5 (2023-10-29) : Ctrl-C: SIGINT handler added

- Version 0.4 (2023-10-29) : --new key added, some first-last page fixes

- Version 0.3 (2023-10-21) : ageRestrict cookie set to avoid content limitations

- Version 0.2 (2023-06-23) : --info key added

- Version 0.1 (2023-06-16) : Initial release

