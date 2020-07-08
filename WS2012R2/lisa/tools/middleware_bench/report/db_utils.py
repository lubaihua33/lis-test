"""
Linux on Hyper-V and Azure Test Code, ver. 1.0.0
Copyright (c) Microsoft Corporation

All rights reserved
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See the Apache Version 2.0 License for specific language governing
permissions and limitations under the License.
"""
import os
import sys
import pprint
import logging
import ConfigParser

from sqlalchemy import Table, Column, Date, DECIMAL, INT, BIGINT, NVARCHAR, MetaData, create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import create_session, mapper


logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%y/%m/%d %H:%M:%S', level=logging.INFO)
log = logging.getLogger(__name__)

COLUMNS = [{'name': 'TestCaseName', 'type': NVARCHAR(50)},
           {'name': 'DataPath', 'type': NVARCHAR(10)},
           {'name': 'TestDate', 'type': Date},
           {'name': 'HostBy', 'type': NVARCHAR(50)},
           {'name': 'HostOS', 'type': NVARCHAR(100)},
           {'name': 'HostType', 'type': NVARCHAR(50)},
           {'name': 'InstanceSize', 'type': NVARCHAR(20)},
           {'name': 'GuestOS', 'type': NVARCHAR(50)},
           {'name': 'GuestSize', 'type': NVARCHAR(50)},
           {'name': 'GuestOSType', 'type': NVARCHAR(50)},
           {'name': 'GuestDistro', 'type': NVARCHAR(50)},
           {'name': 'KernelVersion', 'type': NVARCHAR(50)},
           {'name': 'DiskSetup', 'type': NVARCHAR(20)},
           {'name': 'TestMode', 'type': NVARCHAR(30)},
           {'name': 'FileTestMode', 'type': NVARCHAR(20)},
           {'name': 'WebServerVersion', 'type': NVARCHAR(20)},
           {'name': 'MySqlVersion', 'type': NVARCHAR(20)},
           {'name': 'PhpVersion', 'type': NVARCHAR(20)},
           {'name': 'Driver', 'type': NVARCHAR(10)},
           {'name': 'IPVersion', 'type': NVARCHAR(4)},
           {'name': 'ProtocolType', 'type': NVARCHAR(3)},
           {'name': 'ClusterSetup', 'type': NVARCHAR(25)},
           {'name': 'CpuNumber', 'type': INT},
           {'name': 'MemorySize_G', 'type': INT},
           {'name': 'CpuSpeed_MHZ', 'type': DECIMAL(12, 3)},
           {'name': 'HypervisorVendor', 'type': NVARCHAR(20)},
           {'name': 'HadoopVersion', 'type': NVARCHAR(12)},
           {'name': 'Threads', 'type': DECIMAL(4, 0)},
           {'name': 'BufferSize_Bytes', 'type': DECIMAL(5, 0)},
           {'name': 'TestConnections', 'type': DECIMAL(4, 0)},
           {'name': 'NumberOfConnections', 'type': INT},
           {'name': 'TestPipelines', 'type': DECIMAL(4, 0)},
           {'name': 'TestConcurrency', 'type': DECIMAL(4, 0)},
           {'name': 'NodeSize_bytes', 'type': DECIMAL(4, 0)},
           {'name': 'TeragenRecords', 'type': DECIMAL(12, 0)},
           {'name': 'SortDuration_sec', 'type': DECIMAL(10, 4)},
           {'name': 'TotalCreatedCallsPerSec', 'type': DECIMAL(10, 4)},
           {'name': 'TotalSetCallsPerSec', 'type': DECIMAL(10, 4)},
           {'name': 'TotalGetCallsPerSec', 'type': DECIMAL(10, 4)},
           {'name': 'TotalDeletedCallsPerSec', 'type': DECIMAL(10, 4)},
           {'name': 'TotalWatchedCallsPerSec', 'type': DECIMAL(10, 4)},
           {'name': 'TotalQueries', 'type': DECIMAL(9, 0)},
           {'name': 'TransactionsPerSec', 'type': DECIMAL(8, 3)},
           {'name': 'DeadlocksPerSec', 'type': DECIMAL(8, 3)},
           {'name': 'RWRequestsPerSec', 'type': DECIMAL(10, 3)},
           {'name': 'NumberOfAbInstances', 'type': DECIMAL(3, 0)},
           {'name': 'ConcurrencyPerAbInstance', 'type': DECIMAL(3, 0)},
           {'name': 'Document_bytes', 'type': DECIMAL(7, 0)},
           {'name': 'CompleteRequests', 'type': DECIMAL(7, 0)},
           {'name': 'RequestsPerSec', 'type': DECIMAL(8, 3)},
           {'name': 'TransferRate_KBps', 'type': DECIMAL(10, 3)},
           {'name': 'MeanConnectionTimes_ms', 'type': DECIMAL(8, 4)},
           {'name': 'TotalRequests', 'type': DECIMAL(9, 0)},
           {'name': 'ParallelClients', 'type': DECIMAL(5, 0)},
           {'name': 'Payload_bytes', 'type': DECIMAL(5, 0)},
           {'name': 'ConnectionsPerThread', 'type': DECIMAL(8, 0)},
           {'name': 'RequestsPerThread', 'type': DECIMAL(8, 0)},
           {'name': 'BestLatency_ms', 'type': DECIMAL(7, 4)},
           {'name': 'WorstLatency_ms', 'type': DECIMAL(7, 4)},
           {'name': 'AverageLatency_ms', 'type': DECIMAL(7, 4)},
           {'name': 'BestOpsPerSec', 'type': DECIMAL(10, 3)},
           {'name': 'WorstOpsPerSec', 'type': DECIMAL(10, 3)},
           {'name': 'AverageOpsPerSec', 'type': DECIMAL(10, 3)},
           {'name': 'SETRequestsPerSec', 'type': DECIMAL(10, 3)},
           {'name': 'GETRequestsPerSec', 'type': DECIMAL(10, 3)},
           {'name': 'NumOutstandingSmall_IO', 'type': DECIMAL(3, 0)},
           {'name': 'NumOutstandingLarge_IO', 'type': DECIMAL(3, 0)},
           {'name': 'BlockSize_Kb', 'type': DECIMAL(3, 0)},
           {'name': 'BlockSize_KB', 'type': INT},
           {'name': 'QDepth', 'type': INT},
           {'name': 'Throughput_MBps', 'type': DECIMAL(10, 2)},
           {'name': 'Latency95Percentile_ms', 'type': DECIMAL(10, 2)},
           {'name': 'RequestsExecutedPerSec', 'type': DECIMAL(10, 2)},
           {'name': 'Latency_ms', 'type': DECIMAL(7, 3)},
           {'name': 'Latency_sec', 'type': DECIMAL(8, 4)},
           {'name': 'IOPS', 'type': DECIMAL(10, 2)},
           {'name': 'TotalOpsPerSec', 'type': DECIMAL(10, 4)},
           {'name': 'ReadOps', 'type': DECIMAL(9, 1)},
           {'name': 'ReadLatency95Percentile_us', 'type': DECIMAL(6, 0)},
           {'name': 'CleanupOps', 'type': DECIMAL(9, 1)},
           {'name': 'CleanupLatency95Percentile_us', 'type': DECIMAL(6, 0)},
           {'name': 'UpdateOps', 'type': DECIMAL(9, 1)},
           {'name': 'UpdateLatency95Percentile_us', 'type': DECIMAL(6, 0)},
           {'name': 'ReadFailedOps', 'type': DECIMAL(9, 1)},
           {'name': 'ReadFailedLatency95Percentile_us', 'type': DECIMAL(6, 0)},
           {'name': 'Throughput_Gbps', 'type': DECIMAL(5, 3)},
           {'name': 'SenderCyclesPerByte', 'type': DECIMAL(5, 2)},
           {'name': 'ReceiverCyclesPerByte', 'type': DECIMAL(5, 2)},
           {'name': 'SenderCpuUsePercent', 'type': DECIMAL(5, 2)},
           {'name': 'ReceiverCpuUsePercent', 'type': DECIMAL(5, 2)},
           {'name': 'RetransSegments', 'type': DECIMAL(12, 2)},
           {'name': 'LostRetrans', 'type': DECIMAL(12, 2)},
           {'name': 'SenderCpuBusyPercent', 'type': DECIMAL(8, 2)},
           {'name': 'ReceiverCpuBusyPercent', 'type': DECIMAL(8, 2)},
           {'name': 'ConnectionsCreatedTime', 'type': INT},           
           {'name': 'Latency_ms', 'type': DECIMAL(9, 3)},
           {'name': 'PacketSize_KBytes', 'type': DECIMAL(5, 3)},
           {'name': 'MaxLatency_us', 'type': DECIMAL(9, 3)},
           {'name': 'AverageLatency_us', 'type': DECIMAL(9, 3)},
           {'name': 'MinLatency_us', 'type': DECIMAL(9, 3)},
           {'name': 'Latency95Percentile_us', 'type': DECIMAL(9, 3)},
           {'name': 'Latency99Percentile_us', 'type': DECIMAL(9, 3)},
           {'name': 'Percentile_50', 'type': INT},
           {'name': 'Percentile_75', 'type': INT},
           {'name': 'Percentile_90', 'type': INT},
           {'name': 'Percentile_99.9', 'type': INT},
           {'name': 'Percentile_99.99', 'type': INT},
           {'name': 'Percentile_99.999', 'type': INT},
           {'name': 'Latency95thPercentile_us', 'type': DECIMAL(8, 1)},
           {'name': 'Latency99thPercentile_us', 'type': DECIMAL(8, 1)},
           {'name': 'RxThroughput_Gbps', 'type': DECIMAL(5, 3)},
           {'name': 'TxThroughput_Gbps', 'type': DECIMAL(5, 3)},
           {'name': 'RetransmittedSegments', 'type': DECIMAL(6, 0)},
           {'name': 'CongestionWindowSize_KB', 'type': DECIMAL(6, 0)},
           {'name': 'SendBufSize_KBytes', 'type': DECIMAL(9, 0)},
           {'name': 'DatagramLoss', 'type': DECIMAL(5, 3)},
           {'name': 'seq_read_iops', 'type': DECIMAL(8, 1)},
           {'name': 'seq_read_lat_usec', 'type': DECIMAL(10, 2)},
           {'name': 'seq_read_iops_stdev', 'type': DECIMAL(8, 1)},
           {'name': 'seq_read_lat_usec_stdev', 'type': DECIMAL(10, 2)},
           {'name': 'seq_read_clat_percentil_90', 'type': INT},
           {'name': 'seq_read_clat_percentil_99', 'type': INT},
           {'name': 'seq_read_cpu_usr', 'type': DECIMAL(6, 2)},
           {'name': 'seq_read_cpu_sys', 'type': DECIMAL(6, 2)},
           {'name': 'seq_read_cpu_ctx', 'type': INT},
           {'name': 'seq_read_free_mem', 'type': INT},
           {'name': 'rand_read_iops', 'type': DECIMAL(8, 1)},
           {'name': 'rand_read_lat_usec', 'type': DECIMAL(10, 2)},
           {'name': 'rand_read_iops_stdev', 'type': DECIMAL(8, 1)},
           {'name': 'rand_read_lat_usec_stdev', 'type': DECIMAL(10, 2)},
           {'name': 'rand_read_clat_percentil_90', 'type': INT},
           {'name': 'rand_read_clat_percentil_99', 'type': INT},
           {'name': 'rand_read_cpu_usr', 'type': DECIMAL(6, 2)},
           {'name': 'rand_read_cpu_sys', 'type': DECIMAL(6, 2)},
           {'name': 'rand_read_cpu_ctx', 'type': INT},
           {'name': 'rand_read_free_mem', 'type': INT},
           {'name': 'seq_write_iops', 'type': DECIMAL(8, 1)},
           {'name': 'seq_write_lat_usec', 'type': DECIMAL(10, 2)},
           {'name': 'seq_write_iops_stdev', 'type': DECIMAL(8, 1)},
           {'name': 'seq_write_lat_usec_stdev', 'type': DECIMAL(10, 2)},
           {'name': 'seq_write_clat_percentil_90', 'type': INT},
           {'name': 'seq_write_clat_percentil_99', 'type': INT},
           {'name': 'seq_write_cpu_usr', 'type': DECIMAL(6, 2)},
           {'name': 'seq_write_cpu_sys', 'type': DECIMAL(6, 2)},
           {'name': 'seq_write_cpu_ctx', 'type': INT},
           {'name': 'seq_write_free_mem', 'type': INT},
           {'name': 'rand_write_iops', 'type': DECIMAL(8, 1)},
           {'name': 'rand_write_lat_usec', 'type': DECIMAL(10, 2)},
           {'name': 'rand_write_iops_stdev', 'type': DECIMAL(8, 1)},
           {'name': 'rand_write_lat_usec_stdev', 'type': DECIMAL(10, 2)},
           {'name': 'rand_write_clat_percentil_90', 'type': INT},
           {'name': 'rand_write_clat_percentil_99', 'type': INT},
           {'name': 'rand_write_cpu_usr', 'type': DECIMAL(6, 2)},
           {'name': 'rand_write_cpu_sys', 'type': DECIMAL(6, 2)},
           {'name': 'rand_write_cpu_ctx', 'type': INT},
           {'name': 'rand_write_free_mem', 'type': INT},
           {'name': 'ScaleFactor', 'type': DECIMAL(4, 0)},
           {'name': 'SQLServerVersion', 'type': NVARCHAR(20)},
           {'name': 'ResponseTime95thPercentile', 'type': DECIMAL(8, 3)},
           {'name': 'TxnPerSec', 'type': DECIMAL(10, 2)},
           {'name': 'PostgreSQLVersion', 'type': NVARCHAR(20)},
           {'name': 'TransactionType', 'type': NVARCHAR(50)},
           {'name': 'TestClients', 'type': DECIMAL(3, 0)},
           {'name': 'ScalingFactor', 'type': DECIMAL(5, 0)},
           {'name': 'TestDuration_s', 'type': DECIMAL(5, 0)},
           {'name': 'TransactionsPerSecIncEstablishing', 'type': DECIMAL(8, 3)},
           {'name': 'TransactionsPerSecExcEstablishing', 'type': DECIMAL(8, 3)},
           {'name': 'DataSize_bytes', 'type': DECIMAL(4, 0)},
           {'name': 'Loops', 'type': DECIMAL(3, 0)},
           {'name': 'Groups', 'type': DECIMAL(3, 0)},
           {'name': 'WorkerThreads', 'type': DECIMAL(3, 0)},
           {'name': 'MessageThreads', 'type': DECIMAL(3, 0)},
           {'name': 'Device', 'type': NVARCHAR(4)},
           {'name': 'BenchmarkCommitHash', 'type': NVARCHAR(42)},
           {'name': 'BatchSize', 'type': INT},
           {'name': 'WorkloadName', 'type': NVARCHAR(20)},
           {'name': 'Model', 'type': NVARCHAR(15)},
           {'name': 'TensorflowVersion', 'type': NVARCHAR(10)},
           {'name': 'RunsPerSec', 'type': DECIMAL(6, 3)},
           {'name': 'ImagesPerSec', 'type': DECIMAL(7,3)},
           {'name': 'NumGpus', 'type': INT},
           {'name': 'NodejsVersion', 'type': NVARCHAR(10)},
           {'name': 'DataFormat', 'type': NVARCHAR(10)},
           {'name': 'Distortions', 'type': INT},
           {'name': 'RuntimeSec', 'type': DECIMAL(15,7)},
           {'name': 'TaskName', 'type': NVARCHAR(200)},
           {'name': 'TrackName', 'type': NVARCHAR(15)},
           {'name': 'ElasticsearchVersion', 'type': NVARCHAR(10)},
           {'name': 'TotalYoungGenGC_s', 'type': DECIMAL(10, 4)},
           {'name': 'TotalOldGenGC_s', 'type': DECIMAL(10, 4)},
           {'name': 'IndexSize_GB', 'type': DECIMAL(15, 6)},
           {'name': 'TotallyWritten_GB', 'type': DECIMAL(15, 6)},
           {'name': 'IndexMinDocsPerSec', 'type': DECIMAL(10, 2)},
           {'name': 'IndexMedianDocsPerSec', 'type': DECIMAL(10, 2)},
           {'name': 'IndexMaxDocsPerSec', 'type': DECIMAL(10, 2)},
           {'name': 'Latency50thPercentile_ms', 'type': DECIMAL(15, 6)},
           {'name': 'Latency90thPercentile_ms', 'type': DECIMAL(15, 6)},
           {'name': 'Latency99thPercentile_ms', 'type': DECIMAL(15, 6)},
           {'name': 'Latency999thPercentile_ms', 'type': DECIMAL(15, 6)},
           {'name': 'Latency100thPercentile_ms', 'type': DECIMAL(15, 6)},
           {'name': 'ServiceTime50thPercentile_ms', 'type': DECIMAL(15, 6)},
           {'name': 'ServiceTime90thPercentile_ms', 'type': DECIMAL(15, 6)},
           {'name': 'ServiceTime99thPercentile_ms', 'type': DECIMAL(15, 6)},
           {'name': 'ServiceTime999thPercentile_ms', 'type': DECIMAL(15, 6)},
           {'name': 'ServiceTime100thPercentile_ms', 'type': DECIMAL(15, 6)},
           {'name': 'ErrorRate_percent', 'type': DECIMAL(5, 3)},
           {'name': 'MinOpsPerSec', 'type': DECIMAL(15, 3)},
           {'name': 'MedianOpsPerSec', 'type': DECIMAL(15, 3)},
           {'name': 'MaxOpsPerSec', 'type': DECIMAL(15, 3)},
           {'name': 'KafkaVersion', 'type': NVARCHAR(10)},
           {'name': 'ReplicationFactor', 'type': INT},
           {'name': 'PartitionNum', 'type': INT},
           {'name': 'BufferMem', 'type': DECIMAL(12, 0)},
           {'name': 'RecordNum', 'type': DECIMAL(12, 0)},
           {'name': 'RecordSize', 'type': INT},
           {'name': 'BatchSize', 'type': INT},
           {'name': 'RecordsPerSec', 'type': DECIMAL(15, 6)},
           {'name': 'MaxLatency_ms', 'type': DECIMAL(10, 4)},
           {'name': 'Latency50Percentile_ms', 'type': DECIMAL(10, 2)},
           {'name': 'Latency95Percentile_ms', 'type': DECIMAL(10, 2)},
           {'name': 'Latency99Percentile_ms', 'type': DECIMAL(10, 2)},
           {'name': 'Latency999Percentile_ms', 'type': DECIMAL(10, 2)},
           ]


def upload_results(localpath=None, table_name=None, results_path=None, parser=None,
                   other_table=False, **kwargs):
    """
    Connect to DB and upload results
    """
    if localpath:
        log.info('Looking up DB details in {}\*.config.' .format(localpath))
        db_creds_file = [os.path.join(localpath, c) for c in os.listdir(localpath)
                         if c.endswith('.config')][0]
        # read credentials from file - should be present in the localpath provided to runner
        config = ConfigParser.ConfigParser()
        config.read(db_creds_file)
    else:
        log.error('No credentials file path provided. Skipping results upload.')
        return None

    test_results = parser(log_path=results_path, **kwargs).process_logs()

    pprint.pprint(test_results)
    if 'linux' in sys.platform:
        driver = config.get('Credentials', 'Driver_linux')
    else:
        driver = config.get('Credentials', 'Driver_windows')

    if other_table:
        temp = table_name.split('_')
        temp.insert(2, config.get('Credentials', 'Other_table'))
        table_name = '_'.join(temp)

    e = create_engine('mssql+pyodbc://{}:{}@{}/{}?driver={}'.format(
            config.get('Credentials', 'User'), config.get('Credentials', 'Password'),
            config.get('Credentials', 'Server'), config.get('Credentials', 'Database'), driver,
            poolclass=NullPool, convert_unicode=True, echo=True))
    metadata = MetaData(bind=e)

    table_columns = [column for column in COLUMNS if column['name'] in test_results[0]]
    t = Table(table_name, metadata,
              Column('TestId', BIGINT, primary_key=True, nullable=False, index=True),
              *(Column(column['name'], column['type']) for column in table_columns))

    # When creating db is also necessary
    # metadata.create_all(checkfirst=True)

    class TestResults(object):
        def __getitem__(self, item):
            return getattr(self, item)

        def __setitem__(self, item, value):
            return setattr(self, item, value)

    mapper(TestResults, t)
    session = create_session(bind=e, autocommit=False, autoflush=True)

    for row in test_results:
        test_data = TestResults()
        for k, v in row.items():
            test_data[k] = v
        session.add(test_data)
        try:
            session.commit()
        except Exception as ex:
            log.exception(ex)
            print("Failed to commit {} data. Rolling back.".format(row))
            session.rollback()
            raise
