import json, pandas as pd
cat=pd.read_csv("catalog.csv",dtype={"size":str}); orders=pd.read_csv("orders.csv",dtype=str)
data=json.load(open("conversations_sample.json",encoding="utf-8"))["conversations"]
ACTIONS={"check_stock","recommend","answer_policy","create_order","request_confirmation","get_order_status",
         "deny_status_mismatch","create_exchange","escalate"}
errs=[]; ids=set()
for c in data:
    
    i=c["conv_id"]; e=c["expected"]
    if i in ids: errs.append(f"{i}: duplicate id")
    ids.add(i)
    if e["expected_action"] not in ACTIONS: errs.append(f"{i}: bad action {e['expected_action']}")
    if e["should_escalate"]!=(e["expected_action"]=="escalate"): errs.append(f"{i}: escalate flag mismatch")
    if e["should_escalate"]!=bool(e["escalation_reason"]): errs.append(f"{i}: escalation_reason mismatch")
    for x in e["entities"]["items"]:
        m=cat[(cat.name==x["product"])&(cat.color==x["color"])&(cat["size"]==x["size"])]
        if m.empty: errs.append(f"{i}: not in catalog {x}")
    oid=e["entities"]["order_id"]
    if oid and oid not in set(orders.order_id): errs.append(f"{i}: unknown order {oid}")
    if not any(t["speaker"]=="customer" for t in c["turns"]): errs.append(f"{i}: no turns")
print("conversations:",len(data)); print("errors:",len(errs)); [print(" -",x) for x in errs]
print(pd.Series([c["category"] for c in data]).value_counts().to_string())
print("escalations:",sum(c["expected"]["should_escalate"] for c in data),"hard:",sum(c["difficulty"]=="hard" for c in data))
