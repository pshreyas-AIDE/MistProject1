import asyncio
import httpx
import json
from library.https_call import HTTP_Calls
import time
import logging



HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + "VgUb81zThTG9VKvAKjS8d6oqnmM2WMfIuEwp8VEQgdcELihOiMjHO9cBwBqiiwEuxTexZygCRXbOITggKh2NTjma3W9o8tBv"
}
error_file=open("error_list.json","w")
result={}
async def fetch_pair(client, mac_id,version,model, semaphore):
    async with semaphore:
        # We don't use gather() here to ensure we reuse the connection
        # and stay within rate limits more easily.

        # Call 1

        try:
            resp1 = await client.get(f"http://papi-internal-production.mist.pvt/internal/devices/{mac_id}/config_with_qs",follow_redirects=True,timeout=30.0)
            status_code=resp1.status_code
            data1 = resp1.json()
            if("ConfigCmd" in data1):
                config_cmd1 = set(data1['ConfigCmd'])
            if("_errors" in data1):
                error1= set(data1['_errors'])
        except Exception as e:
            error_file.write("papi-internal"+str(mac_id)+str(e)+"\n")
            data1={}
            config_cmd1 = set()
            error1 = set()
        #print(status_code, data1)


        # Call 2 (Uses the same 'warm' connection automatically)
        try:
            resp2 = await client.get(f"http://papi-pilot-production.mist.pvt/internal/devices/{mac_id}/config_with_qs",follow_redirects=True,timeout=30.0)
            status_code = resp2.status_code
            data2 = resp2.json()
            if("ConfigCmd" in data2):
                config_cmd2 = set(data2['ConfigCmd'])
            if("_errors" in data2):
                error2 = set(data2['_errors'])
        except Exception as e:
            error_file.write("Papi-pilot"+str(mac_id) + str(e) + "\n")
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
                    "version":version,
                    "model":model
            }
        else:
            return None

async def main(item_ids):
    # Limit to 100 concurrent requests to stay within connection limits
    sem = asyncio.Semaphore(100)
    batch_size=1000
    all_clean_results=[]
    limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
    async with httpx.AsyncClient(limits=limits, timeout=None,headers=HEADERS,follow_redirects=True) as client:
        for i in range(0, len(item_ids), batch_size):
            batch = item_ids[i: i + batch_size]
            print(f"Processing batch: {i} to {i + batch_size}...")
            # Create and run tasks only for the current 1000 items
            tasks = [fetch_pair(client, item[0], item[1], item[2], sem) for item in batch]
            batch_results = await asyncio.gather(*tasks)

            # Filter out the None values (items with no differences)
            clean_batch = [r for r in batch_results if r is not None]
            all_clean_results.extend(clean_batch)

            # Optional: Save incremental progress to a file
            with open(f"results_batch_{i // batch_size}.json", "w") as f:
                json.dump(clean_batch, f, indent=4)
        # 'results' is now a list of 100k set-differences
    # After the gather is complete:
    with open("api_results_final.json", "w") as f:
        json.dump(all_clean_results, f, indent=4)


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
        mac_id=None
        version=None
        model=None
        if("mac" in item):
            mac_id=item["mac"]
        if("version" in item):
            version=item["version"]
        if("model" in item):
            model=item["model"]
        mac_list.append((mac_id, version,model))

    # Batches of 1000 macs
    asyncio.run(main(mac_list))
    end_time = time.perf_counter()
    total_time = end_time - start_time
    print(f"Processed 100,000 items in {total_time:.2f} seconds.")




