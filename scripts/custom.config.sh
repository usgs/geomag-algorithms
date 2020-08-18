
export SITE_URL="${SITE_URL_PREFIX}geomag${SITE_URL_SUFFIX}";
export BASE_HREF=${BASE_HREF:-ws};
export SERVICE_MAP=(
  "/${BASE_HREF}":'web'
);
# Algorithms Environment Variables
export DATA_HOST=${DATA_HOST:-cwbpub.cr.usgs.gov};
export DATA_PORT=${DATA_PORT:-2060};
export DATA_TYPE=${DATA_TYPE:-edge};
