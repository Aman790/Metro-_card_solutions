from flask_classful import FlaskView, route
from flask import Flask, request, jsonify
from Metro.helpers import metro_database
import hashlib
import random
import string
import redis
from datetime import datetime
from email_validator import validate_email, EmailNotValidError


# initialising redis to store punch out history as travel history
r = redis.StrictRedis(decode_responses=True)



col_station, col_card, col_travel_history = metro_database()



now = datetime.now()

# function to hash items
def hash_item(item):
    hashed_item = hashlib.md5(str(item).encode('utf-8')).hexdigest()
    return hashed_item


class MetroCardSolution(FlaskView):
    # api to create some stations
    @route('/create_station', methods=['POST'])
    def create_station(self):
        station_data = request.json['station_data']
        col_station.insert_one(station_data)
        return jsonify({"message": "station created successfully", "station_data": station_data})


    # api to create metro card
    @route('/create_card', methods=['POST'])
    def create_card(self):
        card_data = request.json['card_data']
        card_mapped_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        card_data['card_mapped_id'] = hash_item(card_mapped_id)
        email = card_data['email']
        if col_card.find_one({"email":email}):
            return jsonify({"message": "card has already been registered to user"})
        else:
            valid = validate_email(email)
            if not valid:
                return jsonify({"message":"email is not valid"})
            card_data['balance'] = 500
            col_card.insert_one(card_data)
            return jsonify({"message": "card created successfully"})

    @route('/get_card_details', methods=['GET'])
    def get_card_details(self):
        card_mapped_id = request.args['card_mapped_id']
        card_data = col_card.find_one({"card_mapped_id":card_mapped_id})
        del card_data['_id']
        return jsonify({"message": "card_details fetched successfuly", "card_details": card_data})

    # api to punch in metro card
    @route('/punch_in', methods=['POST'])
    def punch_in(self):
        punchin = {}
        punchin_data = request.json['punchin_data']
        email = punchin_data['email']
        card_data = col_card.find_one({"email":email})
        if not card_data:
            return jsonify({"message":"Invalid user email"})
        if card_data['is_valid'] == False:
            return jsonify({"message":"card is not valid"})
        else:
            if card_data['is_blocked'] == True:
                return jsonify({"message": "card is blocked"})
            else:
                if card_data['balance'] < 15:
                    return jsonify({"message":"please recharge your card"})
                else:
                    punchin['email'] = email
                    punchin['start_time'] = now.strftime("%d%m%Y %H%M%S")
                    punchin['start_station_code'] = punchin_data['start_station_code']
                    punchin['balance'] = card_data['balance']
                    hash_name = card_data['card_mapped_id']
                    r.hmset(hash_name, punchin)
        return jsonify({"message":"card punched in"})


    # api to punch out metro card
    @route('/punched_out', methods=['POST'])
    def punched_out(self):
        travel_history = []
        travel_history_dict = {}
        punchout_data= request.json['punchout_data']
        email = punchout_data['email']
        card_data = col_card.find_one({"email":email})
        hash_name = card_data['card_mapped_id']
        punchin_data = r.hgetall(hash_name)
        start_time = punchin_data['start_time']
        start_station_code = int(punchin_data['start_station_code'])
        end_time = now.strftime("%d%m%Y %H%M%S")
        end_station_code = int(punchout_data['end_station_code'])
        num_stations = abs(end_station_code - start_station_code)
        left_stations = num_stations - 3
        balance = card_data['balance']
        if num_stations <= 3:
            balance = balance - 15
        elif num_stations == 4:
            balance = balance - (left_stations * 5) - 15
        elif num_stations >= 5:
            rem = num_stations // 5
            balance = balance - (left_stations * 5) + (5/100)*50*rem - 15
        elif balance < 0:
            return jsonify({"message": "Insufficient balance to exit the metro"})
        else:
            card_data['balance'] = balance
            col_card.update_one({"email":email}, {"$set": card_data})
            travel_history_dict[str(start_station_code)] = start_time
            travel_history_dict[str(end_station_code)] = end_time
            travel_history.append(travel_history_dict)
            col_travel_history.insert_one(travel_history_dict)
            return jsonify({"message":"punched out successfully"})



    #api to recharge metro card
    route('/recharge', methods=['POST'])
    def recharge_data(self):
        recharge_data = request.json['recharge_data']
        amount = recharge_data['amount']
        card_mapped_id = recharge_data['card_mapped_id']
        card_data = col_card.find_one({"card_id":card_mapped_id})
        if card_data:
            card_data['balance'] += amount
        email = card_data['email']
        col_card.update_one({"email":email}, {"$set":card_data})
        return jsonify({"message": "Recharge successfull", "Amount": amount})