# dfa_trie.py
from typing import List
from pathlib import Path

def build_trie_dot(keywords: List[str], out_path: str) -> str:
    trie = {}
    end_states = set()
    next_id = 0
    root = 0
    trie[root] = {}

    def new_node():
        nonlocal next_id, trie
        next_id += 1
        trie[next_id] = {}
        return next_id

    for word in sorted(keywords):
        cur = root
        for ch in word:
            if ch not in trie[cur]:
                nid = new_node()
                trie[cur][ch] = nid
            cur = trie[cur][ch]
        end_states.add(cur)

    lines = []
    lines.append('digraph Trie {')
    lines.append('  rankdir=LR;')
    lines.append('  node [shape=circle];')
    for nid in trie:
        attrs = []
        if nid == root:
            attrs.append('label="q0"')
        else:
            attrs.append(f'label="{nid}"')
        if nid in end_states:
            attrs.append('peripheries=2')
        lines.append(f'  n{nid} [{", ".join(attrs)}];')
    for nid, edges in trie.items():
        for ch, child in edges.items():
            label = ch.replace('"', '\\"')
            lines.append(f'  n{nid} -> n{child} [label="{label}"];')
    lines.append('}')
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    return out_path
