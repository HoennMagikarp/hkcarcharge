from flask import Flask, request
import requests
import xmltodict
import haversine as hs
import json
app = Flask(__name__)

url = requests.get("https://opendata.clp.com.hk/GetChargingSectionXML.aspx?lang=EN")
data = xmltodict.parse(url.text)


@app.route('/stations', methods=['GET', 'POST'])
def main():
   if request.method == 'GET':
       return list_type_and_district()
   elif request.method == "POST":
       return get_distance_station(request.get_json(force=True))

def list_type_and_district():
   avaliable_type = []
   avaliable_district = []
   avaliable_check = [False, False]
   for value in data['ChargingStationData']['stationList']['station']:
      for x in avaliable_type:
         if value['type'] == x:
            avaliable_check[0] = True
            break
      for x in avaliable_district:
         if value['districtS'] == x:
            avaliable_check[1] = True
            break
      
      if not avaliable_check[0]:
         avaliable_type.append(value['type'])
      if not avaliable_check[1]:
         avaliable_district.append(value['districtS'])
      avaliable_check = [False, False]
   avaliable_type.append('All')
   colon_list = []
   for value in avaliable_type:
      if ';' in value:
         colon_list.append(value)
   for value in colon_list:
      avaliable_type.remove(value)
   e = json.dumps([avaliable_type, avaliable_district])
   return e

def get_distance_station(inputted):
   in_lat = str(inputted['lat'])
   in_lng = str(inputted['lng'])
   in_district = str(inputted['district'])
   in_type = inputted['type']
   in_max = int(inputted['max'])
   avaliable_type = []
   avaliable_check = False
   i=0
   for value in data['ChargingStationData']['stationList']['station']:
      for x in avaliable_type:
         if value['type'] == x:
            avaliable_check = True
            break
      if not avaliable_check:
         avaliable_type.append(value['type'])
      avaliable_check = False
   colon_list = []
   for value in avaliable_type:
      if ';' in value:
         colon_list.append(value)
   for value in colon_list:
      avaliable_type.remove(value)
   avaliable_check = False
   for value in avaliable_type:
      if str(value) == in_type or in_type == 'All':
         avaliable_check = True
         break
   if not avaliable_check:
      e = 'type not supported, avaliable types: '+str(avaliable_type)
      return e
   if in_max < 1:
      e = 'max value must be larger than 0'
      return e
   if in_max > len(data['ChargingStationData']['stationList']['station']):
      in_max = len(data['ChargingStationData']['stationList']['station'])
   from geopy.geocoders import Nominatim
   geoLoc = Nominatim(user_agent="GetLoc")
   locname = geoLoc.reverse((in_lat)+' '+(in_lng))
   if locname.raw['address']['state'] != '香港 Hong Kong':
       raise Exception('inputted location is outside of Hong Kong')
   nomineeList = []
   distanceList = []
   for i in range(in_max+1):
      nomineeList.append('')
      distanceList.append(0)
   i = -1
   usercord = tuple(map(float, (in_lat + ' ' + in_lng).split(' ')))
   if in_district and in_max and in_type:
      for value in data['ChargingStationData']['stationList']['station']:
         if in_district == value['districtS'] and (in_type in value['type'] and ';' in value['type'] or in_type == value['type'] or in_type == 'All'):
            i += 1
            nomineeData =tuple(map(float, (value['lat']+' '+value['lng']).split(' ')))
            if i > int(in_max):
               nomineeList[in_max] = value
               distanceList[in_max] = hs.haversine(nomineeData,usercord)
               indexx = distanceList.index(max(distanceList))
               del nomineeList[indexx]
               del distanceList[indexx]
               nomineeList.append('')
               distanceList.append(0)
            else:
               nomineeList[i] = value
               distanceList[i] = hs.haversine(nomineeData,usercord)
   nomineeList = list(filter(('').__ne__, nomineeList))
   distanceList = list(filter((0).__ne__, distanceList))
   i = 0
   for value in distanceList:
      nomineeList[i]['distance']=value
      i += 1
   e = json.dumps(nomineeList)
   
   return e
   
if __name__ == '__main__':
    app.run() 
