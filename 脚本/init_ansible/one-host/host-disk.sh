#!/bin/bashi
#
disk=$1
size=$2
echo "n\np\n1\n\n\nt\n8e\nw\n" | fdisk /dev/${disk}
pvcreate /dev/${disk}1
vgextend axon /dev/${disk}1
lvextend -L +${size}G /dev/axon/apps
resize2fs /dev/axon/apps
