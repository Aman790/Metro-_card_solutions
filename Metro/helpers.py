from Metro.constants import constants
import pymongo



constants = constants['development']


client_metro = pymongo.MongoClient(constants['mongoUrl_metrocardsystem'])

def metro_database():
    metro_db = client_metro[constants['database_metro']]
    col_station = metro_db[constants['col_station']]
    col_card = metro_db[constants['col_card']]
    col_travel_history = metro_db[constants['col_travel_history']]
    return col_station, col_card, col_travel_history