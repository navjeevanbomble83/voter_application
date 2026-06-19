import os
import redis as redislib
from flask import Flask, render_template_string, request, redirect, jsonify

app = Flask(__name__)

TEAM_NAME  = os.environ.get("TEAM_NAME", "Blue Team")
BG_COLOR   = os.environ.get("BG_HEX", "#1a237e")
ACCENT     = os.environ.get("ACCENT_HEX", "#42a5f5")
REDIS_HOST = os.environ.get("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
# REDIS_PASS = os.environ.get("REDIS_PASSWORD", None)
VOTE_KEY   = os.environ.get("VOTE_KEY", "red_votes")

# Connect to Redis (graceful degradation if unavailable)
try:
    r = redislib.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=3)
    r.ping()
    REDIS_OK = True
except Exception as e:
    print(f"Redis connection failed: {e}")
    r = None
    REDIS_OK = False

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

<form method="POST" action={{ rv_api }}>
<button class="btn" type="submit">CAST VOTE</button>
</form>
<div class="status">Redis: {{ "✅ Connected" if redis_ok else "❌ Disconnected (in-memory)" }}</div>
<div class="info">Pod: {{ pn }} | NS: {{ ns }}</div>

</div>
</body>
</html>
"""

@app.route("/")
def welcome():
    return """
    <h1>Voting Application</h1>
    <a href="/red">Red Team</a><br>
    <a href="/blue">Blue Team</a>
    """    
    
@app.route("/red")
@app.route("/blue")
def index():
    vc = 0
    route_vote_api = f"/{TEAM_NAME.lower().split()[0]}/vote"
    if REDIS_OK and r:
        try:
            vc = int(r.get(VOTE_KEY) or 0)
        except:
            pass
    return render_template_string(TEMPLATE, nm=TEAM_NAME, bg=BG_COLOR,
        ac=ACCENT, vc=vc, redis_ok=REDIS_OK, rv_api = route_vote_api,
        pn=os.environ.get("HOSTNAME","?"),
        ns=os.environ.get("POD_NAMESPACE","?"))

@app.route("/red/vote", methods=["POST"])
@app.route("/blue/vote", methods=["POST"])
def vote():
    if REDIS_OK and r:
        try:
            r.incr(VOTE_KEY)
        except:
            pass
    return redirect(request.referrer or "/")

@app.route("/healthz")
def health():
    return jsonify(status="ok",redis=REDIS_OK), 200
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
