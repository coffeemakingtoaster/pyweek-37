import os

# Print message only if 'DEBUG_LOG' variable is set to true
def debug_log(message: str) -> None:
   if os.getenv("DEBUG_LOG") == "TRUE":
      print(message)
