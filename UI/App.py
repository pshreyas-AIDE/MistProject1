import streamlit as st
import json
import io
import zipfile


# --- 1. UPDATED CORE GROUPING LOGIC ---
def run_papi_analysis(uploaded_file):
    output_files = {}

    def grouping(commands, mac_wise_commands):
        parent_child, token_dict, token_content = {}, {}, {}
        token = "$RENAME_TOKEN$"
        token_count = 0

        if not commands: return {}, {}

        # Tokenizing logic (Parent-Child context)
        for command in commands:
            cmd_split = command.split(" ")
            for i in range(len(cmd_split)):
                parent = cmd_split[i - 1] if i > 0 else None
                child = cmd_split[i + 1] if i < len(cmd_split) - 1 else None
                key = (parent, child)
                if key not in token_dict:
                    t_name = f"{token}{token_count}"
                    token_dict[key] = t_name
                    token_content[t_name] = [cmd_split[i]]
                    token_count += 1
                elif cmd_split[i] not in token_content[token_dict[key]]:
                    token_content[token_dict[key]].append(cmd_split[i])

        # Build tokenized command list
        new_cmds = []
        for cmd in commands:
            split = cmd.split(" ")
            new_cmds.append(" ".join(
                [token_dict[(split[j - 1] if j > 0 else None, split[j + 1] if j < len(split) - 1 else None)] for j in
                 range(len(split))]))

        res_unique = {" ".join([",".join(token_content[t]) for t in c.split(" ")]): 1 for c in set(new_cmds)}
        cmds_all = {c: 1 for c in commands}
        grouped_cmds, command_group_mapping = {}, {}

        # Recursive expansion to map commands to Group IDs
        def expand(str_list, current, ind, g_id):
            if ind >= len(str_list):
                final = current.strip()
                if final in cmds_all and final not in grouped_cmds:
                    command_group_mapping[final] = g_id
                    grouped_cmds[final] = 1
                return
            for word in str_list[ind].split(","):
                expand(str_list, current + word + " ", ind + 1, g_id)

        for count, group_str in enumerate(res_unique, 1):
            expand(group_str.strip().split(" "), "", 0, count)

        # Device/MAC Grouping Logic (Subgroups)
        device_group_set = {}
        for cmd in commands:
            mac_list = mac_wise_commands.get(cmd, [])
            for mac in mac_list:
                g_id = command_group_mapping.get(cmd)
                if g_id:
                    device_group_set.setdefault(mac, []).append(g_id)

        temp_list = {}  # Key: tuple of groups, Value: MAC list
        for mac, groups in device_group_set.items():
            g_tuple = tuple(sorted(set(groups)))
            temp_list.setdefault(g_tuple, []).append(mac)

        return temp_list, command_group_mapping

    # Load and Parse Payload
    payload = json.load(uploaded_file)
    st.session_state['payload_data'] = payload
    exclude = {'papi_pilot_version', 'papi_internal_version', 'Environment', 'devices selection aproach',
               'unique_commands_added_overall', 'unique_commands_removed_overall', 'ignored device macs'}

    mac_wise, added_cmds, rem_cmds, add_err, rem_err = {}, [], [], [], []
    for mac, data in payload.items():
        if mac in exclude or not isinstance(data, dict): continue
        for key, target in [('added_config', added_cmds), ('removed_config', rem_cmds), ('add_error', add_err),
                            ('remove_error', rem_err)]:
            if key in data:
                for cmd in data[key]:
                    mac_wise.setdefault(cmd, []).append(mac)
                    target.append(cmd)

    # Helper to generate Subgrouped Reports
    def generate_report(cmds, mapping_data, prefix):
        summary_grouping, group_mapping = mapping_data
        cmds_per_group = {}
        for cmd, g_id in group_mapping.items():
            cmds_per_group.setdefault(f"{prefix}{g_id}", []).append(cmd)

        report_buf = io.StringIO()
        report_buf.write(f"{'Newly Added' if prefix == 'A' else 'Newly Removed'} Configs Summary Grouping\n")

        visited = []
        group_visited = {}
        for group_count, (group_tuple, mac_list) in enumerate(summary_grouping.items(), 1):
            report_buf.write(f"\n\n{'*' * 30}\nGroup : {group_count}\n")
            report_buf.write(f"\tMac List : {','.join(mac_list)}\n\n")

            for subgroup_count, g_id in enumerate(group_tuple, 1):
                full_id = f"{prefix}{g_id}"
                if full_id not in group_visited:
                    group_visited[full_id] = [str(group_count), str(subgroup_count)]
                    report_buf.write(f"\tSub group {subgroup_count} :\n")
                    for cmd in cmds_per_group.get(full_id, []):
                        report_buf.write(f"\t\t{cmd}\n")
                        visited.append(cmd)
                else:
                    report_buf.write(
                        f"\tConfigs are part of Group : {group_visited[full_id][0]} Subgroup : {group_visited[full_id][1]}\n")

        report_buf.write(f"\n{'*' * 30}\nCommands belonging to no group :\n")
        for cmd in set(cmds) - set(visited):
            report_buf.write(f"{cmd}\n")

        return report_buf.getvalue()

    # Process Analysis
    added_data = grouping(added_cmds, mac_wise)
    removed_data = grouping(rem_cmds, mac_wise)

    output_files["newly_added_configs.txt"] = generate_report(added_cmds, added_data, "A")
    output_files["newly_removed_configs.txt"] = generate_report(rem_cmds, removed_data, "R")
    output_files[
        "analysis_summary.txt"] = f"{output_files['newly_added_configs.txt']}\n\n{output_files['newly_removed_configs.txt']}"

    error_buf = io.StringIO()
    error_buf.write(
        f"ERRORS SUMMARY\n{'=' * 20}\nAdded Errors:\n" + "\n".join(add_err) + "\n\nRemoved Errors:\n" + "\n".join(
            rem_err))
    output_files["errors_report.txt"] = error_buf.getvalue()

    return output_files


# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="Papi Analyzer", layout="wide")

if 'results_dict' not in st.session_state: st.session_state['results_dict'] = None
if 'payload_data' not in st.session_state: st.session_state['payload_data'] = None
if 'reset_count' not in st.session_state: st.session_state['reset_count'] = 0


def reset_all():
    st.session_state['results_dict'] = None
    st.session_state['payload_data'] = None
    st.session_state['reset_count'] += 1


st.title("📂 Papi Analyzer")

col_tabs, col_spacer, col_btn = st.columns([4, 2, 1])
with col_tabs:
    tab1, tab2, tab3 = st.tabs(["📊 Analyzer", "🔍 Pattern Matching MAC", "❓ Help"])
with col_btn:
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    st.button("🔄 Clear All", on_click=reset_all, use_container_width=True)

st.divider()

with tab1:
    u_file = st.file_uploader("Upload Papi Diff JSON", type=['json'], key=f"file_up_{st.session_state['reset_count']}")
    if u_file:
        if st.button("🚀 Analyze File"):
            with st.spinner("Analyzing..."):
                try:
                    st.session_state['results_dict'] = run_papi_analysis(u_file)
                    st.success("Analysis Complete!")
                except Exception as e:
                    st.error(f"Error during analysis: {e}")

        res = st.session_state['results_dict']
        if res:
            z_buf = io.BytesIO()
            with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
                for n, c in res.items(): zf.writestr(n, c)
            st.download_button("📥 Download All Reports (ZIP)", z_buf.getvalue(), "papi_results.zip")

            st.divider()
            st.subheader("Results Preview")

            # CSS for the scrollable box
            scroll_style = """
                        <style>
                            .scroll-box {
                                height: 400px;
                                overflow-y: scroll;
                                padding: 10px;
                                border: 1px solid #4B4B4B;
                                border-radius: 5px;
                                background-color: #0E1117;
                                font-family: monospace;
                                white-space: pre;
                            }
                        </style>
                        """
            st.markdown(scroll_style, unsafe_allow_html=True)

            with st.expander("Preview Added Configs (Subgrouped)", expanded=True):
                content = res.get("newly_added_configs.txt", "No data available.")
                st.markdown(f'<div class="scroll-box">{content}</div>', unsafe_allow_html=True)

            with st.expander("Preview Removed Configs (Subgrouped)"):
                content = res.get("newly_removed_configs.txt", "No data available.")
                st.markdown(f'<div class="scroll-box">{content}</div>', unsafe_allow_html=True)

            with st.expander("Preview Errors"):
                content = res.get("errors_report.txt", "No errors found.")
                st.markdown(f'<div class="scroll-box">{content}</div>', unsafe_allow_html=True)

# (Tab 2 and Tab 3 logic remain the same for MAC pattern matching and help text)
with tab2:
    st.header("Pattern Matching MAC")
    if not st.session_state['payload_data']:
        st.warning("Please upload and analyze a file in the 'Analyzer' tab first.")
    else:
        pat = st.text_input("Enter pattern to search (e.g. gbp_):")
        c1, c2 = st.columns(2)
        p_data = st.session_state['payload_data']

        if c1.button("Search Added Config"):
            if not pat:
                st.error("Pattern not given")
            else:
                res_mac = []
                for mac, data in p_data.items():
                    if not isinstance(data, dict): continue
                    if 'added_config' in data:
                        for cmd in data['added_config']:
                            if pat in cmd:
                                res_mac.append(mac)
                                break
                unique_macs = set(res_mac)
                st.subheader(f"Matches in Added Config ({len(unique_macs)})")
                st.write(unique_macs)

        if c2.button("Search Removed Config"):
            if not pat:
                st.error("Pattern not given")
            else:
                res_mac = []
                for mac, data in p_data.items():
                    if not isinstance(data, dict): continue
                    if 'removed_config' in data:
                        for cmd in data['removed_config']:
                            if pat in cmd:
                                res_mac.append(mac)
                                break
                unique_macs = set(res_mac)
                st.subheader(f"Matches in Removed Config ({len(unique_macs)})")
                st.write(unique_macs)

with tab3:
    st.info("Upload your JSON in the Analyzer tab to begin. The 'Clear All' button at the top right resets everything.")