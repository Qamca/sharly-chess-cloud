from database.sqlite.migration import BaseMigration


class Migration(BaseMigration):
    def forward(self):
        self.database.execute(
            'ALTER TABLE `info` ADD COLUMN `cloud_admin_password_hash` TEXT'
        )

    def backward(self):
        # SQLite does not support DROP COLUMN in older versions; recreate the table
        self.database.execute(
            'CREATE TABLE `info_backup` AS SELECT '
            '`force_edit`, `console_log_level`, `console_color`, `console_show_date`, '
            '`console_show_level`, `experimental`, `launch_browser`, `federation`, '
            '`locale`, `date_formatter` FROM `info`'
        )
        self.database.execute('DROP TABLE `info`')
        self.database.execute('ALTER TABLE `info_backup` RENAME TO `info`')
