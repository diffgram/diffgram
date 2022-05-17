# -*- coding: utf-8 -*-
import os
import uuid
import string
import random
import base64
import hashlib
import platform


def create_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + \
                                 string.digits) for x in range(length))


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def printcolor(string, color):
        print(color + string + bcolors.ENDC)

    @staticmethod
    def inputcolor(string, color = '\033[96m'):
        val = input(color + string + bcolors.ENDC)
        return val


class DiffgramInstallTool:

    def gen_install_finger_print(self):
        # Installation Fingeprint
        mac_addr = hex(uuid.getnode()).encode('utf-8')
        hash_object = hashlib.md5(mac_addr)
        fingerprint = hash_object.hexdigest()
        return fingerprint

    def get_system_os(self):
        os_name = os.name.lower()
        system = platform.system().lower()
        release = platform.release().lower()

        os_data = f"{os_name} {system} {release}"
        return os_data

    def populate_env(self):
        env_file = ''
        bcolors.printcolor('Generating Environment Variables file...', bcolors.OKBLUE)

        fernet_key = base64.urlsafe_b64encode(os.urandom(32))
        if isinstance(fernet_key, bytes):
            fernet_key = fernet_key.decode()


        # Local database
        env_file += "POSTGRES_IMAGE=postgres:12.5\n"
        env_file += "DATABASE_URL=postgresql+psycopg2://diffgram:diffgram@db:5432/diffgram\n"
        env_file += "DATABASE_HOST=db\n"
        env_file += "DATABASE_USER=diffgram\n"
        env_file += "DATABASE_PASS=diffgram\n"
        env_file += "DATABASE_NAME=diffgram\n"

        # minio provider
        env_file += "DIFFGRAM_MINIO_ENDPOINT_URL=http://host.docker.internal:9000\n"
        env_file += "DIFFGRAM_MINIO_ACCESS_KEY_ID=diffgram\n"
        env_file += "DIFFGRAM_MINIO_ACCESS_KEY_SECRET=diffgram\n"
        env_file += "SIGNED_URL_CACHE_MINIMUM_DAYS_VALID=5\n"
        env_file += "SIGNED_URL_CACHE_NEW_OFFSET_DAYS_VALID=7\n"
        env_file += "DIFFGRAM_S3_BUCKET_NAME=diffgram-storage\n"
        env_file += "DIFFGRAM_S3_BUCKET_REGION=us-east-1\n"
        env_file += "ML__DIFFGRAM_S3_BUCKET_NAME=diffgram-storage\n"
        env_file += "SAME_HOST=False\n"
        env_file += "DIFFGRAM_STATIC_STORAGE_PROVIDER=minio\n"
        env_file += "GCP_SERVICE_ACCOUNT_FILE_PATH=/dev/null\n"

        env_file += "DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE=True\n"

        env_file += f"FERNET_KEY={fernet_key}\n"
        env_file += f"USER_PASSWORDS_SECRET={create_random_string(10)}\n"
        env_file += f"INTER_SERVICE_SECRET={create_random_string(10)}\n"
        env_file += f"SECRET_KEY={create_random_string(18)}\n"

        install_fingerprint = self.gen_install_finger_print()
        env_file += f"DIFFGRAM_INSTALL_FINGERPRINT={install_fingerprint}\n"
        env_file += "DIFFGRAM_VERSION_TAG=latest\n"
        env_file += f"DIFFGRAM_HOST_OS={self.get_system_os()}\n"

        text_file = open(".env", "w")
        text_file.write(env_file)
        text_file.close()
        bcolors.printcolor(f"✓ Environment file written to: {os.path.abspath(text_file.name)}", bcolors.OKGREEN)


    def launch_dockers(self):
        try:
            print('Launching Diffgram...')
            os.system('docker-compose up -d')
            print('✓ Diffgram Successfully Launched!')
            print('View the Web UI at: http://localhost:8085')
        except Exception as e:
            print(f"Error Launching diffgram {str(e)}")

    def install(self):
        self.print_logo()
        print('')
        print('')
        bcolors.printcolor('Welcome To the Diffgram Installer.', bcolors.OKGREEN)
        print('')
        print('')

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
def main():
    pass


if __name__ == '__main__':
   main()