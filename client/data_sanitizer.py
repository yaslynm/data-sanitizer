#
# DataSanitizer API functions, supporting downloading and uploading
# files to S3.
#
# Authors:
#   Kai'lyn Mohammed
#   Yas'lyn Mohammed
#   Reem Khalid
#   Prof. Joe Hummel (initialize, get_ping, get_bucket)
#


import os
import logging
import boto3
import uuid
from botocore.client import Config
from configparser import ConfigParser


###################################################################
#
# initialize
#
# Initializes local environment need to access AWS, based on
# given configuration file and user profiles. Call this function
# only once, and call before calling any other API functions.
#
# NOTE: does not check to make sure we can actually reach and
# login to S3 and database server. Call get_ping() to check.
#
def initialize(config_file, s3_profile):
    """
    Initializes local environment for AWS access, returning True
    if successful and raising an exception if not. Call this 
    function only once, and call before calling any other API
    functions.
    
    Parameters
    ----------
    config_file is the name of configuration file, probably 'photoapp-config.ini'
    s3_profile to use for accessing S3, probably 's3readwrite'
    mysql_user to use for accessing database, probably 'photoapp-read-write'
    
    Returns
    ---------
    True if successful, raises an exception if not
  """

    try:
        #
        # save name of config file for other API functions:
        #
        global PHOTOAPP_CONFIG_FILE
        PHOTOAPP_CONFIG_FILE = config_file

        #
        # configure boto for S3 access, make sure we can read necessary
        # configuration info:
        #
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        boto3.setup_default_session(profile_name=s3_profile)

        configur = ConfigParser()
        configur.read(config_file)
        bucketname = configur.get('s3', 'bucket_name')
        regionname = configur.get('s3', 'region_name')

#     #
#     # also check to make sure we can read database server config info:
#     #
#     endpoint = configur.get('rds', 'endpoint')
#     portnum = int(configur.get('rds', 'port_number'))
#     username = configur.get('rds', 'user_name')
#     pwd = configur.get('rds', 'user_pwd')
#     dbname = configur.get('rds', 'db_name')

#     if username == mysql_user:
#       # we have password, all is good:
#       pass
#     else:
#       raise ValueError("mysql_user does not match user_name in [rds] section of config file")

        #
        # success:
        #
        return True

    except Exception as err:
        logging.error("initialize():")
        logging.error(str(err))
        raise


###################################################################
#
# get_ping
#
# To "ping" a system is to see if it's up and running. This 
# function pings the bucket and the database server to make
# sure they are up and running. Returns a tuple (M, N), where
#
#   M = # of items in the S3 bucket
#
# If an error occurs / a service is not accessible, M or N
# will be an error message. Hopefully the error messages will
# convey what is going on (e.g. no internet connection).
#
def get_ping():
    """
    Based on the configuration file, retrieves the # of items in the S3 bucket and
    the # of users in the photoapp.users table. Both values are returned as a tuple
    (M, N), where M or N are replaced by error messages if an error occurs or a
    service is not accessible.
     
    Parameters
    ----------
    N/A

    Returns
    -------
    the tuple (M, N) where M is the # of items in the S3 bucket and
    N is the # of users in the photoapp.users table. If S3 is not
    accessible then M is an error message; if database server is not
    accessible then N is an error message.
    """

    def get_M():
        try:
            #
            # access S3 and obtain the # of items in the bucket:
            #
            bucket = get_bucket()
            assets = bucket.objects.all()

            M = len(list(assets))
            return M

        except Exception as err:
            logging.error("get_ping.get_M():")
            logging.error(str(err))
            raise

        finally:
            try:
                bucket.close()
            except:
                pass

    try:
        M = get_M()
    except Exception as err:
        M = str(err)

    return (M)


###################################################################
#
# get_bucket
#
# create and return bucket object, based on configuration
# information in app config file. You should call close() 
# on the object when you are done.
#
def get_bucket():
    """
    Reads the configuration info from app config file, creates
    a bucket object based on this info, and returns it. You 
    should call close() on the object when you are done.

    Parameters
    ----------
    N/A

    Returns
    -------
    S3 bucket object
    """

    try:
        #
        # configure S3 access using config file:
        #  
        configur = ConfigParser()
        configur.read(PHOTOAPP_CONFIG_FILE)
        bucketname = configur.get('s3', 'bucket_name')
        regionname = configur.get('s3', 'region_name')

        s3 = boto3.resource(
            's3',
            region_name=regionname,
            config = Config(
                retries = {
                    'max_attempts': 3,
                    'mode': 'standard'
                }
            )
        )
        
        bucket = s3.Bucket(bucketname)
        return bucket
  
    except Exception as err:
        logging.error("get_bucket():")
        logging.error(str(err))
        raise


###################################################################
#
# post_file
#
def post_file(local_filename):

    bucket = None

    try:
        if local_filename is None:
            raise ValueError("no filename")
        if not os.path.isfile(local_filename):
            raise FileNotFoundError(local_filename)
        
        unique_str = str(uuid.uuid4())
        key = f"original/{unique_str}_{local_filename}"
        bucket = get_bucket()
        bucket.upload_file(local_filename, key)

    except Exception as err:
        logging.error("post_file():")
        logging.error(str(err))
        raise

    finally: 
        try:
            if bucket is not None:
                bucket.close()
        except:
            pass