from flask import Flask, request, jsonify, render_template
from db import events_collection
from datetime import datetime, timedelta
from pytz import timezone
import pytz

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    action_type = request.headers.get('X-GitHub-Event')
    event = None  # initialize

    # for push
    if action_type == "push":
        event = {
            "author": data["pusher"]["name"],
            "action": "push",
            "from_branch": None,
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": datetime.utcnow()
        }

    # for pull
    elif action_type == "pull_request":
        pr = data.get("pull_request")
        pr_action = data.get("action")

        if pr and pr_action == "opened":
            event = {
                "author": pr["user"]["login"],
                "action": "pull_request",
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": datetime.utcnow()
            }

        elif pr and pr_action == "closed" and pr.get("merged"):
            event = {
                "author": pr["user"]["login"],
                "action": "merge",
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": datetime.utcnow()
            }

    if event:
        events_collection.insert_one(event)
        return jsonify({"message": "Event stored"}), 200
    else:
        return jsonify({"message": "Skipped or unhandled event"}), 204




@app.route('/latest')
def latest():
    date_str = request.args.get("date")  # Format: YYYY-MM-DD
    now = datetime.utcnow().replace(tzinfo=pytz.utc)

    query = {}
    # date formating for mongodb storage
    if date_str:
        try:
            ist = timezone('Asia/Kolkata')
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            start_ist = ist.localize(datetime.combine(date_obj, datetime.min.time()))
            end_ist = start_ist + timedelta(days=1)

            start_utc = start_ist.astimezone(pytz.utc)
            end_utc = end_ist.astimezone(pytz.utc)

            query["timestamp"] = {"$gte": start_utc, "$lt": end_utc}
        except Exception as e:
            print("Date parsing failed:", e)

    events = list(events_collection.find(query).sort("timestamp", -1).limit(10))

    for e in events:
        e["_id"] = str(e["_id"])
        ist = timezone('Asia/Kolkata')
        local_time = e["timestamp"].replace(tzinfo=pytz.utc).astimezone(ist)
        e["timeago"] = time_ago(now, e["timestamp"])
        e["timestamp"] = local_time.strftime("%d %b %Y - %I:%M %p IST")

    return jsonify(events)

def time_ago(now, past):
    diff = now - past.replace(tzinfo=pytz.utc)
    seconds = int(diff.total_seconds())
    minutes = seconds // 60
    hours = minutes // 60

    if seconds < 30:
        return "Just now"
    elif minutes < 1:
        return f"{seconds} sec ago"
    elif minutes < 60:
        return f"{minutes} min ago"
    elif hours < 24:
        return f"{hours} hr ago"
    else:
        return past.strftime("%d %b %Y")

if __name__ == '__main__':
    app.run(debug=True)
