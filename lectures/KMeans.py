from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.ml.feature import VectorAssembler

# 学習用データの読み込み
df2 = spark.read.parquet("/tmp/share_file/datamart/web_actions/")

df2 = df2.select(F.col('id').cast("integer"),F.col('money').cast("integer"))

# データをモデル作成用(train)と適用用(predict)に分ける
predict,train=df2.randomSplit([0.6,0.4],785)
train =train.groupby('id').agg(F.sum('money').alias('money'))
train_vector = VectorAssembler(inputCols = ['money'], outputCol = "features").transform(train)

# モデルを利用して学習する
kmeans = KMeans().setK(2).setSeed(1)
model = kmeans.fit(train_vector)


# モデルの結果からユーザを分類する
predict =predict.groupby('id').agg(F.sum('money').alias('money'))
predict_vector = VectorAssembler(inputCols = ['money'], outputCol = "features").transform(predict)
predictions = model.transform(predict_vector)

# 予測結果を確認する
into_kvs = predictions.select('id','prediction')

# 結果をparquetとして保存する
#into_kvs.repartition(1).write.mode("overwrite").option("compression","gzip").parquet("/tmp/share_file/datamodel/part1")
into_kvs.repartition(1).write.mode("overwrite").option("compression","gzip").parquet("/tmp/share_file/datamodel/part2")
