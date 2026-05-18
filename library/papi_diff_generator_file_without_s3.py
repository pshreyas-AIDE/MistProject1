import asyncio
import os

import httpx
import json
from library.https_call import HTTP_Calls
from library.s3_library import S3StorageManager
from library.postgresql import *
import time
import logging
import subprocess


# # s3 Object creation to write diffs
# schema_name=os.environ.get("s3_schema_name")
# s3_object = S3StorageManager(schema_name)
#
# # path global for the papi diff run
# path_of_s3_file=f"{schema_name}/{os.environ['env_id']}/{os.environ['papi_internal_version']}|{os.environ['papi_pilot_version']}"
#



# Diff Generator
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + os.environ['env_api_token']
}
error_file=open("error_list.json","w")
mac_list_file=open("mac_list.json","w")
result={}


def check_port_exhaustion(threshold=0.8, wait_time=120):
    """
    Checks if TCP port usage is above the threshold (default 80%).
    If so, sleeps for wait_time (default 2 mins).
    """
    # 1. Get the total range size (macOS specific)
    # Typically 49152 to 65535 on Mac = 16,383 ports
    try:
        first = int(subprocess.check_output(["sysctl", "-n", "net.inet.ip.portrange.first"]).decode())
        last = int(subprocess.check_output(["sysctl", "-n", "net.inet.ip.portrange.last"]).decode())
        total_allowed = last - first
    except Exception:
        total_allowed = 16383  # Fallback for standard macOS config

    # 2. Count current TCP connections (Established and Time_Wait)
    # We use netstat -an and count lines containing 'tcp'
    try:
        current_usage = int(subprocess.check_output("netstat -an | grep -c 'tcp'", shell=True).decode())
    except subprocess.CalledProcessError:
        current_usage = 0

    usage_percent = current_usage / total_allowed
    print(f"Current Port Usage: {current_usage}/{total_allowed} ({usage_percent:.1%})")

    # 3. Logic: If 80% or more, wait
    if usage_percent >= threshold:
        print(f"PORT EXHAUSTION RISK! {usage_percent:.1%} used. Waiting {wait_time}s for ports to clear...")
        time.sleep(wait_time)
        return True

    return False

def check_port_exhaustion_linux(threshold=0.8, wait_time=120):
    """
    Linux-optimized check for ephemeral TCP port exhaustion.
    Reads directly from /proc filesystem to maximize speed and minimize resource footprint.
    """
    # 1. Get the exact Ephemeral Port Pool Size configured on the host
    try:
        with open('/proc/sys/net/ipv4/ip_local_port_range', 'r') as f:
            parts = f.read().split()
            first, last = int(parts[0]), int(parts[1])
            total_allowed = last - first + 1
    except Exception:
        # Fallback to the default Linux kernel range if file reading fails
        total_allowed = 28232  # (32768 to 60999)

    # 2. Count active TCP sockets from the kernel space
    # This reads the live TCP connection table instantly
    try:
        with open('/proc/net/tcp', 'r') as f:
            # Read lines and subtract 1 for the header row
            current_usage = len(f.readlines()) - 1
    except Exception:
        current_usage = 0

    # Prevent potential ZeroDivisionError
    if total_allowed <= 0:
        total_allowed = 28232

    usage_percent = current_usage / total_allowed
    print(f"Current Linux Port Usage: {current_usage}/{total_allowed} ({usage_percent:.1%})")

    # 3. Defensive safeguard logic
    if usage_percent >= threshold:
        print(f"PORT EXHAUSTION RISK! {usage_percent:.1%} used on runner. Waiting {wait_time}s to clear...")
        time.sleep(wait_time)
        return True

    return False


async def fetch_pair(client, mac_id,version,model, semaphore):
    async with semaphore:
        # We don't use gather() here to ensure we reuse the connection
        # and stay within rate limits more easily.

        # Call 1

        try:
            resp1 = await client.get(f"http://papi-internal-{os.environ['env_id']}.mist.pvt/internal/devices/{mac_id}/config_with_qs",follow_redirects=True,timeout=30.0)
            status_code=resp1.status_code
            data1 = resp1.json()
            if("ConfigCmd" in data1):
                config_cmd1 = set(data1['ConfigCmd'])
            else:
                config_cmd1 = set()
            if("_errors" in data1):
                error1= set(data1['_errors'])
            else:
                error1 = set()
            if(status_code!=200):
                error_file.write("papi-internal"+str(mac_id)+" Status code : "+str(status_code)+"\n")
                error_file.write(str(data1)+"\n")
                # error_message="papi-internal"+str(mac_id)+" Status code : "+str(status_code)+"\n"+str(data1)+"\n"
                # error_file_s3_path=f"{path_of_s3_file}/error_list.jsonl"
                # s3_object.upload_data(error_file_s3_path,error_message)
        except Exception as e:
            err_detail = str(e) if str(e) else repr(e)
            error_file.write(f"papi-internal | {mac_id} | Exception: {type(e).__name__} | {err_detail}\n")
            # error_message=f"papi-internal | {mac_id} | Exception: {type(e).__name__} | {err_detail}\n"
            # error_file_s3_path = f"{path_of_s3_file}/error_list.jsonl"
            # s3_object.upload_data(error_file_s3_path, error_message)
            data1={}
            config_cmd1 = set()
            error1 = set()
        #print(status_code, data1)


        # Call 2 (Uses the same 'warm' connection automatically)
        try:
            resp2 = await client.get(f"http://papi-pilot-{os.environ['env_id']}.mist.pvt/internal/devices/{mac_id}/config_with_qs",follow_redirects=True,timeout=30.0)
            status_code = resp2.status_code
            data2 = resp2.json()
            if("ConfigCmd" in data2):
                config_cmd2 = set(data2['ConfigCmd'])
            else:
                config_cmd2 = set()
            if("_errors" in data2):
                error2 = set(data2['_errors'])
            else:
                error2 = set()
            if (status_code != 200):
                error_file.write("papi-pilot" + str(mac_id) + " Status code : " + str(status_code) + "\n")
                error_file.write(str(data2) + "\n")

                # error_message="papi-pilot"+str(mac_id)+" Status code : "+str(status_code)+"\n"+str(data2)+"\n"
                # error_file_s3_path=f"{path_of_s3_file}/error_list.jsonl"
                # s3_object.upload_data(error_file_s3_path,error_message)

        except Exception as e:
            err_detail = str(e) if str(e) else repr(e)
            error_file.write(f"papi-pilot | {mac_id} | Exception: {type(e).__name__} | {err_detail}\n")
            error_message = f"papi-pilot | {mac_id} | Exception: {type(e).__name__} | {err_detail}\n"
            # error_file_s3_path = f"{path_of_s3_file}/error_list.jsonl"
            # s3_object.upload_data(error_file_s3_path, error_message)

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
                "added_config":list(diff_added),
                "removed_config":list(diff_removed),
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

            check_port_exhaustion_linux()
            # Save incremental progress to a file
            with open(f"results_batch_{i // batch_size}.json", "w") as f:
                json.dump(clean_batch, f, indent=4)
            # batch_s3_path= f"{path_of_s3_file}/results_batch_{i // batch_size}.json"
            # s3_object.upload_data(batch_s3_path, json.dumps(clean_batch, indent=4))


            # Add percentage of execution
            # s3_path_percentage = f"{path_of_s3_file}/percentage_of_run.json"
            # percentage_of_run = (i/len(item_ids))*100
            # s3_object.update_percentage(s3_path_percentage, percentage_of_run)


        # 'results' is now a list of 100k set-differences



    # After the gather is complete:
    # with open("api_results_final.json", "w") as f:
    #     json.dump(all_clean_results, f, indent=4)
    papi_diff_file_final_contets = {
        "papi_pilot_version": os.environ.get("papi_pilot_version"),
        "papi_internal_version": os.environ.get("papi_internal_version"),
        "Environment": os.environ.get("env_id"),
        "devices considered": len(item_ids),
        "devices with diff": len(all_clean_results)
    }
    for i in all_clean_results:
        mac_id=i["mac"]
        papi_diff_file_final_contets[mac_id]=i

    # papi_diff_final_s3_path = f"{path_of_s3_file}/papi_config_compare_data_switch_{os.environ['env_id']}.json"
    # s3_object.upload_data(papi_diff_final_s3_path, json.dumps(papi_diff_file_final_contets,indent=4))
    with open(f"papi_config_compare_data_switch_{os.environ['env_id']}.json", "w") as f:
        json.dump(papi_diff_file_final_contets, f, indent=4)


# if __name__ == "__main__":
#     start_time=time.perf_counter()
#     mac_list = []
#     obj = HTTP_Calls(os.environ['env_api_token'])
#
#     results = []
#     res = obj.get_call(f"http://papi-internal-{os.environ['env_id']}.mist.pvt/search/switches?type=switch&limit=10000")
#     results += res["results"]
#
#     while "next" in res.keys():
#         all_search_url = res["next"]
#         res = obj.get_call(all_search_url)
#         results += res["results"]
#
#     for item in results:
#         mac_id=None
#         version=None
#         model=None
#         if("mac" in item):
#             mac_id=item["mac"]
#         if("version" in item):
#             version=item["version"]
#         if("model" in item):
#             model=item["model"]
#         mac_list.append((mac_id, version,model))
#
#     # Batches of 1000 macs
#     asyncio.run(main(mac_list))
#     end_time = time.perf_counter()
#     total_time = end_time - start_time
#     print(f"Processed 100,000 items in {total_time:.2f} seconds.")



class papi_diff_generator_for_env:
    def __init__(self):
        start_time=time.perf_counter()
        mac_list = []
        obj = HTTP_Calls(os.environ['env_api_token'])

        results = []
        res = obj.get_call(f"http://papi-internal-{os.environ['env_id']}.mist.pvt/search/switches?type=switch&limit=10000")
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
        print(f"Processed {len(mac_list)} items in {total_time:.2f} seconds.")
        mac_list_file.write(f"Processed {len(mac_list)} items in {total_time:.2f} seconds.\n\n{str(mac_list)}")

        # After going through all files - Update percentage as 100 %
        # s3_path_percentage = f"{path_of_s3_file}/percentage_of_run.json"
        # percentage_of_run = 100
        # s3_object.update_percentage(s3_path_percentage, percentage_of_run)

obj=papi_diff_generator_for_env()

