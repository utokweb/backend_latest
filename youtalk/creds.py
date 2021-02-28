from . import settings

paytm_test_id =  "7MBTec97774678157894" #"rCRdAO97112990271342"
paytm_test_key = "kAmcEGZ%XP_ySKym" #"&Qsk@BESHuReaw#2"
paytm_prod_id = "7MBTec45180199073008"
paytm_prod_key = "QeoQFs!GrZDUQitY"
paytm_subwallet_guid_test = "68c39e84-77f7-11eb-9783-fa163e429e83"
paytm_subwallet_guid_prod = "767ce465-0add-4bbe-88f6-a3ae0b1ad730"

PAYTM_ID = paytm_test_id  if settings.DEBUG is True else paytm_prod_id
PAYTM_KEY = paytm_test_key if settings.DEBUG is True else paytm_prod_key
PAYTM_SUBWALLET_GUID = paytm_subwallet_guid_test if settings.DEBUG is True else paytm_subwallet_guid_prod

#food, gift, gratification, loyalty, allowance, communication possible values for "solution"
PAYTM_URL = "https://staging-dashboard.paytm.com/bpay/api/v1/disburse/order/wallet/gratification" if settings.DEBUG is True else "https://dashboard.paytm.com/bpay/api/v1/disburse/order/wallet/gratification"
PAYOUT_STATUS_URL = "https://staging-dashboard.paytm.com/bpay/api/v1/disburse/order/query" if settings.DEBUG is True else "https://dashboard.paytm.com/bpay/api/v1/disburse/order/query"

DYNAMIC_LINKS_API = "https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=AIzaSyDDwhxE-356wwR7b7-AaqriQ1tSmgIjqHU"
