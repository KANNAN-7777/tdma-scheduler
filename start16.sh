cd /mnt/c/Users/kanna/Downloads/TDMA/tdma-scheduler
mkdir -p logs16

for i in $(seq 1 16)
do
    emane -d -f "logs16/node$i.log" "platforms16/platform-$i.xml"
done

sleep 3
pgrep -a emane
