from flask import Flask, render_template
from flask import request
import xmltodict
import requests
import json
import geocoder


app = Flask(__name__)
@app.route("/")
def index():
    url = "http://127.0.0.1:5000/stations"
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.content)
    type_list = data[0]
    district_list = data[1]
    input_data = '''<form action="" method="GET"><label for="type">Type: </label><select name="type" method="GET" action="/" id="type">'''
    for value in data[0]:
        input_data += '<option value ="'+value+'">'+value+'</option>'
    input_data += '</select><br>'
    input_data += '''<label for="district">District: </label><select name="district" method="GET" action="/" id="district">'''
    for value in data[1]:
        input_data += '<option value ="'+value+'">'+value+'</option>'
                
    input_data += '''
                <input type="submit" value="Find Charging Stations">
            </form>
                  '''

    i_district = request.args.get("district", "")
    i_type = request.args.get("type", "")
    i_max = 3
    if i_district and i_type:
        usercord = usercord_from()
        i_lat, i_lng = usercord.split(' ',1)
    else:
        i_lat=i_lng=''
        output = "Missing input data"
    try:
        data = { "lat" : i_lat, "lng" : i_lng, "type" : i_type, "district" : i_district, "max" : i_max}
        response = requests.request("POST", url, json=data, headers=headers)
        data = json.loads(response.content)
        data.sort(key=call_distance)
        output = ''
        for value in data:
            output += 'Address: '
            output += value['address']
            output += '<br>'
            output += 'Type: '
            output += value['type']
            output += '<br>'
            if value['parkingNo'] != None:
                output += 'Parking Number: '
                output += value['parkingNo']
                output += '<br>'
            output += 'Distance: '
            if float(value['distance']) > 1:
                output += str("{:.2f}".format(float(value['distance'])))
                output += 'km'
            else:
                output += str("{:.2f}".format(1000*float(value['distance'])))
                output += 'm'
            output += '<br>'
            output += '\n'
            output += '<br><meta http-equiv="refresh" content="15">'
            valid_check = True
    except:
        valid_check = False
    if not (valid_check):
        return (
           ''
           + input_data
        )
    else:
        return (
            ''
            + output
        )
def call_distance(e):
    return e['distance']
def usercord_from():
    """Convert coordinates to user's cords."""
    try:
        usercord = geocoder.ip('me')
        return str(usercord.lat)+' '+ str(usercord.lng)
    except ValueError:
        return "invalid input"
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
