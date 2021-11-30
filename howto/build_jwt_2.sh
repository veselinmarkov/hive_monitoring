#!/bin/bash
PEM="dummy_rsa.privkey"
NOW=$( date +%s )
IAT="${NOW}"
USER="writer"
if [ -z ${1} ]; then NONCE=1; else NONCE=$1; fi
HEADER_RAW='{"typ": "JWT","alg":"RS512"}'
HEADER=$( echo -n "${HEADER_RAW}" | openssl base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n' )
PAYLOAD_RAW='{"username": '\"${USER}\"',"time":'${IAT}', "nonce":'\"${NONCE}\"'}'
PAYLOAD=$( echo -n "${PAYLOAD_RAW}" | openssl base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n' )
HEADER_PAYLOAD="${HEADER}"."${PAYLOAD}"
SIGNATURE=$( openssl dgst -sha512 -sign ${PEM} <(echo -n "${HEADER_PAYLOAD}") | openssl base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n' )
JWT="${HEADER_PAYLOAD}"."${SIGNATURE}"
echo $JWT
