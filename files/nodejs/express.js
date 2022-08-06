const { Kafka } = require('kafkajs')
const mongodb = require('mongodb')

const MongoClient = mongodb.MongoClient

const kafka = new Kafka({
    clientId: 'my-app',
    brokers: ['kafka_big:9092']
})
const express = require('express');
const app = express();

const promiseFunc = req => {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            // mongoDB直接ではなくてAPIサーバと接続することも多いです
            MongoClient.connect('mongodb://action:pass123@mongo_data_big:27017/user_prediction', (err, db) => {
                if (err) throw err;

                const dbName = db.db("user_prediction");

                // dbName.collection("prediction").find().toArray(function(err, res) {
                //   if (err) throw err;
                //   console.log(res);
                // });
                // 予測値をmongoDBより取得
                dbName.collection("prediction").find({id:parseInt(req.query.id)},{predictions:1, _id:0}).toArray((error, documents)=>{
                    console.log(documents);
                    let attr = 0;
                    for (var document of documents) {
                        attr = parseInt(document.predictions);
                        console.log('attribute:' + attr);
                    }
                    resolve(attr);
                });
            })

    }, 1000);
    });
};

async function mongos(req) {
    return await promiseFunc(req)
}

app.get('/display_user_base_data', (req, res) => {

    mongos(req).then(result => {
        console.log('hogepeke' + result);
        if (result == 1) {
            res.send('ユーザ属性が1の人です。A広告');  
        }
        else {
            res.send('ユーザ属性が1以外の人です。B広告');
        }
    });

});

app.get('/done', (req, res) => {
    senddata('check_cart', req)
    res.send('お買い上げどうも\n');
});

app.get('/cart', (req, res) => {
    senddata('add_cart',req)
    res.send('カートに入りました\n');
});

app.get('/', (req, res) => {
    senddata('login',req)
    res.send('ログインしました\n');
});

function senddata(action,req) {
    let today = new Date();
 
    let year = today.getFullYear();
    let month = today.getMonth() + 1;
    let date = today.getDate();
    let date_str = year + '-' + month.toString().padStart(2, "0") + '-' + date;
    
    (async () => {
        const producer = kafka.producer()

        await producer.connect()
        await producer.send({
            topic: 'pyspark-topic',
            messages: [
                {
                    key: `${date_str}`, "value": `{"id": "${req.params.id}", "money": "${Math.floor(Math.random() * (100 - 2000000))}", "sendtime": ${Date.now()}}`
                },
            ],
        })

        await producer.disconnect()

    })()
}

app.listen(3001);