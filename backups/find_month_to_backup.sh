mysql --login-path=local hive -N --batch -e "select date_format(min(sample_time),'%Y-%m') from samples where sample_time < date_sub(now(), interval 4 month )"
#mysql --login-path=local hive -N --batch -e "select date_format(min(sample_time),'%Y-%m') from samples where sample_time < date_sub('2020-02-15', interval 4 month )"

