# KKDB_ABSOLUTE_PATH="/home/osman/caylak/code/python/tgbots/kto_karatay_duyuru_bot"
KKDB_ABSOLUTE_PATH=`dirname $(readlink -f $0)`
cd $KKDB_ABSOLUTE_PATH
mkdir -p logs

echo -e "$(/bin/date)\tBEGIN cron_tasks.sh" >> logs/script_logs.txt

source env/bin/activate
python cli.py cron_tasks 2>&1 >> logs/runtime_logs.txt

echo -e "$(/bin/date)\tEND cron_tasks.sh" >> logs/script_logs.txt
