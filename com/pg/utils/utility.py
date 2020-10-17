import os


def get_mysql_jdbc_url(mysql_config: dict):
    host = mysql_config["mysql_conf"]["hostname"]
    port = mysql_config["mysql_conf"]["port"]
    database = mysql_config["mysql_conf"]["database"]
    return "jdbc:mysql://{}:{}/{}?autoReconnect=true&useSSL=false".format(host, port, database)

def read_from_mysql(spark, app_conf, app_secret):
    jdbcParams = {"url": get_mysql_jdbc_url(app_secret),
                  "lowerBound": "1",
                  "upperBound": "100",
                  "dbtable": app_conf["SB"]["mysql_conf"]["dbtable"],
                  "numPartitions": "2",
                  "partitionColumn": app_conf["SB"]["mysql_conf"]["partition_column"],
                  "user": app_secret["mysql_conf"]["username"],
                  "password": app_secret["mysql_conf"]["password"]
                  }
    print(jdbcParams)

    print("\nReading data from MySQL DB using SparkSession.read.format(),")
    # use the ** operator/un-packer to treat a python dictionary as **kwargs
    txnDF = spark \
        .read.format("jdbc") \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .options(**jdbcParams) \
        .load()

    return txnDF

def read_from_sftp(spark, app_conf, app_secret):
    txnDF = spark \
        .read \
        .format("com.springml.spark.sftp") \
        .option("host", app_secret["sftp_conf"]["hostname"]) \
        .option("port", app_secret["sftp_conf"]["port"]) \
        .option("username", app_secret["sftp_conf"]["username"]) \
        .option("pem", os.path.abspath(current_dir + "/../../../../" + app_secret["sftp_conf"]["pem"])) \
        .option("fileType", "csv") \
        .option("delimiter", "|") \
        .load(app_conf["OL"]["sftp_conf"]["directory"] + app_conf["OL"]["sftp_conf"]["file_name"])

    return txnDF

def read_from_s3(spark, app_conf):
    txnDF = spark \
        .read \
        .csv("s3://" + app_conf["1CP"]["s3_conf"]["s3_bucket"] + "/" + app_conf["1CP"]["s3_conf"]["filename"])

    return txnDF

def read_from_mongodb(spark, app_conf):
    txn_DF = spark \
        .read \
        .format("com.mongodb.spark.sql.DefaultSource") \
        .option("database", app_conf["mongodb_conf"]["database"]) \
        .option("collection", app_conf["mongodb_conf"]["collection"]) \
        .load()

    return txn_DF