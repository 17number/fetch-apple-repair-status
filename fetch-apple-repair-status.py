import configparser
import requests

APPLE_SUPPORT_BASE = f"https://mysupport.apple.com"
APPLE_SUPPORT_API_BASE = f"{APPLE_SUPPORT_BASE}/api"
APPLE_SUPPORT_API_V1 = f"{APPLE_SUPPORT_API_BASE}/v1"
CSRF_API = f"{APPLE_SUPPORT_BASE}/csrf"
REPAIR_API = f"{APPLE_SUPPORT_API_V1}/supportaccount/getRepairStatus"
REPAIR_DETAIL = f"{APPLE_SUPPORT_BASE}/repairs/details"
LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"

def get_jsessionid():
  res = requests.get(CSRF_API)
  return list(filter(lambda x: "JSESSIONID" in x, res.headers["set-cookie"].split(";")))[0].split("JSESSIONID=")[-1]

def get_repair_status(repair_id, serial_number, jsessionid):
  queries = {"repairId": repair_id, "serialNumber": serial_number}
  headers = {"Cookie": f"SA-Locale=ja_JP; JSESSIONID={jsessionid}"}
  res = requests.get(REPAIR_API, params=queries, headers=headers)
  return res.json()

def extract_repair_summary(repair_id, serial_number, repair_status):
  from datetime import datetime
  date = datetime.fromtimestamp(repair_status["data"]["repairMetaData"]["modifiedDate"] / 1000)
  msg  = "\n"
  msg += f"{date}\n"
  msg += f"{repair_status['data']['repairMetaData']['repairStatusDesc']}\n"
  msg += f"{repair_status['data']['repairMetaData']['repairShortDesc']}\n"
  repair_detail = f"{REPAIR_DETAIL}/{repair_id}?serialNumber={serial_number}"
  msg += f"{repair_detail}\n"
  return msg

def get_repair_params():
  repair_id = config.get("DEFAULT", "repair_id")
  serial_number = config.get("DEFAULT", "serial_number")
  return [repair_id, serial_number]

def notify_to_line(message):
  token = config.get("DEFAULT", "line_notify_token")
  headers = {"Authorization": f"Bearer {token}"}
  data = {"message": message}
  requests.post(LINE_NOTIFY_URL, data=data, headers=headers)

if __name__ == '__main__':
  config = configparser.ConfigParser()
  config.read("config.ini")
  repair_id, serial_number = get_repair_params()
  jsessionid = get_jsessionid()
  repair_status = get_repair_status(repair_id, serial_number, jsessionid)
  repair_summary = extract_repair_summary(repair_id, serial_number, repair_status)
  notify_to_line(repair_summary)

  # IF you check all of response, comment out below codes.
  # from pprint import pprint as pp
  # pp(repair_status)
