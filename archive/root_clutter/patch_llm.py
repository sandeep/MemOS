import re

with open("src/llm_utils.py", "r") as f:
    code = f.read()

# Change range(5) to range(10)
code = code.replace("for attempt in range(5):", "for attempt in range(10):")

# Change the exception block
old_except = """        except Exception as e:
            print(f"LLM Connection Error: {e}")
            time.sleep(2)"""

new_except = """        except requests.exceptions.Timeout as e:
            sleep_time = 2 ** attempt
            print(f"LLM Timeout Error (Attempt {attempt+1}/10). Retrying in {sleep_time}s...")
            time.sleep(sleep_time)
        except Exception as e:
            sleep_time = 2 ** attempt
            print(f"LLM Connection Error (Attempt {attempt+1}/10): {e}. Retrying in {sleep_time}s...")
            time.sleep(sleep_time)"""

code = code.replace(old_except, new_except)

# Increase timeout from 45 to 90
code = code.replace("timeout=45", "timeout=90")

with open("src/llm_utils.py", "w") as f:
    f.write(code)
print("Patched src/llm_utils.py")
