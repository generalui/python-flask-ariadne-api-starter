import json


def test_add_address(client, address_1, address_2, city, country, state, zipcode):
    address_mutation = """mutation Address($input: AddressInput!) {
            addAddress(input: $input) {
                status
                id
            }
        }"""

    response = client.post('/api', json={'query': address_mutation, 'variables': {
        "input":
        {
            "country": country,
            "address1": address_1,
            "address2": address_2,
            "city": city,
            "state": state,
            "zipcode": zipcode
        }
    }
    })
    json_data = json.loads(response.data)
    data = json_data['data']
    register = data['addAddress']

    assert register['status'] == True
