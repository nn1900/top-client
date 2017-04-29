from topclient import TopClient

APP_KEY = "app key"
APP_SECRET = "app secret"
SESSION_KEY = "session key"
SUBWAY_TOKEN = "subway token"

client = TopClient(
    APP_KEY,
    APP_SECRET,
    session=SESSION_KEY,
    subway_token=SUBWAY_TOKEN,
    debug=True
)

try:
    # invoke general `request` method w/ params
    result = client.request('taobao.simba.rpt.adgroupkeywordeffect.get', {
        'nick': 'nick',
        'campaign_id': 2311036,
        'adgroup_id': 739459266,
        'start_time': '2017-04-17',
        'end_time': '2017-04-24',
        'source': '1',
        'page_no': 1,
        'page_size': 500,
        'search_type': 'SEARCH'
    })
    print(result)

    # invoke general `request` method w/ named params
    result = client.request('taobao.simba.rpt.adgroupkeywordeffect.get',
        nick='nick',
        campaign_id=2311036,
        adgroup_id=739459266,
        start_time='2017-04-17',
        end_time='2017-04-24',
        source='1',
        page_no=1,
        page_size=500,
        search_type='SEARCH'
    )
    print(result)

    # invoke specific api method if available
    result = client.get_adgroup_effect_rpt(
        nick='nick',
        campaign_id=2311036,
        adgroup_id=739459266,
        start_time='2017-04-17',
        end_time='2017-04-24',
        source='1',
        page_no=1,
        page_size=500,
        search_type='SEARCH'
    )
    print(result)

    # invoke vai api name
    result = client.simba.rpt.adgroupkeywordeffect.get(
        nick='nick',
        campaign_id=2311036,
        adgroup_id=739459266,
        start_time='2017-04-17',
        end_time='2017-04-24',
        source='1',
        page_no=1,
        page_size=500,
        search_type='SEARCH'
    )
    print(result)
except Exception as ex:
    print(ex)
