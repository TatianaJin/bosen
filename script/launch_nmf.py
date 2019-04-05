#!/usr/bin/env python

import os
from os.path import dirname, join
import time

hostfile_name = "localserver" # m20.cfg

proj_dir = dirname(dirname(os.path.realpath(__file__)))
app_dir = join(proj_dir, "build", "app", "NMF")
hostfile = join(proj_dir, "machinefiles", hostfile_name)

petuum_params = {
    "hostfile": hostfile,
    "num_worker_threads": 4
    }

params = {
    "is_partitioned": 0
    , "load_cache": 0
    , "input_data_format": "text"
    , "output_data_format": "text"
     , "output_path": os.path.join(app_dir, "output")
    #, "output_path": "hdfs://hdfs-domain/user/bosen/dataset/nmf/sample/output"
    , "rank": 3
    , "m": 9
    , "n": 9
    , "num_epochs": 800
    , "minibatch_size": 9
    , "num_iter_L_per_minibatch": 10
    , "num_eval_minibatch": 10
    , "num_eval_samples": 100
    , "init_step_size": 0.05
    , "step_size_offset": 0.0
    , "step_size_pow": 0.0
    , "init_step_size_L": 0.0
    , "step_size_offset_L": 0.0
    , "step_size_pow_L": 0.0
    , "init_step_size_R": 0.0
    , "step_size_offset_R": 0.0
    , "step_size_pow_R": 0.0
    , "init_L_low": 0.5
    , "init_L_high": 1.0
    , "init_R_low": 0.5
    , "init_R_high": 1.0
    , "table_staleness": 0
    , "maximum_running_time": 0.0
     , "data_file": os.path.join(app_dir, "test-matrix")
    #, "data_file": "hdfs://hdfs-domain/user/bosen/dataset/nmf/sample/data/sample.txt"
    , "cache_path": os.path.join(app_dir, "N/A")
    }

prog_name = "nmf_main"
prog_path = os.path.join(app_dir, prog_name)


ssh_cmd = (
    "ssh "
    "-o StrictHostKeyChecking=no "
    "-o UserKnownHostsFile=/dev/null "
    )

env_params = (
  "GLOG_logtostderr=true "
  "GLOG_v=-1 "
  "GLOG_minloglevel=0 "
  )

def main ():
    # Get host IPs
    with open(hostfile, "r") as f:
        hostlines = f.read().splitlines()
        host_ips = [line.split()[1] for line in hostlines]
        petuum_params["num_clients"] = len(host_ips)
    
    if not params["output_path"].startswith("hdfs://"):
      os.system("mkdir -p {0}".format(params["output_path"]))

    all_cmd = "stop() { pkill -u `whoami` " + prog_name + "; }; trap stop INT;"
    for client_id, ip in enumerate(host_ips):
      petuum_params["client_id"] = client_id
      cmd = ssh_cmd + ip + " "
      #cmd += "export CLASSPATH=`hadoop classpath --glob`:$CLASSPATH; "
      cmd += "export CLASSPATH=`hadoop classpath --glob`:$CLASSPATH; "
      cmd += env_params + " " + prog_path
      cmd += "".join([" --%s=%s" % (k,v) for k,v in petuum_params.items()])
      cmd += "".join([" --%s=%s" % (k,v) for k,v in params.items()])
      cmd += " &"
      all_cmd="{0} {1}".format(all_cmd, cmd)

      if client_id == 0:
        all_cmd="{0} sleep 2; ".format(all_cmd)

    all_cmd="{0} wait".format(all_cmd)
    os.system(all_cmd)
    

if __name__ == '__main__':
    main()
