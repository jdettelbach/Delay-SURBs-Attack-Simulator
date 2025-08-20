import json
import sys

conf = {}

def load(filepath):
    global conf
    print("Settings are being loaded from: %s" % filepath)
    try:
        return json.loads(open(filepath).read())
        # print("Loaded: " + str(conf))
    except Exception:
        print("Scenario file not found!")
        sys.exit(1)

def save(filepath, conf):
    print("Settings are being saved to :%s" % filepath)
    json_obj = json.dumps(conf)
    with open(filepath, 'w') as f:
        f.write(json_obj)
