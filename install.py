import os
import random
import string
import base64

def create_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + \
                                 string.digits) for x in range(length))


class DiffgramInstallTool:
    static_storage_provider = None
    bucket_name = None
    gcp_credentials_path = None
    s3_access_id = None
    s3_access_secret = None
    azure_connection_string = None

    def set_static_storage_option(self, option_number):
        if option_number == 1:
            self.static_storage_provider = 'gcp'
        elif option_number == 2:
            self.static_storage_provider = 'aws'
        elif option_number == 3:
            self.static_storage_provider = 'azure'

    def set_gcp_credentials(self):
        is_valid = False
        # Ask For Service Account
        service_account_path = input('Please provide the Full Path of your GCP service account JSON file: ')
        while not is_valid:
            try:
                if not service_account_path.endswith('.json'):
                    print('Path must be a JSON file')
                    is_valid = False
                    continue
                f = open(service_account_path)
                # Do something with the file
                self.gcp_credentials_path = service_account_path
                is_valid = True
            except IOError:
                print("Invalid path, make sure your are writing the full path to your GCP credentials JSON file")
            finally:
                f.close()
        # Ask for bucket name
        bucket_name = input('Please provide the GCP Storage Bucket Name [Default is diffgram-storage]: ')
        if bucket_name == '':
            self.bucket_name = 'diffgram-storage'
        else:
            self.bucket_name = bucket_name

    def set_s3_credentials(self):
        # Ask For Access Key ID
        is_valid = False
        s3_access_id = input('Please provide the AWS Access Key ID: ')
        while not is_valid:
            if s3_access_id == '':
                continue
            else:
                self.s3_access_id = s3_access_id
                is_valid = True

        # Ask For Access Key Secret
        is_valid = False
        s3_access_secret = input('Please provide the AWS Access Key Secret: ')
        while not is_valid:
            if s3_access_secret == '':
                continue
            else:
                self.s3_access_secret = s3_access_secret
                is_valid = True

        # Ask for bucket name
        bucket_name = input('Please provide the AWS S3 Bucket Name [Default is diffgram-storage]: ')
        if bucket_name == '':
            self.bucket_name = 'diffgram-storage'
        else:
            self.bucket_name = bucket_name

    def set_azure_credentials(self):
        # Ask For Access Key ID
        is_valid = False
        azure_connection_string = input('Please provide the Azure Connection String: ')
        while not is_valid:
            if azure_connection_string == '':
                continue
            else:
                self.azure_connection_string = azure_connection_string
                is_valid = True

        # Ask for bucket name
        bucket_name = input('Please provide the Azure Container Name [Default is diffgram-storage]: ')
        if bucket_name == '':
            self.bucket_name = 'diffgram-storage'
        else:
            self.bucket_name = bucket_name

    def populate_env(self):
        env_file = ''
        print('Generating Environment Variables file...')
        if self.static_storage_provider == 'gcp':
            env_file = 'GCP_SERVICE_ACCOUNT_FILE_PATH={}\n'.format(self.gcp_credentials_path)
            env_file += 'CLOUD_STORAGE_BUCKET={}\n'.format(self.bucket_name)
            env_file += 'ML__CLOUD_STORAGE_BUCKET={}\n'.format(self.bucket_name)
            env_file += 'SAME_HOST=False\n'.format(self.bucket_name)
            env_file += 'DIFFGRAM_STATIC_STORAGE_PROVIDER={}\n'.format(self.static_storage_provider)
        elif self.static_storage_provider == 'aws':
            env_file = 'DIFFGRAM_AWS_ACCESS_KEY_ID={}\n'.format(self.s3_access_id)
            env_file += 'DIFFGRAM_AWS_ACCESS_KEY_SECRET={}\n'.format(self.s3_access_secret)
            env_file += 'DIFFGRAM_S3_BUCKET_NAME={}\n'.format(self.bucket_name)
            env_file += 'ML__DIFFGRAM_S3_BUCKET_NAME={}\n'.format(self.bucket_name)
            env_file += 'SAME_HOST=False\n'.format(self.bucket_name)
            env_file += 'DIFFGRAM_STATIC_STORAGE_PROVIDER={}\n'.format(self.static_storage_provider)
            env_file += 'GCP_SERVICE_ACCOUNT_FILE_PATH={}\n'.format('/dev/null')
        elif self.static_storage_provider == 'azure':
            env_file = 'DIFFGRAM_AZURE_CONNECTION_STRING={}\n'.format(self.azure_connection_string)
            env_file += 'DIFFGRAM_AZURE_CONTAINER_NAME={}\n'.format(self.bucket_name)
            env_file += 'ML__DIFFGRAM_AZURE_CONTAINER_NAME={}\n'.format(self.bucket_name)
            env_file += 'SAME_HOST=False\n'.format(self.bucket_name)
            env_file += 'DIFFGRAM_STATIC_STORAGE_PROVIDER={}\n'.format(self.static_storage_provider)
            env_file += 'GCP_SERVICE_ACCOUNT_FILE_PATH={}\n'.format('/dev/null')

        fernet_key = base64.urlsafe_b64encode(os.urandom(32))
        env_file += 'FERNET_KEY={}\n'.format(fernet_key)
        env_file += 'USER_PASSWORDS_SECRET={}\n'.format(create_random_string(10))
        env_file += 'INTER_SERVICE_SECRET={}\n'.format(create_random_string(10))
        env_file += 'SECRET_KEY={}\n'.format(create_random_string(18))
        env_file += 'WALRUS_SERVICE_URL_BASE={}\n'.format('http://walrus:8080/')

        text_file = open(".env", "w")
        text_file.write(env_file)
        text_file.close()
        print('Environment file written to: {}'.format(os.path.abspath(text_file.name)))

    def launch_dockers(self):
        print('Launching Diffgram...')
        os.system('docker-compose up -d')
        print('Diffgram Successfully Launched!')
        print('View the Web UI at: http://localhost:8085')


    def install(self):
        self.print_logo()
        print('')
        print('')
        print('Welcome To the Diffgram Installer.')
        print('')
        print('')

        print('First We need to know what static storage provider you will use: ')
        print('1. Google Cloud Storage (GCP)')
        print('2. Amazon Web Services S3 (AWS S3)')
        print('3. Microsoft Azure Storage (Azure)')
        option_valid = False
        while not option_valid:
            option = input('Enter 1, 2 or 3. Or write exit to quit the installation: ')

            if option.isnumeric() and int(option) in [1, 2, 3]:
                option_valid = True
                self.set_static_storage_option(int(option))
            elif option == 'exit':
                option_valid = True
                print('Thanks for using Diffgram :)')
                return
            else:
                print('Invalid option. Please enter either 1,2 or 3. Write exit to quit the installation process.')

        if self.static_storage_provider == 'gcp':
            self.set_gcp_credentials()
        elif self.static_storage_provider == 'aws':
            self.set_s3_credentials()
        elif self.static_storage_provider == 'azure':
            self.set_azure_credentials()

        self.populate_env()
        self.launch_dockers()


    def print_logo(self):
        print("""\
        ________  .__  _____  _____                            
        \______ \ |__|/ ____\/ ____\________________    _____  
            |    |  \|  \   __\\   __\/ ___\_  __ \__  \  /      \ 
            |    `   \  ||  |   |  | / /_/  >  | \// __ \|  Y Y   \

        /_______  /__||__|   |__| \___  /|__|  (____  /__|_|  /
                \/               /_____/            \/      \/
        """)

        print(""" 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&####@@@@@@@@@@@#////%#/%#@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#%///*##(///*######%##(///%*/*#*/##@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@##/(#%#//*#//////////////////////%#@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@###/((/////////////////////////////*#%@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@##%%(*##///#////////////////////////////////*#%@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@#**/#**#////////////////////////////////////(#@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@%##%*#(///////#//##%#////(/////////////////////#@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@#(***#*//(/////%,,,,%#%#(,#(///%##*///#///////%#@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@#%**#/////////,,,,,,,,,,,,%#%%,,,##(#,#////##%@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@#%****%#//##//////*,,,,,,,,,,,,,,,,,#%,,,%##&@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@%%***/#*////##////////*#%##%%#(/**,,,,,##@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@#%**/#*//////#///////##%#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@#%*****##*(#///*///////(***%#######@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@##/*##/////////*%%#%(****#%//////#%#@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@##******%%////#//////////###%####//#%%#@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@#%****#(/////////%%*///*/%*%#@@##@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@##(*****##//#////////%#(/#//%*#%@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@&#*****%%///////////((##(**%/%#@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@#////***/#*/#/////////#//******%#@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@#@##*****##*////////////#********#&@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@&###%/*(##***#***%#//////*///////%********#%@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@&#**####****(%##(/#////////////*%*******%#@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@#%//##//*//*//**//////////#/*#******###@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@##*/////////////(#////////(%***%##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@%#%////////////(#////////##*(##&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@&############(//////(#///////*%##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#*////*/*%##%%###&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@##//////*%##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@        
        """)



install_tool = DiffgramInstallTool()
install_tool.install()
