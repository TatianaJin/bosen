if [ $# -lt 1 ]
then
  echo 'usage: ./generate_machine_file.sh <n_machines>'
  exit
fi
n_machines=$1
port=23233
hostname_prefix=172.16.105.

output=machinefiles/m$n_machines.cfg
rm -f $output
for i in `seq 1 $n_machines`
do
  echo $((i-1)) ${hostname_prefix}$((i+30)) $port >> $output
done
