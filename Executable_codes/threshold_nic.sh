#!/bin/bash

FILE="/tmp/wifi_out.pcap"
FILE2="/tmp/wifi_in.pcap"
FLOWGRAPH="wifi_transceiver_threshold.py"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

### create fifo
if [ -e ${FILE} ]
then
	echo "${FILE}: file already exists"
	if ! [ -p ${FILE} ]
	then
		echo "ERROR: ${FILE} exists and is not a FIFO"
		exit 1
	fi
else
	echo "creating fifo: ${FILE}"
	mkfifo ${FILE}
fi

### create fifo
if [ -e ${FILE2} ]
then
	echo "${FILE2}: file already exists"
	if ! [ -p ${FILE2} ]
	then
		echo "ERROR: ${FILE2} exists and is not a FIFO"
		exit 1
	fi
else
	echo "creating fifo: ${FILE2}"
	mkfifo ${FILE2}
fi

### create tap interface
if [[ `ifconfig -a | grep tap0 | wc -l` -eq 0 ]]
then
	sudo ip tuntap add dev tap0 user ${USER} mode tap
fi

### reconfigure it in any case, just to be sure it's up
sudo ifconfig tap0 down
sudo ifconfig tap0 hw ether ba:09:87:65:43:21
sudo ifconfig tap0 mtu 440
sudo ifconfig tap0 up
sudo ifconfig tap0 192.168.123.2

sudo route del -net 192.168.123.0/24 
sudo route add -net 192.168.123.0/24 mss 400 dev tap0

sudo tc qdisc del dev tap0 root
sudo tc qdisc add dev tap0 root netem delay 10ms

sudo arp -s 192.168.123.1 12:34:56:78:90:ab -i tap0






### start transceiver
cd ${DIR}
cd ../examples/
./${FLOWGRAPH} &
sleep 1


### start wireshark
wireshark -k -i ${FILE} &

### start wireshark
wireshark -k -i ${FILE2} &


sleep 1



### start netcat
echo "##########################################################################"
echo "### starting netcat. Just type and the lines will be send to the flowgraph"
echo "##########################################################################"
sleep 2

#echo | nc -u localhost 52001
cat


