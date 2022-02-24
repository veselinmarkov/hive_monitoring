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
-d '{"hive":1, "time_stamp":"2020-06-30T20:05:00Z", "t_heated_air":32.69, "t_hive_air":0.00, 
            "t_ambient_air":23.81, "fan_frequency":2233, "heater_power":0, "heater_register":0, 
            "heater_pwm":0, "t_target":9.00, "heating_mode":"monitor", "pid_previous_deviation":0.00, 
            "pid_deviation":0.00, "pid_integral":0.00, "pid_derivative":0.00, "pid_output":0.00, 
            "humidity_hive_air":0.00, "t_hive_ceiling":33.38, "heater_breakers":10}' -v \
"${HOST}/api/sample/"


JWT=$(./build_jwt_2.sh 2)
curl -X DELETE --header "Content-Type: application/json" --header "Authorization: JWT ${JWT}" -v \
"${HOST}/api/sample/?sample=2020-06-30T20:05:00.000Z&hive=1"
