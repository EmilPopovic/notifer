import logging
import boto3

logger = logging.getLogger(__name__)

def get_file_key(email: str) -> str:
    return f"{email.replace('@', '_').replace('.', '-')}.ics"

class S3Client:

    def __init__(
            self,
            endpoint_url: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            bucket_name: str,
    ):
        self.__endpoint_url = endpoint_url
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__bucket_name = bucket_name

        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=self.__aws_access_key_id,
            aws_secret_access_key=self.__aws_secret_access_key,
        )

    def save_calendar(self, email: str, ics_content: str) -> str | None:
        """
        Updates (or creates if it doesn't exist) a calendar for a user in S3 storage.

        :param email: The user's email address.
        :param ics_content: The calendar content in iCalendar format.
        :return: The URL of the uploaded calendar file.
        """
        file_key = get_file_key(email)

        try:
            self.s3.put_object(
                Bucket=self.__bucket_name,
                Key=file_key,
                Body=ics_content.encode('utf-8'),
                ContentType='text/calendar',
            )
            url = self.get_calendar_url(email)
            logger.info(f'Successfully updated calendar for {email}')
            return url
        except Exception as e:
            logger.error(f'Error updating calendar for {email}: {e}')
            return None

    def get_calendar(self, email: str) -> str | None:
        """
        Retrieves the calendar content of a user from S3 storage.

        :param email: The user's email address.
        :return: The calendar content as a string, or None if not found.
        """
        file_key = get_file_key(email)

        try:
            response = self.s3.get_object(Bucket=self.__bucket_name, Key=file_key)
            logger.info(f'Successfully retrieved calendar for {email}')
            return response['Body'].read().decode('utf-8')
        except self.s3.exceptions.NoSuchKey:
            logger.warning(f'Calendar content not found for {email}')
            return None
        except Exception as e:
            print(f'Error retrieving calendar for {email}: {e}')
            return None

    def delete_calendar(self, email: str):
        """
        Deletes the calendar file of a user from S3 storage.

        :param email: The user's email address.
        """
        file_key = get_file_key(email)

        try:
            self.s3.delete_object(Bucket=self.__bucket_name, Key=file_key)
            logger.info(f'successfully deleted calendar for {email}')
        except Exception as e:
            logger.error(f'Error deleting calendar for {email}: {e}')

    def get_calendar_url(self, email: str) -> str:
        """
        Generages the public URL of a user's calendar file.

        :param email: The user's email address.
        :return: The URL of the calendar file.
        """
        file_key = get_file_key(email)
        return f'{self.__endpoint_url}/{self.__bucket_name}/{file_key}'
