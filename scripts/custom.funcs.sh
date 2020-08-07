# This file contains any custom functions / hooks for the geomag-algorithms
# deployment process.

preStackDeployHook () {
  writeYmlFile;
}

##
# Write a customized YML file for deploying the stack. Necessary because
# by default, YML files do not allow variables for defining configs.
##
writeYmlFile () {
  local ymlFileName="${APP_NAME}.yml";
  local configName="assets-$(date +%H%M%S)-$$";

  cat <<-EO_YML > ${ymlFileName}
version: "3.5"
services:
  # Do not change the name of the "web" service without also updating the
  # custom.funcs.sh and the custom.config.sh as well. Probably just do not
  # ever do this...
  web:
    image: ${REGISTRY}/${IMAGE_NAME}
    deploy:
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
        window: 120s
      replicas: 3
      update_config:
        order: start-first
        parallelism: 3
    ports:
      - 8000:8000
    environment:
      - BASE_HREF=${BASE_HREF}
      - DATA_HOST=${DATA_HOST}
      - DATA_PORT=${DATA_PORT}
      - DATA_TYPE=${DATA_TYPE}
      - SITE_URL=${SITE_URL}
    configs:
      - source: ${configName}
EO_YML
}
