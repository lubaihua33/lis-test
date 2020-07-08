#!/bin/bash

########################################################################
#
# Linux on Hyper-V and Azure Test Code, ver. 1.0.0
# Copyright (c) Microsoft Corporation
#
# All rights reserved.
# Licensed under the Apache License, Version 2.0 (the ""License"");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION
# ANY IMPLIED WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY OR NON-INFRINGEMENT.
#
# See the Apache Version 2.0 License for specific language governing
# permissions and limitations under the License.
#
########################################################################

LOG_FILE=/tmp/summary.log
function LogMsg() {
    echo $(date "+%a %b %d %T %Y") : ${1} >> ${LOG_FILE}
}

function get_AvailableDisks_azure() {
	for disk in $(lsblk | grep "sd[a-z].*disk" | cut -d ' ' -f1);
	do
		if [ $(df | grep -c $disk) -eq 0 ]; then
			echo $disk
            break
		fi
	done
}

function get_AvailableDisks_aws() {
	for disk in $(lsblk | grep "xvd[a-z].*disk" | cut -d ' ' -f1);
	do
		if [ $(df | grep -c $disk) -eq 0 ]; then
			echo $disk
            break
		fi
	done
}

function ConfigNVME()
{
	namespace_list=$(ls -l /dev | grep -w nvme[0-9]n[0-9]$ | awk '{print $10}')
	nvme_namespaces=""
	for namespace in ${namespace_list}; do
        if [ $(df | grep -c $namespace) -eq 0 ]; then
            sudo nvme format /dev/${namespace}
            sleep 1
            (echo d; echo w) | sudo fdisk /dev/${namespace}
            sleep 1
            sudo bash -c "echo 0 > /sys/block/${namespace}/queue/rq_affinity"
            sleep 1
            nvme_namespaces="${nvme_namespaces}/dev/${namespace}:"
            LogMsg "NMVe name space: $namespace"
            break
        fi
	done
	# Deleting last char of string (:)
	nvme_namespaces=${nvme_namespaces%?}

	# Set the remaining variables
	# NVMe perf tests will have a starting qdepth equal to vCPU number
	startQDepth=$(nproc)
	LogMsg "Setting qdepth in the setting: $startQDepth"
	# NVMe perf tests will have a max qdepth equal to vCPU number x 256
	maxQDepth=$(($(nproc) * 256))
	LogMsg "Setting maxQDepth in the setting: $maxQDepth"
}

if [ $# -lt 1 ]; then
    echo -e "\nUsage:\n$0 disk"
    exit 1
fi
if [ -e /tmp/summary.log ]; then
    sudo rm -rf /tmp/summary.log
fi

DISK="$1"
startQDepth=1
maxQDepth=256
IO_SIZE=(4 1024)
FILE_SIZE=(1000)
IO_MODE=(read randread write randwrite)

if [[ $DISK =~ "azure" ]]; then
    disk=$(get_AvailableDisks_azure)
    DISK=/dev/$disk
elif [[ $DISK =~ "aws" ]]; then
    disk=$(get_AvailableDisks_aws)
    DISK=/dev/$disk
elif [[ $DISK =~ "md" ]]; then
    sudo umount $DISK
elif [[ $DISK =~ "nvme" ]]; then
    ConfigNVME
fi

distro="$(head -1 /etc/issue)"
if [[ ${distro} == *"Ubuntu"* ]]
then
    sudo apt update
    sudo apt -y install sysstat zip fio blktrace bc libaio1 nvme-cli >> ${LOG_FILE}
elif [[ ${distro} == *"Amazon"* ]]
then
    sudo yum clean dbcache>> ${LOG_FILE}
    sudo yum -y install sysstat zip blktrace bc libaio* wget gcc automake autoconf nvme-cli>> ${LOG_FILE}
    cd /tmp; wget http://brick.kernel.dk/snaps/fio-2.21.tar.gz
    tar -xzf fio-2.21.tar.gz
    cd fio-2.21; ./configure; sudo make; sudo make install
    sudo cp /usr/local/bin/fio /usr/bin/fio
else
    LogMsg "Unsupported distribution: ${distro}."
fi

cd /tmp
mkdir -p /tmp/storage

function run_storage ()
{
    qdepth=$1
    io_size=$2
    file_size=$3
    io_mode=$4

    if [[ ${qdepth} -gt 8 ]]
    then
        actual_q_depth=$((${qdepth} / 8))
        num_jobs=8
    else
        actual_q_depth=${qdepth}
        num_jobs=1
    fi

    if [[ $DISK =~ "nvme" ]]; then
        num_jobs=$(nproc)
        actual_q_depth=$((qdepth/num_jobs))
    fi

    FILEIO="fio --size=${file_size}G --direct=1 --ioengine=libaio --filename=${DISK} --overwrite=1 "
	if [[ $DISK =~ "nvme" ]]; then
		FILEIO="fio --direct=1 --ioengine=libaio --filename=${nvme_namespaces} --gtod_reduce=1"
	fi

    LogMsg "======================================"
    LogMsg "Running Test qdepth= ${qdepth} io_size=${io_size} io_mode=${io_mode} file_size=${file_size}"
    LogMsg "======================================"

    iostat -x -d 1 900 2>&1 > /tmp/storage/${qdepth}.${io_mode}.iostat.netio.log &
    vmstat 1 900       2>&1 > /tmp/storage/${qdepth}.${io_mode}.vmstat.netio.log &

    sudo $FILEIO --name=${io_mode} --bs=${io_size}k --iodepth=${actual_q_depth} --runtime=60 --numjobs=${num_jobs} --rw=${io_mode} --group_reporting > /tmp/storage/${io_size}K-${qdepth}-${io_mode}.fio.log

    sudo pkill -f iostat
    sudo pkill -f vmstat

    LogMsg "sleep 20 seconds"
    sleep 30
}

qdepth=$startQDepth
while [ $qdepth -le $maxQDepth ]
do
    for io_size in "${IO_SIZE[@]}"
    do
        for file_size in "${FILE_SIZE[@]}"
        do
            for io_mode in "${IO_MODE[@]}"
            do
                run_storage ${qdepth} ${io_size} ${file_size} ${io_mode}
            done
        done
    done
    qdepth=$((qdepth*2))
done

LogMsg "Kernel Version : `uname -r`"
LogMsg "Guest OS : ${distro}"

cd /tmp
zip -r storage.zip . -i storage/* >> ${LOG_FILE}
zip -r storage.zip . -i summary.log >> ${LOG_FILE}
