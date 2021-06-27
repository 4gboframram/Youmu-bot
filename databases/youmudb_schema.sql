BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "prefixes" (
	"guild_id"	INTEGER NOT NULL,
	"prefix"	TEXT NOT NULL,
	UNIQUE("guild_id","prefix")
);
CREATE TABLE IF NOT EXISTS "levels" (
	"guild_id"	INTEGER NOT NULL,
	"member_id"	INTEGER NOT NULL,
	"level"	INTEGER NOT NULL DEFAULT 1,
	"exp"	INTEGER NOT NULL DEFAULT 0,
	UNIQUE("guild_id","member_id")
);
CREATE TABLE IF NOT EXISTS "bot_channels" (
	"channel_id"	INTEGER NOT NULL,
	UNIQUE("channel_id")
);
CREATE TABLE IF NOT EXISTS "xp_channels" (
	"channel_id"	INTEGER NOT NULL,
	UNIQUE("channel_id")
);
CREATE UNIQUE INDEX IF NOT EXISTS "idx_prefix_guild" ON "prefixes" (
	"guild_id"
);
CREATE INDEX IF NOT EXISTS "idx_level_guild" ON "levels" (
	"guild_id"
);
CREATE INDEX IF NOT EXISTS "idx_level_member" ON "levels" (
	"member_id"
);
COMMIT;
