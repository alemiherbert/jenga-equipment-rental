# Jenga Equipment Rental
An equipment rental service

## Note
The fixed calling `jinja2.Markup` without an argument has been deprecated, as per Jinja2 v3.01.
This is however still used in the `flask-feather` extension, and will no doubt lead to some errors. To correct these, change the import in the file `venv/lib/python3.8/site-packages/flask_feather/extension.py` from
```(python)
from jinja2 import Markup
```
to
```(python)
from markupsafe import Markup
```

## Image Credits
1. Hero Section Photo <br>
Photo by <a href="https://unsplash.com/@jasonjarr?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Jason Jarrach</a> on <a href="https://unsplash.com/photos/orange-and-black-heavy-equipment-on-brown-sand-7deCnQFcrUw?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>
      