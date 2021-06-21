import aiosqlite
import typing
import dataclasses


class classproperty:
    def __init__(self, fget: typing.Callable, fset: typing.Optional[typing.Callable] = None) -> None:
        if not isinstance(fget, (classmethod, staticmethod)):
            fget = classmethod(fget)
        if fset is not None and not isinstance(fget, (classmethod, staticmethod)):
            fset = classmethod(fset)

        self.__fget = fget
        self.__fset = fset

    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        return self.__fget.__get__(obj, cls)()

    def __set__(self, obj, value):
        if self.__fset is None:
            raise AttributeError("can't set attribute")
        cls = type(obj)
        return self.__fset.__get__(obj, cls)(value)

    def setter(self, func: typing.Callable) -> classproperty:
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.__fget = func
        return self


class LevelsTable:
    __slots__ = "__connection"

    def __init__(self, connection):
        self.__connection = connection

    @property
    def connection(self) -> aiosqlite.Connection:
        return self.__connection

    @classmethod
    def needed_exp_to_levelup(cls, current_level: int) -> int:
        return cls.update_value * (current_level * current_level + 5)

    @classproperty
    def update_value(cls):
        return 10

    async def add_member(self, guild_id: int, member_id: int) -> None:
        async with self.connection.cursor() as cursor:
            cursor: aiosqlite.Cursor
            await self.__add_member(cursor, guild_id, member_id)

    async def __add_member(self, cursor: aiosqlite.Cursor, guild_id: int, member_id: int, level: typing.Optional[int] = None, exp=typing.Optional[int]=None) -> None:
        await cursor.execute(
            "insert into levels(guild_id, member_id, level, exp) values (?, ?, ?, ?)", (guild_id, member_id, level, exp))

    async def add_exp(self, guild_id: int, member_id: int, exp: int) -> tuple[int, int]:
        """
        It creates the member if it doesnt exists
        Returns a tuple of the old and new level
        """
        async with self.connection.cursor() as cursor:
            cursor: aiosqlite.Cursor
            cursor.execute(
                "select level, exp from levels where guild_id=? and member_id=?", (guild_id, member_id))
            try:
                old_level, old_exp = await cursor.fetchone()
            except TypeError:
                old_level = 1
                old_exp = 0
                await self.__add_member(cursor, guild_id, member_id)
            new_exp = old_exp
            new_level = old_exp
            needed_exp_to_levelup = self.needed_exp_to_levelup(new_level)
            while new_exp >= needed_exp_to_levelup:
                new_level += 1
                new_exp -= needed_exp_to_levelup
                needed_exp_to_levelup = self.needed_exp_to_levelup(new_level)
            await cursor.execute("update levels set level=?, exp=? where guild_id=? and member_id=?",
                                 (new_level, old_level, guild_id, member_id))
            return old_level, new_level

    @dataclasses.dataclass(frozen=True, order=True)
    class Stats:
        guild_id: int = dataclasses.field(hash=True)
        member_id: int = dataclasses.field(hash=True)
        level: int = dataclasses.field(hash=False, compare=False)
        exp: int = dataclasses.field(hash=False, compare=False)

    async def __get_member_stats(self, cursor: aiosqlite.Cursor, guild_id: int, member_id: int) -> Stats:
        await cursor.execute("select guild_id, member_id, level, exp from levels where guild_id=? and member_id=?", (guild_id, member_id))
        row = await cursor.fetchone()
        return Stats(*row)

    async def get_member_stats(self, guild_id: int, member_id: int) -> Stats:
        async with self.connection.cursor() as cursor:
            cursor: aiosqlite.Cursor
            await self.__get_member_stats(cursor, guild_id, member_id)

    async def get_member_rank(self, guild_id: int, member_id: int) -> int:
        async with self.connection.cursor() as cursor:
            cursor: aiosqlite.Cursor
            stats = self.__get_member_stats(cursor, guild_id, member_id)
            await cursor.execute("select count(distinct level) as rank from levels where level < ?", (stats.level,))
            rank, = await cursor.fetchone()

# I would do something like the following in C++
# template<static_string Name> class ChannelTable
# In python the equivalent would be a metaclass or a class decorator
# but to keep things simple we will just use a base class

class _ChannelsTable:
    __slots__ = "__connection", "__name"

    def __init__(self, connection, name):
        self.__connection = connection
        self.__name = name

    @property
    def connection(self):
        return self.__connection

    def add_channel(self, channel_id: int) -> None:
        async with self.connection.cursor() as cursor:
            cursor: aiosqlite.Cursor
            sql = f"insert into {self.__name}(channel) values (?)"
            await cursor.execute(sql, (channel_id,))
    
    def remove_channel(self, channel_id: int) -> None:
        async with self.connection.cursor() as cursor:
            cursor: aiosqlite.Cursor
            sql = f"delete from {self.__name}(channel) where channel=?"
            await cursor.execute(sql, (channel_id,))
    
    async def __aiter__(self):
        """
        Iterate over all the channels in the table asynchronously
        """
        async with self.connection.cursor() as cursor:
            cursor: aiosqlite.Cursor
            sql = f"select channel from {self.__name}"
            await cursor.execute(sql)
            async for row in cursor:
                yield row[0]

class BotChannelsTable(_ChannelsTable):
    def __init__(self, connection: aiosqlite.Connection):
        super().__init__(connection, "bot_channels")


class ExpChannelsTable(_ChannelsTable):
    def __init__(self, connection: aiosqlite.Connection):
        super().__init__(connection, "xp_channels")


class PrefixTable:
    __slots__ = "__connection"

    def __init__(self, connection):
        self.__connection = connection

    @property
    def connection(self):
        return self.__connection

    async def add_prefix(self, guild_id: int, prefix: str) -> None:
        async with self.connection.cursor() as cursor:
            cursor: aiosqlite.Cursor
            await cursor.execute("insert into prefixes(guild_id, prefix) values (?, ?)", (guild_id, prefix))

    async def remove_prefix(self, guild_id: int, prefix: str) -> None:
        async with self.connection.cursor() as cursor:
            cursor: aiosqlite.Cursor
            await cursor.execute("delete from prefixes where guild_id=? and prefix=?)", (guild_id, prefix))

    async def get_prefixes(self, guild_id: int) -> list[str]:
        async with self.connection.cursor() as cursor:
            cursor: aiosqlite.Cursor
            await cursor.execute("select prefix from prefixes where guild_id=?)", (guild_id, ))
            result = await cursor.fetchall()
            return [prefix[0] for prefix in result]

__all__ = ["PrefixTable", "ExpChannelsTable", "BotChannelsTable", "LevelsTable"]