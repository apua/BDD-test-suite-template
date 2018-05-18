 #!/bin/bash
 # Usage: bash xvfb.sh
 i=$(ps -ef|grep Xvfb|grep -v 'grep'|awk '{print $2}')
 if [ "$i" == "" ]; then
     echo "Kicking off Xvfb..."
     export DISPLAY=:1
     Xvfb :1 -screen 0 1280x900x24 2>/dev/null &
 fi
 i=$(ps -ef|grep Xvfb|grep -v 'grep'|awk '{print $2}')
 echo Xvfb $i is running
 i=$(ps -ef|grep x11vnc|grep -v 'grep'|awk '{print $2}')
 if [ "$i" == "" ]; then
     echo "Kick off x11vnc..."
     echo -ne '\n\n' | x11vnc -display :1  2>/dev/null &
 fi
 echo "x11vnc is activating -> IP address:5900"

