from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class AddResource(Resource):
    def post(self):
        """
        This function handles the POST request to the '/api/add' endpoint.
        It accepts two numbers as input and returns their sum.
        """
        try:
            num1 = float(request.json['num1'])
            num2 = float(request.json['num2'])
        except (KeyError, ValueError):
            return jsonify({'error': 'Both num1 and num2 must be floating point numbers.'}), 400

        result = num1 + num2
        return jsonify({'result': result})

api.add_resource(AddResource, '/api/add')

if __name__ == '__main__':
    app.run(debug=True)
