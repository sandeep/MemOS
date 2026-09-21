with open('src/models.py', 'r') as f:
    content = f.read()
    
content = content.replace("nodes: List[Dict[str, Any]]", "nodes: List[Any]")
content = content.replace("edges: List[Dict[str, Any]]", "edges: List[Any]")
content = content.replace("events: List[Dict[str, Any]]", "events: List[Any]")
content = content.replace("decisions: List[Dict[str, Any]]", "decisions: List[Any]")
content = content.replace("rejected_branches: List[Dict[str, Any]]", "rejected_branches: List[Any]")

with open('src/models.py', 'w') as f:
    f.write(content)
