# get old month - 4 months before today
old_month=$(. find_month_to_backup.sh)
if [ ${old_month} = 'NULL' ]; then
  echo "no records older than 3 monts for a backup/delete"
  exit
fi
echo "month $old_month will be backed up and removed"

echo "dumping interval and number of records"
mysql --login-path=local hive -N --batch -e "select min(sample_time), max(sample_time), count(*) from samples where date_format(sample_time,'%Y-%m') = '${old_month}'"
#if [ ! -d backups ]; then mkdir backups; fi
mysqldump --login-path=local hive samples --no-create-info --where="date_format(sample_time,'%Y-%m') = '${old_month}'" | gzip > samples_monthly_dump_${old_month}.bkp.gz
echo "backup file created samples_monthly_dump_${old_month}.bkp.gz"

echo "uploading to AWS S3 bucket s3://hive-monthly-backups"
aws s3 cp samples_monthly_dump_${old_month}.bkp.gz s3://hive-monthly-backups

#deleting the interval
mysql --login-path=local hive -N --batch -e "delete from samples where date_format(sample_time,'%Y-%m') = '${old_month}'"
echo "records deleted"

rm samples_monthly_dump_${old_month}.bkp.gz
echo "backup file removed"

