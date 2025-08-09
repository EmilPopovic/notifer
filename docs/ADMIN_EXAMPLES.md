# PLACEHOLDER_TITLE

## Restore Database Backup

1. **Prepare your backup file:**

    ```bash
    cp ./db_backups/db_YYYY-mm-dd_HH-MM-SS.dump ./db_backups/backup.dump
    ```

2. **Start only postgres and restore the database:**

    ```bash
    docker compose --profile restore up postgres db_restore
    ```

3. **Start the full application:**

    ```bash
    docker compose --profile restore down

    docker compose up -d
    ```
