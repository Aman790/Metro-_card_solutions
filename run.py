from flask import Flask
from Metro.metro_systems import MetroCardSolution


app = Flask(__name__)


MetroCardSolution.register(app, route_base='/')

if __name__ == '__main__':
    app.run(debug=True)
