from app.meta.meta_store import load_meta_store, save_meta_store

def prune_meta_memory():
    """
    Cleanses the meta memory storage of:
    - Zero-weight or low confidence policies (< 0.05)
    - Dead strategies (< 0.05 confidence/success)
    - Older reflections (retaining the 50 most recent)
    - Expired failure logs (retaining the 50 most recent)
    """
    store = load_meta_store()

    # 1. Prune policies
    policies = store.setdefault("planner_policies", {})
    pruned_policies = {}
    for p_id, p in policies.items():
        if p.get("confidence", 1.0) >= 0.05 and p.get("success_rate", 1.0) >= 0.05:
            pruned_policies[p_id] = p
    store["planner_policies"] = pruned_policies

    # 2. Prune strategies
    strategies = store.setdefault("strategies", {})
    pruned_strategies = {}
    for s_id, s in strategies.items():
        if s.get("confidence", 1.0) >= 0.05 and s.get("success_rate", 1.0) >= 0.05:
            pruned_strategies[s_id] = s
    store["strategies"] = pruned_strategies

    # 3. Prune reflections (keep latest 50)
    reflections = store.setdefault("meta_reflections", {})
    sorted_refl = sorted(reflections.values(), key=lambda r: r.get("timestamp", ""), reverse=True)
    store["meta_reflections"] = {r["reflection_id"]: r for r in sorted_refl[:50]}

    # 4. Prune expired failures (keep latest 50 of each type)
    tf = store.setdefault("tool_failures", {})
    sorted_tf = sorted(tf.values(), key=lambda x: x.get("last_seen", ""), reverse=True)
    store["tool_failures"] = {x["failure_id"]: x for x in sorted_tf[:50]}

    pf = store.setdefault("policy_failures", {})
    sorted_pf = sorted(pf.values(), key=lambda x: x.get("last_seen", ""), reverse=True)
    store["policy_failures"] = {x["failure_id"]: x for x in sorted_pf[:50]}

    rf = store.setdefault("reflection_failures", {})
    sorted_rf = sorted(rf.values(), key=lambda x: x.get("last_seen", ""), reverse=True)
    store["reflection_failures"] = {x["failure_id"]: x for x in sorted_rf[:50]}

    save_meta_store()
