import os
import sqlite3
import string
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string, redirect, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'admin_tptool_vip_2024')

DB = "vip_keys.db"

ADMIN_USER = "admin"
ADMIN_PASS = "thienphu@2024"

PACKAGES = {
    "1day": {"name": "1 Ngày", "days": 1},
    "3day": {"name": "3 Ngày", "days": 3},
    "7day": {"name": "7 Ngày", "days": 7},
    "30day": {"name": "30 Ngày", "days": 30},
    "forever": {"name": "Vĩnh Viễn", "days": 36500},
}


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS vip_keys(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_code TEXT UNIQUE,
            package TEXT,
            created_at TEXT,
            expiry TEXT,
            device_id TEXT DEFAULT '',
            is_used INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()


def gen_key():
    return f"TPV-{''.join(random.choices(string.ascii_uppercase + string.digits, k=5))}"


CSS = '''<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

*{
    margin:0;
    padding:0;
    box-sizing:border-box
}

body{
    background:linear-gradient(135deg,#0a0015,#150030,#0a0015);
    min-height:100vh;
    font-family:'Orbitron',sans-serif;
    color:#fff;
    padding:20px
}

.container{
    max-width:500px;
    margin:0 auto
}

.header{
    text-align:center;
    padding:25px;
    background:rgba(255,255,255,.03);
    backdrop-filter:blur(20px);
    border:1px solid rgba(255,0,255,.2);
    border-radius:25px;
    margin-bottom:20px
}

.header h1{
    font-size:24px;
    font-weight:900;
    background:linear-gradient(135deg,#ff00ff,#ffaa00);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent
}

.card{
    background:rgba(255,255,255,.03);
    backdrop-filter:blur(25px);
    border:1px solid rgba(255,255,255,.1);
    border-radius:22px;
    padding:25px;
    margin-bottom:20px;
    text-align:center
}

h3{
    color:#ff00ff;
    margin-bottom:15px
}

.btn{
    display:block;
    width:100%;
    padding:14px;
    border:none;
    border-radius:50px;
    font-family:'Orbitron',sans-serif;
    font-size:13px;
    font-weight:700;
    cursor:pointer;
    letter-spacing:2px;
    margin:7px 0;
    text-transform:uppercase
}

.btn-vip{
    background:linear-gradient(135deg,#ff00ff,#cc00cc);
    color:#fff
}

.btn-copy{
    background:linear-gradient(135deg,#00aaff,#0077cc);
    color:#fff
}

.btn-danger{
    background:linear-gradient(135deg,#ff4444,#cc0000);
    color:#fff
}

.btn-delete{
    background:linear-gradient(135deg,#ff4444,#990000);
    color:#fff;
    padding:5px 10px;
    font-size:10px;
    width:auto;
    display:inline-block;
    margin-left:3px
}

.input-field{
    width:100%;
    padding:14px;
    background:rgba(0,0,0,.5);
    border:2px solid rgba(255,255,255,.2);
    border-radius:50px;
    color:#fff;
    font-family:'Orbitron',sans-serif;
    font-size:13px;
    outline:none;
    margin:7px 0
}

.input-field:focus{
    border-color:#ff00ff
}

.toast{
    position:fixed;
    top:20px;
    left:50%;
    transform:translateX(-50%);
    background:#00ff88;
    color:#000;
    padding:12px 25px;
    border-radius:50px;
    font-weight:700;
    z-index:9999;
    opacity:0;
    pointer-events:none;
    transition:opacity .3s
}

.toast.show{
    opacity:1
}

table{
    width:100%;
    border-collapse:collapse;
    font-size:10px;
    margin-top:15px
}

th{
    background:rgba(255,0,255,.1);
    padding:10px;
    color:#ff00ff;
    text-align:left
}

td{
    padding:8px;
    border-bottom:1px solid rgba(255,255,255,.05)
}

.key-green{
    color:#00ff88;
    font-weight:700
}

.stats{
    display:flex;
    gap:10px;
    justify-content:center;
    flex-wrap:wrap;
    margin-bottom:15px
}

.stat-box{
    background:rgba(0,0,0,.4);
    padding:15px;
    border-radius:15px;
    text-align:center;
    min-width:80px
}

.stat-box .num{
    font-size:22px;
    font-weight:900
}

.green{
    color:#00ff88
}

.pink{
    color:#ff00ff
}

.blue{
    color:#00aaff
}

.stat-box .label{
    font-size:10px;
    color:rgba(255,255,255,.4)
}

.result-box{
    background:rgba(0,0,0,.5);
    border-radius:12px;
    padding:12px;
    margin-top:10px;
    max-height:180px;
    overflow-y:auto;
    text-align:left
}

.result-item{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:8px;
    margin:3px 0;
    background:rgba(0,255,136,.05);
    border-radius:8px;
    font-size:11px
}

a{
    color:rgba(255,255,255,.4);
    text-decoration:none;
    font-size:11px
}
</style>'''


@app.route('/')
def login():
    if session.get('admin'):
        return redirect('/dashboard')

    return f'''<!DOCTYPE html>
<html>
<head>
<title>Admin</title>
<meta name="viewport" content="width=device-width,initial-scale=1.0">
{CSS}
</head>

<body>

<div class="container" style="margin-top:50px;">

<div class="header">
<h1>🔐 ADMIN</h1>
</div>

<div class="card">

<form method="POST" action="/login">

<input class="input-field"
       name="username"
       placeholder="Username"
       required>

<input class="input-field"
       name="password"
       type="password"
       placeholder="Password"
       required>

<button class="btn btn-vip" type="submit">
ĐĂNG NHẬP
</button>

</form>

{'<p style="color:#ff4444;">Sai!</p>' if request.args.get('error') else ''}

</div>
</div>

</body>
</html>'''


@app.route('/login', methods=['POST'])
def login_post():

    if (
        request.form.get('username') == ADMIN_USER
        and request.form.get('password') == ADMIN_PASS
    ):
        session['admin'] = True
        return redirect('/dashboard')

    return redirect('/?error=1')


@app.route('/logout')
def logout():

    session.pop('admin', None)

    return redirect('/')


@app.route('/dashboard')
def dashboard():

    if not session.get('admin'):
        return redirect('/')

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM vip_keys WHERE is_banned=0")
    tv = c.fetchone()[0]

    c.execute(
        "SELECT COUNT(*) FROM vip_keys WHERE is_used=1 AND is_banned=0"
    )
    uv = c.fetchone()[0]

    c.execute("""
        SELECT key_code,package,expiry,is_used
        FROM vip_keys
        WHERE is_banned=0
        ORDER BY id DESC
        LIMIT 50
    """)

    keys = c.fetchall()

    conn.close()

    rows = ""

    for k in keys:

        status = (
            '<span style="color:#ffaa00">USED</span>'
            if k[3]
            else
            '<span style="color:#00ff88">FREE</span>'
        )

        rows += f'''
        <tr>
            <td class="key-green">{k[0]}</td>
            <td>{k[1]}</td>
            <td style="font-size:10px;">
                {k[2] if k[2] else "Chưa kích hoạt"}
            </td>
            <td>{status}</td>

            <td>
                <button
                    class="btn btn-copy"
                    style="padding:5px 10px;font-size:10px;width:auto;"
                    onclick="copyKey('{k[0]}')">
                    COPY
                </button>

                <button
                    class="btn btn-delete"
                    onclick="deleteKey('{k[0]}')">
                    XÓA
                </button>
            </td>
        </tr>
        '''

    return render_template_string(f'''<!DOCTYPE html>

<html>

<head>

<title>Admin VIP</title>

<meta name="viewport"
      content="width=device-width,initial-scale=1.0">

{CSS}

</head>

<body>

<div class="toast" id="toast"></div>

<div class="container">

<div class="header">

<h1>👑 ADMIN PANEL</h1>

<p>KEY VIP</p>

</div>


<div class="stats">

<div class="stat-box">
<div class="num green">{tv}</div>
<div class="label">TỔNG</div>
</div>

<div class="stat-box">
<div class="num pink">{uv}</div>
<div class="label">ĐÃ DÙNG</div>
</div>

<div class="stat-box">
<div class="num blue">{tv-uv}</div>
<div class="label">CÒN</div>
</div>

</div>


<div class="card">

<h3>💎 TẠO KEY VIP</h3>

<select class="input-field" id="pkg">

{"".join(
    f'<option value="{k}">{v["name"]}</option>'
    for k,v in PACKAGES.items()
)}

</select>

<input
    class="input-field"
    id="qty"
    value="1"
    min="1"
    max="100"
    type="number"
    placeholder="Số lượng"
>

<button
    class="btn btn-vip"
    onclick="createKeys()">
    💎 TẠO KEY
</button>

<div
    class="result-box"
    id="resultBox"
    style="display:none;">
</div>

</div>


<div class="card">

<h3>📋 DANH SÁCH KEY</h3>

<table>

<tr>
<th>KEY</th>
<th>GÓI</th>
<th>HẾT HẠN</th>
<th>TT</th>
<th>QUẢN LÝ</th>
</tr>

{rows}

</table>

</div>


<a
    href="/logout"
    class="btn btn-danger">
    🚪 ĐĂNG XUẤT
</a>

</div>


<script>

function showToast(m){{
    var t=document.getElementById("toast");

    t.textContent=m;

    t.classList.add("show");

    setTimeout(
        ()=>t.classList.remove("show"),
        2000
    );
}}


function copyKey(k){{
    navigator.clipboard.writeText(k)
    .then(
        ()=>showToast("✅ Đã copy: "+k)
    );
}}


function deleteKey(k){{

    if(!confirm(
        "Bạn có chắc muốn xóa key "+k+" không?"
    )){{
        return;
    }}

    fetch("/api/delete-key",{{

        method:"POST",

        headers:{{
            "Content-Type":"application/json"
        }},

        credentials:"same-origin",

        body:JSON.stringify({{
            key:k
        }})

    }})

    .then(async r => {{

        var d = await r.json();

        if(!r.ok){{
            throw new Error(
                d.error || "API lỗi: "+r.status
            );
        }}

        return d;

    }})

    .then(d => {{

        if(d.success){{

            showToast("✅ Đã xóa key!");

            setTimeout(
                ()=>location.reload(),
                700
            );

        }}else{{

            showToast(
                "❌ "+(d.error || "Không thể xóa key")
            );

        }}

    }})

    .catch(e => {{

        showToast("❌ "+e.message);

    }});

}}


function createKeys(){{

    var p =
        document.getElementById("pkg").value;

    var q =
        parseInt(
            document.getElementById("qty").value
        );

    if(!q || q < 1 || q > 100){{

        showToast(
            "❌ Số lượng không hợp lệ!"
        );

        return;
    }}

    fetch("/api/create",{{

        method:"POST",

        headers:{{
            "Content-Type":"application/json"
        }},

        credentials:"same-origin",

        body:JSON.stringify({{
            package:p,
            quantity:q
        }})

    }})

    .then(async r => {{

        var d = await r.json();

        if(!r.ok){{
            throw new Error(
                d.error || "API lỗi: "+r.status
            );
        }}

        return d;

    }})

    .then(d => {{

        var b =
            document.getElementById("resultBox");

        if(
            !d.keys ||
            !Array.isArray(d.keys)
        ){{
            throw new Error(
                "API không trả về danh sách key"
            );
        }}

        b.style.display="block";

        b.innerHTML =
            d.keys.map(k =>

                '<div class="result-item">' +

                '<span style="color:#00ff88;">' +
                k.key +
                '</span>' +

                '<span style="font-size:10px;">' +
                (k.expiry || "Chưa kích hoạt") +
                '</span>' +

                '<button class="btn btn-copy" ' +
                'style="padding:4px 8px;font-size:10px;width:auto;" ' +
                'onclick="copyKey(\\'' +
                k.key +
                '\\')">COPY</button>' +

                '</div>'

            ).join("");

        showToast(
            "✅ Đã tạo "+d.keys.length+" key!"
        );

        setTimeout(
            ()=>location.reload(),
            3000
        );

    }})

    .catch(err => {{

        console.error(
            "CREATE KEY ERROR:",
            err
        );

        showToast(
            "❌ "+err.message
        );

    }});

}}

</script>

</body>

</html>''')


@app.route('/api/create', methods=['POST'])
def api_create():

    if not session.get('admin'):
        return jsonify({
            "error":"Unauthorized"
        }),401

    try:

        data = request.get_json(
            silent=True
        ) or {}

        pkg = data.get(
            'package',
            '1day'
        )

        qty = int(
            data.get(
                'quantity',
                1
            )
        )

        if pkg not in PACKAGES:

            return jsonify({
                "error":"Sai gói!"
            }),400

        if qty < 1 or qty > 100:

            return jsonify({
                "error":
                "Số lượng phải từ 1 đến 100!"
            }),400

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        keys = []

        for _ in range(qty):

            key = gen_key()

            now = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # Chưa kích hoạt nên chưa có expiry
            expiry = None

            try:

                c.execute(
                    """
                    INSERT INTO vip_keys
                    (key_code,package,created_at,expiry)
                    VALUES(?,?,?,?)
                    """,
                    (
                        key,
                        pkg,
                        now,
                        expiry
                    )
                )

                keys.append({
                    "key":key,
                    "expiry":expiry,
                    "package":pkg
                })

            except sqlite3.IntegrityError:

                continue

        conn.commit()
        conn.close()

        return jsonify({
            "keys":keys,
            "count":len(keys)
        })

    except Exception as e:

        return jsonify({
            "error":str(e)
        }),500


@app.route('/api/delete-key', methods=['POST'])
def api_delete_key():

    if not session.get('admin'):
        return jsonify({
            "error":"Unauthorized"
        }),401

    try:

        data = request.get_json(
            silent=True
        ) or {}

        key = data.get(
            'key',
            ''
        ).strip().upper()

        if not key:

            return jsonify({
                "error":"Thiếu key!"
            }),400

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "DELETE FROM vip_keys WHERE key_code=?",
            (key,)
        )

        if c.rowcount == 0:

            conn.close()

            return jsonify({
                "error":"Key không tồn tại!"
            }),404

        conn.commit()
        conn.close()

        return jsonify({
            "success":True,
            "message":"Đã xóa key!"
        })

    except Exception as e:

        return jsonify({
            "error":str(e)
        }),500


@app.route('/api/verify', methods=['POST'])
def api_verify():

    data = request.get_json(
        silent=True
    ) or {}

    key_code = data.get(
        'key_code',
        ''
    ).strip().upper()

    device_id = data.get(
        'device_id',
        'unknown'
    )

    if not key_code:

        return jsonify({
            "valid":False,
            "reason":"Nhập key!"
        })

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT * FROM vip_keys WHERE key_code=?",
        (key_code,)
    )

    k = c.fetchone()

    if not k:

        conn.close()

        return jsonify({
            "valid":False,
            "reason":"Key không tồn tại!"
        })

    _, _, pkg, _, expiry, dev, used, banned = k

    if banned:

        conn.close()

        return jsonify({
            "valid":False,
            "reason":"Key bị khóa!"
        })

    if used and dev and dev != device_id:

        conn.close()

        return jsonify({
            "valid":False,
            "reason":"Key đã dùng thiết bị khác!"
        })

    # KEY CHƯA KÍCH HOẠT
    # Thời gian bắt đầu tính từ lúc nhập key lần đầu

    if not used:

        days = PACKAGES[pkg]["days"]

        activated_at = datetime.now()

        expiry_dt = (
            activated_at +
            timedelta(days=days)
        )

        expiry = expiry_dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        c.execute(
            """
            UPDATE vip_keys
            SET device_id=?,
                is_used=1,
                expiry=?
            WHERE key_code=?
            """,
            (
                device_id,
                expiry,
                key_code
            )
        )

        conn.commit()
        conn.close()

        return jsonify({

            "valid":True,

            "expiry":expiry,

            "package":pkg,

            "duration":days * 24,

            "is_vip":True,

            "is_forever":
                pkg == 'forever',

            "message":
                "✅ Key VIP hợp lệ!"

        })

    # KEY ĐÃ KÍCH HOẠT

    if not expiry:

        conn.close()

        return jsonify({

            "valid":False,

            "reason":
                "Key không có thời hạn!"

        })

    exp_dt = datetime.strptime(
        expiry,
        "%Y-%m-%d %H:%M:%S"
    )

    if exp_dt < datetime.now():

        conn.close()

        return jsonify({

            "valid":False,

            "reason":
                "Key đã hết hạn!"

        })

    conn.close()

    days = PACKAGES[pkg]["days"]

    return jsonify({

        "valid":True,

        "expiry":expiry,

        "package":pkg,

        "duration":days * 24,

        "is_vip":True,

        "is_forever":
            pkg == 'forever',

        "message":
            "✅ Key VIP hợp lệ!"

    })


if __name__ == '__main__':

    init_db()

    port = int(
        os.environ.get(
            'PORT',
            8080
        )
    )

    app.run(
        host='0.0.0.0',
        port=port
    )
