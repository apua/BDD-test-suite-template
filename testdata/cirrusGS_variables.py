'''
Cirrus data variables

'''
CIRRUS_IP = '16.104.158.218'
rest_login_usr = '/rest/login-sessions?action='
rest_GS = '/rest/cirrus/globalsearch'
rest_suggestion_list = '/rest/cirrus/suggest'
rest_logfile = '/rest/cirrus/getLogFile'
rest_set_pagesize = '/rest/cirrus/setDefaultPageSize'
rest_get_pagesize = '/rest/cirrus/getDefaultPageSize/'
rest_log_download = '/rest/cirrus/download_gs_logs'
headers = {'X-API-Version':'100','Content-Type':'application/json'}
rest_login = {'userName' :'Administrator','password':'Compaq123','authLoginDomain':'LOCAL'}
rest_global_search={'search':'log file','itemCount':10,'itemFrom':0}
req_suggest = {'search':'log'}
req_pagesize={'userName':'Administrator','pageSize':90}
string=[
                'ci-005056814087_administrator_31',     #give valid single string
                '\"fxdriver@googlecode.com\"',          #give valid string/sentence to find exact match
                '*dmin*',                               #wildcard string *
                '???sDefault?',                         #wildcard string ?
                'log ! file & time',                    #give valid strings with NOT and AND combination
                'log ! file | time',                    #give valid strings with NOT and OR combination
                '! ilo | ( ci & time )',                #give valid strings with NOT, OR and AND (precedence) combination
                'ilo & ( file | time )',                #give valid strings with NOT, AND and OR (precedence) combination
                '    ',                                 #give space
                '$$$$',                                 #give any special character
                'Current Time Stamp of the log file']   #give any sting/sentence for suggestion
itemfrom_Next = 10
itemfrom_Prev = 0