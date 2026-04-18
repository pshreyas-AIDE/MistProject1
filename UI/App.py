import os
import json
import io
import zipfile
from flask import Flask, render_template, request, session, redirect, send_file
from flask_session import Session

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'papi_secure_session_key_2026'

# --- PERSISTENCE CONFIGURATION ---
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['SESSION_PERMANENT'] = True
Session(app)

if not os.path.exists('uploads'): os.makedirs('uploads')
if not os.path.exists('flask_session'): os.makedirs('flask_session')


# --- INTEGRATED GROUPING LOGIC ---
def grouping(commands, mac_wise_commands):
    token_dict, token_content = {}, {}
    token = "$RENAME_TOKEN$"
    token_count = 0
    if not commands: return {}, {}

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

    new_cmds = [" ".join([token_dict[(s[j - 1] if j > 0 else None, s[j + 1] if j < len(s) - 1 else None)]
                          for j in range(len(s))]) for s in [c.split(" ") for c in commands]]

    res_unique = {" ".join([",".join(token_content[t]) for t in c.split(" ")]): 1 for c in set(new_cmds)}
    cmds_all = {c: 1 for c in commands}
    grouped_cmds, command_group_mapping = {}, {}

    def expand(str_list, current, ind, g_id):
        if ind >= len(str_list):
            final = current.strip()
            if final in cmds_all and final not in grouped_cmds:
                command_group_mapping[final], grouped_cmds[final] = g_id, 1
            return
        for word in str_list[ind].split(","):
            expand(str_list, current + word + " ", ind + 1, g_id)

    for count, group_str in enumerate(res_unique, 1):
        expand(group_str.strip().split(" "), "", 0, count)

    device_group_set = {}
    for cmd in commands:
        for mac in mac_wise_commands.get(cmd, []):
            g_id = command_group_mapping.get(cmd)
            if g_id: device_group_set.setdefault(mac, []).append(g_id)

    temp_list = {}
    for mac, groups in device_group_set.items():
        temp_list.setdefault(tuple(sorted(set(groups))), []).append(mac)
    return temp_list, command_group_mapping


class Diff_Analyzer:
    def analyze_diff(self, payload):
        exclude = {'papi_pilot_version', 'papi_internal_version', 'Environment'}
        mac_added, mac_removed = {}, {}
        add_list, rem_list = [], []

        for mac, data in payload.items():
            if not isinstance(data, dict) or mac in exclude: continue
            for cmd in data.get('added_config', []):
                mac_added.setdefault(cmd, []).append(mac)
                add_list.append(cmd)
            for cmd in data.get('removed_config', []):
                mac_removed.setdefault(cmd, []).append(mac)
                rem_list.append(cmd)

        a_summary, a_map = grouping(add_list, mac_added)
        r_summary, r_map = grouping(rem_list, mac_removed)

        mac_to_sig = {}
        for i, macs in a_summary.items():
            for m in macs: mac_to_sig.setdefault(m, [(), ()])[0] = i
        for i, macs in r_summary.items():
            for m in macs: mac_to_sig.setdefault(m, [(), ()])[1] = i

        sig_to_macs = {}
        for m, sig in mac_to_sig.items(): sig_to_macs.setdefault(tuple(sig), []).append(m)

        a_cmds_by_id = {g: [c for c, gid in a_map.items() if gid == g] for g in set(a_map.values())}
        r_cmds_by_id = {g: [c for c, gid in r_map.items() if gid == g] for g in set(r_map.values())}

        ui_groups, report_lines = [], ["Consolidated Grouping Analysis\n\n"]
        map_a, map_r = {}, {}

        for idx, (sig, mac_list) in enumerate(sorted(sig_to_macs.items()), 1):
            group_added_errors = []
            group_removed_errors = []

            for m in mac_list:
                m_data = payload.get(m, {})
                for err in m_data.get('add_error', []):
                    if err not in group_added_errors: group_added_errors.append(err)
                for err in m_data.get('remove_error', []):
                    if err not in group_removed_errors: group_removed_errors.append(err)

            g_data = {
                "id": idx, "macs": mac_list, "added": [], "removed": [],
                "added_errors": group_added_errors, "removed_errors": group_removed_errors
            }
            report_lines.append(f"Group : {idx}\nMac List :{','.join(mac_list)}\n\n")

            for sub_idx, a_id in enumerate(sig[0], 1):
                cmd = a_cmds_by_id[a_id][0]
                status = "Pending analysis" if cmd not in map_a else f"Already Analyzed as Part of Group: {map_a[cmd][0]} Subgroup: {map_a[cmd][1]}"
                map_a.setdefault(cmd, (idx, sub_idx))
                g_data["added"].append({"cmd": cmd, "status": status, "sub": sub_idx})
                report_lines.append(f"\t\t\t\tSubgroup : {sub_idx} ------> {cmd}\n\t\t\t\t\t\t Status - {status} \n\n")

            for sub_idx, r_id in enumerate(sig[1], 1):
                cmd = r_cmds_by_id[r_id][0]
                status = "Pending analysis" if cmd not in map_r else f"Already Analyzed as Part of Group: {map_r[cmd][0]} Subgroup: {map_r[cmd][1]}"
                map_r.setdefault(cmd, (idx, sub_idx))
                g_data["removed"].append({"cmd": cmd, "status": status, "sub": sub_idx})
                report_lines.append(f"\t\t\t\tSubgroup : {sub_idx} ------> {cmd}\n\t\t\t\t\t\t Status - {status} \n\n")

            if group_added_errors: report_lines.append(f"Added Errors: {group_added_errors}\n")
            if group_removed_errors: report_lines.append(f"Removed Errors: {group_removed_errors}\n")
            ui_groups.append(g_data)

        return ui_groups, "".join(report_lines)


# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html', view='dashboard', groups=session.get('ui_groups'))


@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.json'): return redirect('/')
    payload = json.load(file)
    ui_groups, text_report = Diff_Analyzer().analyze_diff(payload)
    session['payload'], session['ui_groups'], session['text_report'] = payload, ui_groups, text_report
    session.modified = True
    return redirect('/')


@app.route('/search_view')
def search_view():
    return render_template('index.html', view='search')


@app.route('/search', methods=['POST'])
def search():
    pattern = request.form.get('pattern', '').lower()
    stype = request.form.get('type', 'removed_config')
    payload = session.get('payload', {})
    results = [m for m, d in payload.items() if
               isinstance(d, dict) and any(pattern in str(c).lower() for c in d.get(stype, []))]
    return render_template('index.html', view='search', search_results=results, pattern=pattern, search_type=stype)


@app.route('/reset')
def reset():
    session.clear()
    return redirect('/')


@app.route('/download')
def download():
    report = session.get('text_report')
    if not report: return redirect('/')
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, 'w') as zf:
        zf.writestr("Consolidated_Analysis_File.txt", report)
    mem.seek(0)
    return send_file(mem, mimetype='application/zip', as_attachment=True, download_name='report.zip')


if __name__ == '__main__':
    app.run(debug=True, port=5000)