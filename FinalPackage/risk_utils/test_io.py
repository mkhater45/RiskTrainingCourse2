"""Project Task 1: test that the implementation actually works
"""

from load_folder import load_folder

connection = load_folder()

result = connection.sql("select count(*) from transactins")

print(result)
