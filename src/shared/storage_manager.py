import logging
import os

logger = logging.getLogger(__name__)

def get_file_key(email: str) -> str:
    return f"{email.replace('@', '_').replace('.', '-')}.ics"

class StorageManager:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        self.__storage_path = os.path.join(current_dir, '../..', 'data', 'calendars')
        os.makedirs(self.__storage_path, exist_ok=True)

    def save_calendar(self, email: str, ics_content: str) -> str | None:
        """
        Updates (or creates if it doesn't exist) a calendar for a user in local storage.

        :param email: The user's email address.
        :param ics_content: The calendar content in iCalendar format.
        :return: The URL of the uploaded calendar file.
        """
        file_key = get_file_key(email)
        file_path = os.path.join(self.__storage_path, file_key)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(ics_content)
            url = self.get_calendar_path(email)
            logger.info(f'Successfully updated calendar for {email}')
            return url
        except Exception as e:
            logger.error(f'Error updating calendar for {email}: {e}')
            return None

    def get_calendar(self, email: str) -> str | None:
        """
        Retrieves the calendar content of a user from storage.

        :param email: The user's email address.
        :return: The calendar content as a string, or None if not found.
        """
        file_key = get_file_key(email)
        file_path = os.path.join(self.__storage_path, file_key)

        try:
            if not os.path.exists(file_path):
                logger.warning(f'Calendar content not found for {email}')
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f'Successfully retrieved calendar for {email}')
            return content
        except Exception as e:
            logger.error(f'Error retrieving calendar for {email}: {e}')
            return None

    def delete_calendar(self, email: str):
        """
        Deletes the calendar file of a user from storage.

        :param email: The user's email address.
        """
        file_key = get_file_key(email)
        file_path = os.path.join(self.__storage_path, file_key)

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f'Successfully deleted calendar for {email}')
            else:
                logger.warning(f'Calendar file not found for {email}')
        except Exception as e:
            logger.error(f'Error deleting calendar for {email}: {e}')

    def get_calendar_path(self, email: str) -> str:
        """
        Generages the public URL of a user's calendar file.

        :param email: The user's email address.
        :return: The URL of the calendar file.
        """
        file_key = get_file_key(email)
        return os.path.join(self.__storage_path, file_key)
