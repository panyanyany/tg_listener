from tg_listener.repo.arctic_repo import arctic_db

print(arctic_db.db_tick.list_symbols())
for sym in arctic_db.db_tick.list_symbols():
    data = arctic_db.db_tick.read(sym)
    if len(data) < 100:
        continue
    print(data)
    print(sym)
