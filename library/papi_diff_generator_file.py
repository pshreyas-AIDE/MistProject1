import asyncio
import httpx
import json
from library.https_call import HTTP_Calls
import time

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + "VgUb81zThTG9VKvAKjS8d6oqnmM2WMfIuEwp8VEQgdcELihOiMjHO9cBwBqiiwEuxTexZygCRXbOITggKh2NTjma3W9o8tBv"
}

result={}
async def fetch_pair(client, mac_id,version,model, semaphore):
    async with semaphore:
        # We don't use gather() here to ensure we reuse the connection
        # and stay within rate limits more easily.

        # Call 1
        resp1 = await client.get(f"http://papi-internal-production.mist.pvt/internal/devices/{mac_id}/config_with_qs")
        status_code=resp1.status_code
        try:
            data1 = resp1.json()
            config_cmd1 = set(data1['ConfigCmd'])
            error1 = set(data1['_errors'])
        except:
            data1={}
            config_cmd1 = set()
            error1 = set()
        #print(status_code, data1)


        # Call 2 (Uses the same 'warm' connection automatically)
        resp2 = await client.get(f"http://papi-pilot-production.mist.pvt/internal/devices/{mac_id}/config_with_qs")
        status_code = resp2.status_code
        try:
            data2 = resp2.json()
            config_cmd2 = set(data2['ConfigCmd'])
            error2 = set(data2['_errors'])
        except:
            data2={}
            config_cmd2 = set()
            error2 = set()
        #print(status_code, data1)

        diff_added=config_cmd1 - config_cmd2
        diff_removed=config_cmd2 - config_cmd1
        error_added=error1 - error2
        error_removed=error2 - error1
        if(len(diff_removed)!=0 or len(diff_added)!=0):
            return {"mac":mac_id,
                "added_configs":list(diff_added),
                "removed_configs":list(diff_removed),
                "added_error":list(error_added),
            "removed_error":list(error_removed),
            "org_id":data1['OrgID'],
                    "version":version,
                    "model":model
            }
        else:
            return None

async def main(item_ids):
    # Limit to 100 concurrent requests to stay within connection limits
    sem = asyncio.Semaphore(100)

    limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
    async with httpx.AsyncClient(limits=limits, timeout=None,headers=HEADERS,follow_redirects=True) as client:
        tasks = [fetch_pair(client, i[0],i[1],i[2], sem) for i in item_ids]

        # gather results as they complete
        results = await asyncio.gather(*tasks)
        # 'results' is now a list of 100k set-differences
    # After the gather is complete:
    clean_results = [r for r in results if r is not None]
    with open("api_results.json", "w") as f:
        json.dump(clean_results, f, indent=4)

if __name__ == "__main__":
    start_time=time.perf_counter()
    mac_list = []
    obj = HTTP_Calls("VgUb81zThTG9VKvAKjS8d6oqnmM2WMfIuEwp8VEQgdcELihOiMjHO9cBwBqiiwEuxTexZygCRXbOITggKh2NTjma3W9o8tBv")

    results = []
    res = obj.get_call("http://papi-internal-production.mist.pvt/search/switches?type=switch&limit=10000")
    results += res["results"]

    while "next" in res.keys():
        all_search_url = res["next"]
        res = obj.get_call(all_search_url)
        results += res["results"]

    for item in results:
        mac_list.append((item["mac"], item["version"],item['model']))


    asyncio.run(main(mac_list))
    end_time = time.perf_counter()
    total_time = end_time - start_time
    print(f"Processed 100,000 items in {total_time:.2f} seconds.")




