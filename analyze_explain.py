import json
import sys


def analyze_node(node):
    res = [node["Node Type"]]
    if "Plans" in node:
        for n in node["Plans"]:
            res.extend(analyze_node(n))
    return res


def analyze():
    data = json.load(sys.stdin)
    print(analyze_node(data[0]["Plan"]), data[0]["Plan"]["Actual Total Time"])


if __name__ == "__main__":
    analyze()
