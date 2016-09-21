curl -XDELETE http://localhost:9200/smartapi
curl -XPUT http://localhost:9200/smartapi
curl -XPUT http://localhost:9200/smartapi/api/1 --data-binary @data.json

