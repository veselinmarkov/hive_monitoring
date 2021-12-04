#!/bin/bash
if [ -z ${1} ] 
    then echo " Please, specify the test host url as a parameter"
    echo "  default host ed1f29b.online-server.cloud assumed"
    HOST="ed1f29b.online-server.cloud"
    else HOST=${1}
fi

JWT=$(./build_jwt_2.sh 1)
#echo $JWT
curl --header "Content-Type: application/json" --header "Authorization: JWT ${JWT}" \
-d '{"hive": 9, "sample_time": "2020-06-30T20:05:00Z", "temp_low": "28.823", "temp_high": null, "temp_hot": "31.663", "temp_out": 24, "temp_target": "-10.000", "humi_in": "47.13", "humi_out": null, "heat_pwr": 0, "fan": 758, "mode": "monitor", "heater_breakers": 10}' -v \
"${HOST}/api/sample/"


JWT=$(./build_jwt_2.sh 2)
curl -X DELETE --header "Content-Type: application/json" --header "Authorization: JWT ${JWT}" -v \
"${HOST}/api/sample/?sample=2020-06-30T20:05:00.000Z&hive=9"
