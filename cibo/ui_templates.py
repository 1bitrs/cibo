REDOC_TEMPLATE = """
<!DOCTYPE html>
<html>

  <head>
    <title>Redoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% if config.REDOC_USE_GOOGLE_FONT %}
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    {% endif %}
    <link rel="icon" type="image/png" href="{{ config.DOCS_FAVICON }}">
    <style>
      body {
        margin: 0;
        padding: 0;
      }
    </style>
  </head>

  <body>
    <div id="redoc"></div>

    <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"> </script> // 
    <script>
      Redoc.init(
        "{{ url_for('openapi.spec') }}",
        {},
        document.getElementById("redoc")
      )
    </script>
  </body>

</html>
"""

DOCS_TEMPLATE = """

"""
