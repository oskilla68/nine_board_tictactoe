make all
# a=awk -v min=5 -v max=10 'BEGIN{srand(); print int(min+rand()*(max-min+1))}'
a=$((RANDOM+20000))
./servt -n 10 -p $a & sleep 0.1
# ./agent -p $a & 
# python3 agent.py -p $a & sleep 0.5
./lookt.mac -p $a -d 3 & sleep 0.1
./agent -p $a
# ./randt -p $a
# python3 agent.py -p $a
# python3 test.py -p $a
# ./lookt.mac -p $a -d 3 
