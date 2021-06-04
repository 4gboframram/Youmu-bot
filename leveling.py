import sqlite3

async def on_level_up():
		print('Level up!')

class LevelDB:
	def __init__(self,name):
		self.update_value=10
		self.rule=lambda x : self.update_value*(x*x+5)
		self.name=name

		self.connection = sqlite3.connect(f'{self.name}.db')
		self.cursor=self.connection.cursor()
		sqlite_select_Query = "select sqlite_version();"
		self.cursor.execute(sqlite_select_Query)
		record = self.cursor.fetchall()
		print("SQLite Database Version is: ", record)

	def add_guild(self, guild_id):	
		self.cursor.execute(f"CREATE TABLE IF NOT EXISTS g{guild_id}(id INTEGER, level INTEGER, exp INTEGER, UNIQUE(id))")
		self.connection.commit()

	def add_member(self, guild_id, member_id):
		self.cursor.execute(f"INSERT INTO g{guild_id}(id, level, exp) VALUES ({member_id}, 0, 0)")
		self.connection.commit()

	async def add_xp(self, guild_id, member_id, multiplier=1, levelup_event=on_level_up, *args):
		self.cursor.execute(f"SELECT id, level, exp FROM 'g{guild_id}' WHERE id={member_id}")

		member=self.cursor.fetchall()[0]
		self.current_member_id=member[0]
		self.current_member_level=member[1]
		self.current_member_exp=member[2]

		self.cursor.execute(f"UPDATE g{guild_id} SET exp={member[2]+int(self.update_value*multiplier)} WHERE id={member_id}")
		self.connection.commit()

		self.cursor.execute(f"SELECT id, level, exp FROM 'g{guild_id}' WHERE id={member_id}")
		member=self.cursor.fetchall()[0]
		if member[2]>=self.rule(member[1]):
			self.cursor.execute(f"UPDATE g{guild_id} SET level={member[1]+1}, exp=0 WHERE id={member_id}")
			self.connection.commit()

			self.cursor.execute(f"SELECT id, level, exp FROM 'g{guild_id}' WHERE id={member_id}")
			member=self.cursor.fetchall()[0]
			await levelup_event(*args)
		self.connection.commit()
		print(member)
		return member
		
	def print_table(self, guild_id):
		self.cursor.execute(f"SELECT * FROM g{guild_id}")
		print(self.cursor.fetchall())

	def get_member_stats(self, guild_id, member_id):
		self.cursor.execute(f"SELECT id, level, exp FROM 'g{guild_id}' WHERE id={member_id}")
		member=self.cursor.fetchall()[0]
		return member

	def get_sorted_table(self, guild_id):
		self.cursor.execute(f'SELECT * FROM g{guild_id} ORDER BY level DESC, exp DESC')
		table=self.cursor.fetchall()
		print(table)
		return table

	def get_member_rank(self, guild_id, member_id):
		rank=self.get_sorted_table(guild_id).index(self.get_member_stats(guild_id, member_id))+1
		print(rank)
		return rank

	def list_of_tables(self):
		self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY 1;")
		try:
			return  list(zip(*self.cursor.fetchall()))[0]
		except IndexError: return []


	
async def new_level_up(id, level):
	print(f"{id} has leveled up to level {level}")


if __name__=='__main__':
	db=LevelDB('Levels')
	try:
		db.add_guild(1)
	except: pass
	try:
		"""db.add_member(1, 69420)
		db.add_member(1, 69421)"""
		db.add_member(1, 69422)
	except: pass
	#db.add_xp(1, 69421, 1)
	#db.add_xp(1, 69422, 1)
	#db.get_sorted_table(1)
	#db.get_member_rank(1, 69420)
	db.add_guild(2)
	print(db.list_of_tables())