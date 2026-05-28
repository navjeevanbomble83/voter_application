import os
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

TEAM_NAME  = os.environ.get("TEAM_NAME", "Blue Team")
BG_COLOR   = os.environ.get("BG_HEX", "#1a237e")
ACCENT     = os.environ.get("ACCENT_HEX", "#42a5f5")

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<title>VoteVibe</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{
  background:{{ bg }};
  font-family:sans-serif;
  min-height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  color:white
}
.card{
  background:rgba(255,255,255,.1);
  border:2px solid {{ ac }};
  border-radius:24px;
  padding:60px 80px;
  text-align:center
}
h1{font-size:3rem;font-weight:800}
.cnt{
  font-size:5rem;
  font-weight:900;
  color:{{ ac }};
  margin:20px 0
}
.btn{
  background:{{ ac }};
  color:#000;
  border:none;
  padding:16px 50px;
  font-size:1.3rem;
  font-weight:700;
  border-radius:50px;
  cursor:pointer
}
.info{
  margin-top:20px;
  font-size:.75rem;
  opacity:.5;
  font-family:monospace
}
</style>
</head>

<body>
<div class="card">
<h1>🔵 {{ nm }}</h1>

<p style="opacity:.6;margin:8px 0 30px">
CloudVibe Internal Voting
</p>

<div class="cnt">{{ vc }}</div>

<p style="opacity:.6;margin-bottom:20px">votes</p>

<form method="POST" action="/vote">
<button class="btn" type="submit">
CAST VOTE
</button>
</form>

<div class="info">
Pod: {{ pn }} | NS: {{ ns }}
</div>

</div>
</body>
</html>
"""

votes = 0

@app.route("/")
def index():
    global votes
    return render_template_string(
        TEMPLATE,
        nm=TEAM_NAME,
        bg=BG_COLOR,
        ac=ACCENT,
        vc=votes,
        pn=os.environ.get("HOSTNAME", "?"),
        ns=os.environ.get("POD_NAMESPACE", "?")
    )

@app.route("/vote", methods=["POST"])
def vote():
    global votes
    votes += 1
    return redirect("/")

@app.route("/healthz")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
