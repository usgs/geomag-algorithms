# This file contains any custom functions / hooks for the geomag-algorithms
# deployment process.

preStackDeployHook () {
  writeYmlFile;
}


##
# override the default updateRouting, which adds a trailing slash...
##
updateRouting () {
  local appName=$1; shift;
  local stackName=$1; shift;
  local serviceMap=$@;

  local dir="$(pwd -P)";
  local stamp=$(date);

  local configFile="${dir}/${appName}.conf";
  local serverFile="${dir}/${appName}.server";
  local upstreamIdx=0;

  debug "Re-routing traffic to ${stackName} stack.";
  echo "# Auto generated ${stamp} for ${stackName}" > $configFile;
  echo "# Auto generated ${stamp} for ${stackName}" > $serverFile;

  for service in ${serviceMap[@]}; do
    local name="${stackName}_$(echo $service | awk -F: '{print $2}')";
    local upstreamName="${name}_${upstreamIdx}";
    local path="$(echo $service | awk -F: '{print $1}')";
    local port=$(getPublishedPort $name 2> /dev/null);

    if [ -z "${port}" ]; then
      # No port exposed. Continue.
      debug "No port exposed for ${name}. Not routing. Moving on.";
      continue;
    fi

    echo "upstream ${upstreamName} {" >> $configFile;
    for host in ${TARGET_HOSTS[@]}; do
      echo "  server ${host}:${port};" >> $configFile;
    done
    echo "}" >> $configFile;

    cat <<- EO_SERVER_SNIP >> $serverFile
      # do not include trailing slash here, map can if needed
      location ${path} {
        proxy_pass http://${upstreamName};
        proxy_connect_timeout 5s;
        proxy_set_header Host \$host;
        proxy_set_header X-Client-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        # keep redirects on https
        proxy_redirect http://\$host:\$port https://\$host;
      }
		EO_SERVER_SNIP
    # ^^ Note: TAB indentation required

    upstreamIdx=$((upstreamIdx + 1));
  done

  if [ $(configsDiffer ${appName} ${configFile} ${serverFile}) ]; then
    debug "Updating configuration for ${appName}";
    routerConfig --update ${appName} ${configFile} ${serverFile};
  else
    debug "${appName} configuration not changed. Skipping router update.";
  fi
}


##
# Write a customized YML file for deploying the stack. Necessary because
# by default, YML files do not allow variables for defining configs.
##
writeYmlFile () {
  local ymlFileName="${APP_NAME}.yml";

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
      - 8000
    environment:
      - BASE_HREF=${BASE_HREF}
      - DATA_HOST=${TARGET_HOSTNAME}
      - DATA_PORT=${DATA_PORT}
      - DATA_TYPE=${DATA_TYPE}
      - SITE_URL=${SITE_URL}
      - WEBSERVICE=true
EO_YML
}
