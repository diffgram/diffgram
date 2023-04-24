from flasgger import APISpec, Schema, Swagger, fields
import json


def setup_swagger(app):
    with app.app_context():
        from flasgger import Swagger
        app.config['SWAGGER'] = {
            'title': 'Diffgram Default API'
        }
        swagger = Swagger(app, template = {
            "swagger": "2.0",
            "info": {
                "title": "Diffgram Default API",
                "version": "1.0",
            },
            "consumes": [
                "application/json",
            ],
            "produces": [
                "application/json",
            ],
        })
        data = swagger.get_apispecs()
        path = "docs/swagger_spec.json"
        with open(path, "w") as write_file:
            json.dump(data, write_file, indent = 4)
        return path