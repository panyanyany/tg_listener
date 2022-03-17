from tg_listener.repo.arctic_repo import arctic_db

print(arctic_db.lib.list_symbols())
for s in arctic_db.lib.list_symbols():
    arctic_db.lib.delete(s)
