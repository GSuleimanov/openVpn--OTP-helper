import configparser, logging, os


def parse_config(ini):
    config = configparser.ConfigParser()
    config.read(ini)
    return config


def get_otp_code(secret_token):
    otp_getter = os.popen(f'oathtool -b --totp {secret_token}')
    otp = otp_getter.read()
    logging.info(f"OTP-code generated: {otp}")
    return otp
