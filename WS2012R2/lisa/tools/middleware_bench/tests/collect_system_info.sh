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
TestName=$1
mkdir -p /tmp/${TestName}
LOG_FILE=/tmp/${TestName}/system_info.log
echo "=>lscpu:" >> ${LOG_FILE}
lscpu >> ${LOG_FILE}
echo -e >> ${LOG_FILE}

echo "=>lspci:" >> ${LOG_FILE}
lspci >> ${LOG_FILE}
echo -e >> ${LOG_FILE}

echo "=>free -g" >> ${LOG_FILE}
free -g >> ${LOG_FILE}
echo -e >> ${LOG_FILE}

echo "=>fdisk -l" >> ${LOG_FILE}
fdisk -l >> ${LOG_FILE}
echo -e >> ${LOG_FILE}

echo "cat /proc/cpuinfo" >> ${LOG_FILE}
cat /proc/cpuinfo >> ${LOG_FILE}

