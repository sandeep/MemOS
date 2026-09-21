import re
text = "some text\n{ \"a\": 1 }\nmore text\n{ \"b\": 2 }"
match = re.search(r'\{.*?\}', text, re.DOTALL)
print(match.group(0))
