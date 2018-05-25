pybot -L TRACE -b debug.log -P resources \
      -v host:cirrus-demo.tw.rdlabs.hpecorp.net \
      Cirrus_REST_no_dependent/Reservation.robot

pybot -L TRACE -b debug.log -P resources \
      -v host:cirrus-demo.tw.rdlabs.hpecorp.net \
      --dryrun -r none -l none -o none \
      Cirrus_REST_no_dependent/Reservation.robot
