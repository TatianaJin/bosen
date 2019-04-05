#!/usr/bin/env python3

import os
from os.path import dirname, join
import time

hostfile_name = "m20.cfg" #localserver

proj_dir = dirname(dirname(os.path.realpath(__file__)))
app_dir = join(proj_dir, "build", "app", "mlr")
hostfile = join(proj_dir, "machinefiles", hostfile_name)

#print("Project dir: {0}".format(proj_dir))
#print("App dir: {0}".format(app_dir))

enwiki50_params = {
    "train_file": "hdfs://ib126:9090//datasets/ml/ml-bosen-enwiki_50g_f262144_p20/part"
    , "test_file": "hdfs://ib126:9090/datasets/ml/webspam_20/part"
    , "w_table_num_cols": 1000
    , "global_data": "false"
    , "perform_test": "false"
    , "use_weight_file": "false"
    , "weight_file": ""
    , "num_epochs": 30
    , "num_batches_per_epoch": 1
    , "init_lr": 0.01 # initial learning rate
    , "lr_decay_rate": 0.99 # lr = init_lr * (lr_decay_rate)^T
    , "num_batches_per_eval": 400
    , "num_train_eval": 10000 # compute train error on these many train.
    , "num_test_eval": 1000
    , "lambda": 0.01
    #, "output_file_prefix": join(app_dir, "out")
    , "output_file_prefix": "hdfs://ib126:9090/user/tati/bosen/mlr"
    }

webspam_params = {
    "train_file": "hdfs://ib126:9090/datasets/ml/webspam_20/part"
    , "test_file": "hdfs://ib126:9090/datasets/ml/webspam_20/part"
    , "global_data": "false"
    , "perform_test": "false"
    , "use_weight_file": "false"
    , "weight_file": ""
    , "num_epochs": 20
    , "num_batches_per_epoch": 1
    , "init_lr": 0.01 # initial learning rate
    , "lr_decay_rate": 0.99 # lr = init_lr * (lr_decay_rate)^T
    , "num_batches_per_eval": 400
    , "num_train_eval": 10000 # compute train error on these many train.
    , "num_test_eval": 1000
    , "lambda": 0.01
    #, "output_file_prefix": join(app_dir, "out")
    , "output_file_prefix": "hdfs://ib126:9090/user/tati/bosen/mlr"
    }

svhn_params = {
    "train_file": "hdfs://ib126:9090/datasets/ml/svhn.scale"
    , "test_file": "hdfs://ib126:9090/datasets/ml/svhn.scale"
    , "global_data": "true"
    , "perform_test": "false"
    , "use_weight_file": "false"
    , "weight_file": ""
    , "num_epochs": 10
    , "num_batches_per_epoch": 1
    , "init_lr": 0.01 # initial learning rate
    , "lr_decay_rate": 0.99 # lr = init_lr * (lr_decay_rate)^T
    , "num_batches_per_eval": 400
    , "num_train_eval": 10000 # compute train error on these many train.
    , "num_test_eval": 1000
    , "lambda": 0
    #, "output_file_prefix": join(app_dir, "out")
    , "output_file_prefix": "hdfs://ib126:9090/user/tati/bosen/mlr"
    }


sample_params = {
    "train_file": join(proj_dir, "app/mlr/datasets/covtype.scale.train.small")
    , "test_file": join(proj_dir, "app/mlr/datasets/covtype.scale.test.small")
    #"train_file": "hdfs://ib126:9090/datasets/ml/bosen_kmeans_sample.txt"
    #, "test_file": "hdfs://ib126:9090/datasets/ml/bosen_kmeans_sample.txt"
    , "global_data": "true"
    , "perform_test": "true"
    , "use_weight_file": "false"
    , "weight_file": ""
    , "num_epochs": 400
    , "num_batches_per_epoch": 10
    , "init_lr": 0.01 # initial learning rate
    , "lr_decay_rate": 0.99 # lr = init_lr * (lr_decay_rate)^T
    , "num_batches_per_eval": 100
    , "num_train_eval": 10000 # compute train error on these many train.
    , "num_test_eval": 20
    , "lambda": 0
    #, "output_file_prefix": join(app_dir, "out")
    , "output_file_prefix": "hdfs://ib126:9090/user/tati/bosen/mlr"
    }

params = enwiki50_params

petuum_params = {
    "hostfile": hostfile
    , "num_app_threads": 20
    , "staleness": 0
    , "num_comm_channels_per_client": 1 # 1~2 are usually enough.
    }

prog_name = "mlr_main"
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

if not params["output_file_prefix"].startswith("hdfs://"):
  os.system("mkdir -p " + join(app_dir, "output"))

all_cmd = "stop() {{ parallel-ssh -P -h {0} \"pkill -u `whoami` mlr_main\"; }}; trap stop INT;".format(join(proj_dir, "m20.cfg"))
for client_id, ip in enumerate(host_ips):
  petuum_params["client_id"] = client_id
  cmd = ssh_cmd + ip + " "
  #cmd += "export CLASSPATH=`hadoop classpath --glob`:$CLASSPATH; "
  cmd += env_params + " " + prog_path
  cmd += "".join([" --%s=%s" % (k,v) for k,v in petuum_params.items()])
  cmd += "".join([" --%s=%s" % (k,v) for k,v in params.items()])
  cmd += " &"
  all_cmd="{0} {1}".format(all_cmd, cmd)

  if client_id == 0:
    #print("Waiting for first client to set up")
    #time.sleep(2)
    all_cmd="{0} sleep 2; ".format(all_cmd)

all_cmd="{0} wait".format(all_cmd)
os.system(all_cmd)
