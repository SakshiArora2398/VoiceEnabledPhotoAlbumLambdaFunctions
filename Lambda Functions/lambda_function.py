import json
import boto3
import requests
import data_index

def lambda_handler(event, context):
    print(event)
    lex = boto3.client('lex-runtime')
    query = event["queryStringParameters"]["q"]
#     query="show me picture of dog"
    lex_response = lex.post_text(
        botName='NLPControlledPhotoAlbum',
        botAlias='photoalbum',
        userId='Twisha',
        inputText=query
    )
    print("LEX RESPONSE --- {}".format(json.dumps(lex_response)))

    query = lex_response['slots']['searchque']
#    query = event['currentIntent']['slots']['searchque'] fffff
    print('query', query)

    keys = query.split(',')
    Res = []
    es = data_index.connect_to_elastic_search()
    out = []
    o=[]
    outS = ""
    outRes = []
    print('keys',keys)
    for i in range(len(keys)):
        print(keys[i])
        print(es.info())
        qu = {"size":25, "query":{"match":{"labels": str(keys[i].lower())}}}
        res = es.search(body=json.dumps(qu))
        print(res)
        Res.append(res)
        print("Got %d Hits:" % res['hits']['total']['value'])
        print(res)
        for i in res['hits']['hits']:
            bucket = i['_source']['bucket']
            image = i['_source']['objectKey']
            a = "https://s3.amazonaws.com/" + bucket + "/" + image
            if a not in o:
                o.append(a)
                out.append({"url":a,"labels":i['_source']['labels']})
                outS += a + ", "
                outRes.append({'title': image.split(".")[0], 'attachmentLinkUrl': a, 'imageUrl': a})
        print('File path: ', out)
    
    return {
        'statusCode': 200,
        'body': json.dumps(out),
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
        }
    }
