import os, pathlib, logging, configparser

class Profile:
    parentFolder = pathlib.Path(__file__).parents[1]
    vpnConfigsFolder = parentFolder / 'vpn_configs'
    def __init__(self, name):
        self.name = name
        self.profileFolder = Profile.vpnConfigsFolder / name
        self.ini = self.profileFolder / f'{name}.ini'
        self.ovpn = self.profileFolder / f'{name}.ovpn'

    def exists(self):
        return any(self.name == c.name[:-4] for c in self.profileFolder.glob('*.ini'))


class Credentials:
    def __init__(self, profileName: str):
        self.profile = Profile(profileName)
        config = self.parseConfig(self.profile.ini)
        self.user = config.get('Credentials', 'USER')
        self.pswd = config.get('Credentials', 'PASS')
        self.secret = config['Credentials']['OTP_SECRET']

    def getExpectedEvents(self):
        return {'.*Auth User name:.*': self.user + '\n',
                '.*Auth Password:.*': self.pswd + self.getOtpCode(self.secret) + '\n'}

    @staticmethod
    def getOtpCode(secret_token) -> str:
        otpGetter = os.popen(f'oathtool -b --totp {secret_token}')
        otp = otpGetter.read()
        logging.info(f"OTP-code generated: {otp}")
        return otp

    @staticmethod
    def parseConfig(ini_filepath):
        # try:
        config = configparser.ConfigParser()
        config.read(ini_filepath)
        return config
        # except :
            # raise ArgumentError(f'Such configuration not found {ini}.ini')