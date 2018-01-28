import ovh

def add_runner_mailing(address):
    # Phidippides access
    client = ovh.Client(
        endpoint='ovh-eu',
        application_key='change_me',
        application_secret='change_me',
        consumer_key='change_me',
    )

    try:
        client.post('/to/update/with/your/endpoint', 
                    email=address)
    except:
        # at this time, do not manage exception
        pass
