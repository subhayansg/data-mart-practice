import os
import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_date

from com.pg.utils.utility import read_from_mysql, read_from_sftp, read_from_s3, read_from_mongodb

if __name__ == "__main__":

    # Step 1. Read configuration files
    current_dir = os.path.abspath(os.path.dirname(__file__))
    # print(current_dir)
    # D:\Workspace\data - mart - practice\com\pg
    app_config_file = os.path.abspath(current_dir + "/../../" + "application.yml")
    app_secret_file = os.path.abspath(current_dir + "/../../" + ".secrets")
    conf = open(app_config_file)
    app_conf = yaml.load(conf, Loader=yaml.FullLoader)
    secrets = open(app_secret_file)
    app_secret = yaml.load(secrets, Loader=yaml.FullLoader)

    # Step 2. Create SparkSession
    spark = SparkSession \
        .builder \
        .master("local[*]") \
        .config("spark.mongodb.input.uri", app_secret["mongodb_conf"]["uri"]) \
        .appName("Read ingestion data from enterprise applications") \
        .getOrCreate()

    spark.sparkContext.setLogLevel('ERROR')

    # Iterate through the sources
    src_list = app_conf["source_list"]
    for src in src_list:
        if src == 'SB':
            # Step 3. Read data from mysql database and write into staging area
            sb_df = read_from_mysql(spark, app_conf, app_secret) \
                .withColumn("ins_dt", current_date())
            sb_df.show()
            sb_df.write \
                .partitionBy("ins_dt") \
                .mode("append") \
                .parquet("s3a://" + app_conf["s3_conf"]["s3_bucket"] + app_conf["s3_conf"]["staging_area"])

        elif src == 'OL':
            # Step 4. Read sftp data and write into staging area
            ol_df = read_from_sftp(spark, app_conf, app_secret) \
                .withColumn("ins_dt", current_date())
            ol_df.show()
            ol_df.write \
                .partitionBy("ins_dt") \
                .mode("append") \
                .parquet("s3a://" + + app_conf["s3_conf"]["s3_bucket"] + "/" + app_conf["s3_conf"]["staging_area"])

        elif src == '1CP':
            # Step 5. Read s3 bucket data and write into staging area
            cp_df = read_from_s3(spark, app_conf) \
                .withColumn("ins_dt", current_date())
            cp_df.show()
            cp_df.write \
                .partitionBy("ins_dt") \
                .mode("append") \
                .parquet("s3a://" + + app_conf["s3_conf"]["s3_bucket"] + "/" + app_conf["s3_conf"]["staging_area"])

        elif src == 'CUST_ADDR':
            # Step 6. Read data from mongodb and write into staging area
            cust_df = read_from_mongodb(spark, app_conf) \
                .withColumn("inst_dt", current_date())
            cust_df.show()
            cust_df.write \
                .partitionBy("ins_dt") \
                .mode("append") \
                .parquet("s3a://" + + app_conf["s3_conf"]["s3_bucket"] + "/" + app_conf["s3_conf"]["staging_area"])

# spark-submit --packages "org.apache.hadoop:hadoop-aws:2.7.4" data-mart-practice/com/pg/source_data_loading.py




