import os
import sys
import json
import requests
import zipfile
import re

def download(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

def known_exploited():
    result = []
    r = requests.get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    for vuln in r.json()['vulnerabilities']:
        result.append(vuln['cveID'])
    return result

def get_cve_data():
    cve_zip = download("https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.zip")
    #cve_zip = "nvdcve-1.1-recent.json.zip"
    cve_json = cve_zip.split('.zip')[0]
    with zipfile.ZipFile(cve_zip, 'r') as zip_ref:
        zip_ref.extractall('./')
    with open(cve_json) as j:
        cve_data = json.loads(j.read())
    os.remove('nvdcve-1.1-recent.json.zip')
    os.remove('nvdcve-1.1-recent.json')
    return cve_data


def parse_cve_data(c):
    cve_res = {}
    cve_res['id'] = c["cve"]["CVE_data_meta"]["ID"]
    for descr in c['cve']['description']['description_data']:
        if descr['lang'] == 'en':
            cve_res['description'] = descr['value']
    if c['impact']:
        cve_res[f"impact"] = str(c['impact'])
        cve_res[f"severity"] = str(c['impact']['baseMetricV3']['cvssV3']['baseSeverity'])
    else:
        cve_res[f"impact"] = "N/A"
        cve_res[f"severity"] = "N/A"
    return cve_res

def fetch():
    exploited = known_exploited()
    result = []
    cve_data = get_cve_data()
    if os.path.isfile('.seen_cve_ids.json'):
        with open('.seen_cve_ids.json', 'r') as s:
            seen_ids = json.load(s)
    else:
        seen_ids = []
    for cve_res in cve_data['CVE_Items']:
        cve_id = cve_res["cve"]["CVE_data_meta"]["ID"]
        if cve_id not in seen_ids:
            seen_ids.append(cve_id)
            val = {"id": cve_id, "description": cve_res['cve']['description']['description_data'], }
            cve_parsed = parse_cve_data(cve_res)
            if cve_id in exploited:
                cve_parsed['exploited'] = True
            else:
                cve_parsed['exploited'] = False
            result.append(cve_parsed)

    with open('.seen_cve_ids.json', 'w+') as s:
        s.write(json.dumps(seen_ids))
    return result

if __name__=="__main__":
    print(cve())
