#!/usr/bin/env bash
# Sources: https://github.com/vishnubob/wait-for-it/blob/master/wait-for-it.sh
#          https://github.com/eficode/wait-for/blob/master/wait-for

WAITFORIT_cmdname=${0##*/}

# parse arguments: look for a timeout flag and a single HOST:PORT
TIMEOUT=15
PROTOCOL=
while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--timeout)
      shift
      TIMEOUT="$1"
      shift
      ;;
    http://*|https://*)
      if [ -n "$PROTOCOL" ]; then
        echo "More than one host/port specified"
        exit 1
      fi
      WAITFORIT_HOST="$1"
      PROTOCOL="http"
      shift
      ;;
    *:*)
      if [ -n "$PROTOCOL" ]; then
        echo "More than one host/port specified"
        exit 1
      fi
      WAITFORIT_HOST=$(printf "%s\n" "$1"| cut -d : -f 1)
      WAITFORIT_PORT=$(printf "%s\n" "$1"| cut -d : -f 2)
      PROTOCOL="tcp"
      shift
      ;;
    *)
      echo "Unknown option '$1'"
      exit 1
      ;;
  esac
done

WAITFORIT_start_ts=$(date +%s)

case "$PROTOCOL" in
    tcp)
      echo "$WAITFORIT_cmdname: waiting $TIMEOUT seconds for $WAITFORIT_HOST:$WAITFORIT_PORT"
      timeout "$TIMEOUT" bash -c 'until printf "" 2>>/dev/null >>/dev/tcp/$0/$1; do sleep 1; done' "$WAITFORIT_HOST" "$WAITFORIT_PORT"
      ;;
    http)
      echo "$WAITFORIT_cmdname: waiting $TIMEOUT seconds for $WAITFORIT_HOST"
      if ! type wget &> /dev/null; then
        echo "Unable to wait for http endpoint $WAITFORIT_HOST: wget isn't installed"
        exit 1
      fi
      timeout "$TIMEOUT" bash -c 'until wget --timeout=1 -q "$0" -O /dev/null > /dev/null 2>&1; do sleep 1; done' "$WAITFORIT_HOST"
      ;;
    *)
      echo "Unknown protocol: '$PROTOCOL'"
      exit 1
      ;;
esac

RESULT=$?

if [ $RESULT -eq 0 ] ; then
    WAITFORIT_end_ts=$(date +%s)
    case "$PROTOCOL" in
        tcp)
          echo "$WAITFORIT_cmdname: $WAITFORIT_HOST:$WAITFORIT_PORT is available after $((WAITFORIT_end_ts - WAITFORIT_start_ts)) seconds"
          ;;
        http)
          echo "$WAITFORIT_cmdname: $WAITFORIT_HOST is available after $((WAITFORIT_end_ts - WAITFORIT_start_ts)) seconds"
          ;;
    esac
else
    case "$PROTOCOL" in
        tcp)
          echo "$WAITFORIT_cmdname: $WAITFORIT_HOST:$WAITFORIT_PORT was not available after $TIMEOUT seconds"
          ;;
        http)
          echo "$WAITFORIT_cmdname: $WAITFORIT_HOST was not available after $TIMEOUT seconds"
          ;;
    esac
fi

exit $RESULT

