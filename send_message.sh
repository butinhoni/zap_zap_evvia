#!/bin/bash

send_message() {
  local numero="$1"
  local message="$2"
  whatsapp-cli send --to "$numero" --message "$message"
}

if [ "$1" == "send_message" ]; then
  shift
  send_message "$@"
fi
