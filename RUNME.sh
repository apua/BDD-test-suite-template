#! /bin/sh

pybot -L TRACE -b debug.log -P . \
      -v host:cirrus-demo.tw.rdlabs.hpecorp.net \
      Reservation.robot

pybot -L TRACE -b debug.log -P . \
      -v host:cirrus-demo.tw.rdlabs.hpecorp.net \
      --dryrun -r none -l none -o none \
      Reservation.robot
