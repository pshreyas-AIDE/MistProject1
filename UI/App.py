import os
import json
import io
import zipfile
import psycopg2
from flask import Flask, render_template, request, session, redirect, url_for, send_file, flash, jsonify
from flask_session import Session
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from library.jira_integrator import JiraToolkit
from library.s3_library import S3StorageManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'papi_secure_session_key_2026'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['SESSION_PERMANENT'] = True
Session(app)



# --- S3 Connection ---
s3_handler = S3StorageManager(
    bucket_name="papi",
    endpoint_url="http://localhost:9005", # Matching your lib's default
    username="admin",
    aws_secret_key="password123"
)
# --- DATABASE CONFIG ---
def get_db_connection():
    # Update these credentials with your local Postgres settings
    return psycopg2.connect(
        host="127.0.0.1",
        database="my_database",
        user="user",
        password="password",
        cursor_factory=RealDictCursor
    )


# Initialize Jira Toolkit
jt = JiraToolkit("https://mistsys.atlassian.net/", "pshreyas@juniper.net", "YOUR_JIRA_TOKEN")

if not os.path.exists('uploads'): os.makedirs('uploads')
if not os.path.exists('flask_session'): os.makedirs('flask_session')


# --- AUTH ROUTES ---

@app.route('/auth')
def auth_page():
    return render_template('auth.html')


@app.route('/signup', methods=['POST'])
def signup():
    full_name = request.form.get('full_name')
    email = request.form.get('email').lower()
    password = generate_password_hash(request.form.get('password'))

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)", (full_name, email, password))
        conn.commit()
        cur.close();
        conn.close()
        flash("Account created! Please sign in.", "success")
    except Exception as e:
        flash("Email already exists or Database Error.", "danger")
    return redirect(url_for('auth_page'))


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email').lower()
    password = request.form.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close();
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['email']
        session['user_name'] = user['full_name']
        flash("Login Successful.", "success")
        # Add 'new_login=true' to the redirect URL
        return redirect(url_for('index', new_login='true'))

    flash("Invalid email or password.", "danger")
    return redirect(url_for('auth_page'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_page'))


# --- PROTECTED DASHBOARD ROUTES ---

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth_page'))

    # Capture the new_login flag from the URL
    new_login = request.args.get('new_login')

    return render_template('index.html',view='dashboard',groups=session.get('ui_groups'),new_login=new_login)  # Pass it to the template


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user_id' not in session: return redirect(url_for('auth_page'))

    s3_path = request.form.get('s3_path')
    if s3_path:
        payload = s3_handler.get_data(s3_path)
    else:
        file = request.files.get('file')
        if not file or not file.filename.endswith('.json'): return redirect('/')
        payload = json.load(file)

    if payload:
        ui_groups, text_report = Diff_Analyzer().analyze_diff(payload)
        session['payload'], session['ui_groups'], session['text_report'] = payload, ui_groups, text_report
        session.modified = True
    return redirect('/')


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
@app.route('/create_jira', methods=['POST'])
def create_jira():
    summary = request.form.get('summary')
    description = request.form.get('description')
    issue_type = request.form.get('issue_type')
    labels = request.form.get('labels', '').split(',')
    labels = [l.strip() for l in labels if l.strip()]
    try:
        new_key = jt.create_jira("MIST", summary, description, labels, issue_type)
        flash(f"Jira Created Successfully: {new_key}", "success")
    except Exception as e:
        flash(f"Error creating Jira: {str(e)}", "danger")
    return redirect('/')


@app.route('/search_view')
def search_view():
    return render_template('index.html', view='search')


@app.route('/search', methods=['GET', 'POST'])
def search():
    # If accessed via GET (e.g. page refresh), redirect to the search view
    if request.method == 'GET':
        return redirect('/search_view')

    pattern = request.form.get('pattern', '').lower()
    stype = request.form.get('type', 'removed_config')
    payload = session.get('payload', {})

    # Perform the search against the session payload
    results = [m for m, d in payload.items() if
               isinstance(d, dict) and any(pattern in str(c).lower() for c in d.get(stype, []))]

    return render_template('index.html', view='search', search_results=results, pattern=pattern, search_type=stype)


@app.route('/reset')
def reset():
    # Only clear analysis-related keys to avoid logging the user out
    keys_to_clear = ['payload', 'ui_groups', 'text_report']
    for key in keys_to_clear:
        session.pop(key, None)

    session.modified = True
    return redirect('/')


@app.route('/group/<int:group_id>')
def group_detail(group_id):
    if 'user_id' not in session: return redirect(url_for('auth_page'))
    all_groups = session.get('ui_groups')
    if not all_groups: return redirect(url_for('index'))
    target_group = next((g for g in all_groups if g['id'] == group_id), None)
    if not target_group:
        flash(f"Group {group_id} not found.", "danger")
        return redirect(url_for('index'))
    return render_template('group_detail.html', group=target_group)


@app.route('/get_envs')
def get_envs():
    # List top-level folders in the bucket
    result = s3_handler.s3.list_objects(Bucket=s3_handler.bucket_name, Delimiter='/')
    envs = [prefix.get('Prefix').strip('/') for prefix in result.get('CommonPrefixes', [])]
    return jsonify(envs)

@app.route('/get_versions/<env>')
def get_versions(env):
    # List folders under the selected env
    prefix = f"{env}/"
    result = s3_handler.s3.list_objects(Bucket=s3_handler.bucket_name, Prefix=prefix, Delimiter='/')
    versions = [p.get('Prefix').replace(prefix, "").strip('/') for p in result.get('CommonPrefixes', [])]
    return jsonify(versions)

@app.route('/get_s3_files/<env>/<version>')
def get_s3_files(env, version):
    # List files under env/version/
    prefix = f"{env}/{version}/"
    result = s3_handler.s3.list_objects(Bucket=s3_handler.bucket_name, Prefix=prefix)
    files = [obj.get('Key').replace(prefix, "") for obj in result.get('Contents', []) if obj.get('Key') != prefix]
    return jsonify(files)

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