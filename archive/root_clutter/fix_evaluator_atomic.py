with open("src/evaluator.py", "r") as f:
    content = f.read()
content = content.replace("import os; os.rename", "os.rename")
with open("src/evaluator.py", "w") as f:
    f.write(content)
