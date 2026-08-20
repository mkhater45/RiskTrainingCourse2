"""Project Task 1: test that the implementation actually works
"""

from io import load_folder

connection = load_folder()

result = connection.sql("select count(*) from transactions")

print(result)
