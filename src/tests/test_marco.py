from controller import SmartAPI

def test_uptime_update():
    
    test_api = SmartAPI.get("3ba7f69133df5fce68d37d00f48e4d3b")
    test_api.check()
    assert test_api.uptime.status[1] == 'Everything looks good!'
    assert test_api.uptime.status[0] == 'good'