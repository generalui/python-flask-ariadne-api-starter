import json


def test_test_query(client):
    query = """query Test {
        test {
            items {
                contentType
                userAgent
                headers {
                    contentLength
                    contentType
                    host
                    userAgent
                }
            }
            page
        }
    }"""
    response = client.post('/api', json={'query': query})
    json_data = json.loads(response.data)
    test = json_data['data']['test']
    results = test['items']

    assert isinstance(results['contentType'], str)
    assert isinstance(results['userAgent'], str)
    assert isinstance(results['headers']['contentLength'], int)
    assert isinstance(results['headers']['contentType'], str)
    assert isinstance(results['headers']['host'], str)
    assert isinstance(results['headers']['userAgent'], str)
