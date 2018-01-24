#!/bin/bash
( 
  sleep 1;
  echo $2
  sleep 1;
  echo sys
  sleep 1;
  echo $3
  sleep 2;
  echo qu
  echo qu 
) | telnet $1
