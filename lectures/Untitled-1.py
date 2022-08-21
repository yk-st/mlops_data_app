from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql import SparkSession
import pyspark.sql.functions as F


df2 = spark.read.csv("/Users/saitouyuuki/Desktop/src/mlops_data_app/files/datafile/user_activity.csv",header=True)
df2 = df2.select(F.col('id').cast("integer"),F.col('money').cast("integer"))
predict,train=df2.randomSplit([0.6,0.4],785)
train =train.groupby('id').agg(F.sum('money').alias('money'))
train_vector = VectorAssembler(inputCols = ['money'], outputCol = "features").transform(train)
kmeans = KMeans().setK(2).setSeed(1)
model = kmeans.fit(train_vector)


predict =predict.groupby('id').agg(F.sum('money').alias('money'))
predict_vector = VectorAssembler(inputCols = ['money'], outputCol = "features").transform(train)
predictions = model.transform(predict_vector)

into_kvs = predictions.select('id','prediction')



# to mongo db
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import Row
spark = SparkSession \
    .builder \
    .appName("mongodbtest1") \
    .config("spark.mongodb.input.uri", "mongodb://action:pass123@mongo_data_mlops:27017/user_prediction") \
    .config("spark.mongodb.output.uri", "mongodb://action:pass123@mongo_data_mlops:27017/user_prediction") \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
    .getOrCreate()

pyspark --packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.2 \
        --conf spark.mongodb.input.uri=mongodb://action:pass123@mongo_data_mlops:27017/user_prediction \
        --conf spark.mongodb.output.uri=mongodb://action:pass123@mongo_data_mlops:27017/user_prediction

df = spark.sql("select 1 as id, 0 as predictions union all select 2 as id, 1 as predictions")
df.repartition(1).write.mode("overwrite").option("compression","gzip").csv("/home/pyspark/hoge")

# parquetの場合
df = spark.read.parquet("")

df.repartition(1).write \
    .format('com.mongodb.spark.sql.DefaultSource') \
    .option( "uri", "mongodb://action:pass123@mongo_data_mlops:27017/user_prediction.prediction") \
    .save()

# mongoへの接続
mongo -u action -p pass123 user_prediction

db.prediction.find()
db.prediction.find({id:1})
db.prediction.find({id:1},{predictions:1, _id:0})

データ
> db.prediction.find()
{ "_id" : ObjectId("62ee12d7f4c0fd4e165552af"), "id" : 1, "predictions" : 0 }
{ "_id" : ObjectId("62ee12d7f4c0fd4e165552b0"), "id" : 2, "predictions" : 1 }
> db.prediction.find({id:'1'})
> 
> db.prediction.find({id:'1'})
> db.prediction.find({id:1})
{ "_id" : ObjectId("62ee12d7f4c0fd4e165552af"), "id" : 1, "predictions" : 0 }
> db.prediction.find({id:1},{predictions:1, _id:0})
{ "predictions" : 0 }
> 

in:
  type: file
  path_prefix: /home/pyspark/hoge
  decoders:
  - {type: gzip}
  parser:
    charset: UTF-8
    newline: LF
    type: csv
    delimiter: ','
    quote: '"'
    escape: '"'
    null_string: 'NULL'
    trim_if_not_quoted: false
    skip_header_lines: 1
    allow_extra_columns: false
    allow_optional_columns: false
    columns:
    - {name: id, type: long}
    - {name: predictions, type: long}
out:
  type: mongodb_nest
  host: mongo_data_big
  database: user_prediction
  user: action
  password: pass123
  collection: prediction
  key: [id]