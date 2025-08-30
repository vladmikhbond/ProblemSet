# def try_url(url: str) -> bool:
#     from urllib.request import urlopen
#     try:
#         with urlopen(url, timeout=5):
#             return True
#     except:
#         return False

# host1 = "http://178.151.21.169:7000"       # for internet
# # host2 = "http://172.17.0.1:7000"         # for docker default net
 

# if try_url(host1): 
#     PSS_HOST = host1
# elif try_url(host2): 
#     PSS_HOST = host2
# else:
#     PSS_HOST = ""
