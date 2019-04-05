#!/usr/bin/env python

import os
from os.path import dirname, join
import time

hostfile_name = "m5.cfg" #localserver

proj_dir = dirname(dirname(os.path.realpath(__file__)))
app_dir = join(proj_dir, "build", "app", "kmeans")
hostfile = join(proj_dir, "machinefiles", hostfile_name)

svhn_params = {
    "train_file": "hdfs://ib126:9090/datasets/ml/svhn.scale"
    , "total_num_of_training_samples": 73257
    , "num_epochs": 73257
    , "mini_batch_size": 10
    , "num_centers": 10
    , "dimensionality": 3072
    , "load_clusters_from_disk": "false"  # "false" to use random init
    #, "output_file_prefix": join(app_dir, "output", "out")
    , "output_file_prefix": "hdfs://ib126:9090/user/tati/bosen/kmeans"
    }

sample_params = {
    #"train_file": join(proj_dir, "app/kmeans/dataset/sample.txt")
    "train_file": "hdfs://ib126:9090/datasets/ml/bosen_kmeans_sample.txt"
    , "total_num_of_training_samples": 100
    , "num_epochs": 40
    , "mini_batch_size": 10
    , "num_centers": 10
    , "dimensionality": 10
    , "load_clusters_from_disk": "false"  # "false" to use random init
    #, "output_file_prefix": join(app_dir, "output", "out")
    , "output_file_prefix": "hdfs://ib126:9090/user/tati/bosen/kmeans"
    }

params = svhn_params

petuum_params = {
    "hostfile": hostfile
    , "num_app_threads": 28
    , "staleness": 0
    , "num_comm_channels_per_client": 1 # 1~2 are usually enough.
    }

prog_name = "kmeans_main"
prog_path = join(app_dir, prog_name)

env_params = (
  "GLOG_logtostderr=true "
  "GLOG_v=-1 "
  "GLOG_minloglevel=0 "
  )

ssh_cmd = (
    "ssh "
    "-o StrictHostKeyChecking=no "
    "-o UserKnownHostsFile=/dev/null "
    )


# Get host IPs
with open(hostfile, "r") as f:
  hostlines = f.read().splitlines()
host_ips = [line.split()[1] for line in hostlines]
petuum_params["num_clients"] = len(host_ips)

all_cmd = "stop() {{ parallel-ssh -P -h {0} \"pkill -u `whoami` kmeans_main\"; }}; trap stop INT;".format(join(proj_dir, "m20.cfg"))
for client_id, ip in enumerate(host_ips):
  petuum_params["client_id"] = client_id
  cmd = ssh_cmd + ip + " \""
  if not params["output_file_prefix"].startswith("hdfs://"):
    cmd += "mkdir -p " + join(app_dir, "output") + "; "
  cmd += "export CLASSPATH=`hadoop classpath --glob`:$CLASSPATH; "
  cmd += env_params + " " + prog_path
  cmd += "".join([" --%s=%s" % (k,v) for k,v in petuum_params.items()])
  cmd += "".join([" --%s=%s" % (k,v) for k,v in params.items()])
  cmd += "\" &"
  all_cmd="{0} {1}".format(all_cmd, cmd)

  if client_id == 0:
    # Wait for first client to set up
    all_cmd="{0} sleep 2; ".format(all_cmd)

all_cmd="{0} wait".format(all_cmd)
os.system(all_cmd)
