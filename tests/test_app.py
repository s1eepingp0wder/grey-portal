from portal import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_index(client):
    response = client.get('/')
    assert b'<form action="login" method="post">' in response.data
    # There is NO nav bar if we're not logged in.
    assert b'<nav>' not in response.data
