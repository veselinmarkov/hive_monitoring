
JWT=$(./build_jwt_2.sh)
#echo $JWT
curl -X post --header "Content-Type: application/json" --header "Authorization: JWT ${JWT}" \
-d '{"hive": 9, "sample_time": "2020-06-30T20:05:00Z", "temp_low": "28.823", "temp_high": null, "temp_hot": "31.663", "temp_out": 24, "temp_target": "-10.000", "humi_in": "47.13", "humi_out": null, "heat_pwr": 0, "fan": 758, "mode": "monitor", "heater_breakers": 10}' -v \
http://127.0.0.1:8000/api/sample/

JWT=$(./build_jwt_2.sh 2)
curl -X delete --header "Content-Type: application/json" --header "Authorization: JWT ${JWT}" -v \
'http://127.0.0.1:8000/api/sample/?sample=2020-06-30T20:05:00.000Z&hive=9'
