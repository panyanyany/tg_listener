from tg_listener.repo.arctic_repo import arctic_db

print(arctic_db.db_tick.list_symbols())
for s in arctic_db.db_tick.list_symbols():
    arctic_db.db_tick.delete(s)
