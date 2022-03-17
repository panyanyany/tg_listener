from tg_listener.repo.arctic_repo import arctic_db

print(arctic_db.lib.list_symbols())
for sym in arctic_db.lib.list_symbols():
    data = arctic_db.lib.read(sym)
    if len(data) < 50:
        continue
    print(data)
    print(sym)
