import json
from cryptography.fernet import Fernet


def load_key():
    with open('secret.key', 'rb') as key_file:
        return key_file.read()


def encrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()


key = load_key()

profiles = [
    # Your profile data here
]

for profile in profiles:
    profile['Phone Number'] = encrypt_data(profile['Phone Number'], key)
    profile['Card Number'] = encrypt_data(profile['Card Number'], key)
    profile['Expiration Date'] = encrypt_data(profile['Expiration Date'], key)
    profile['CVV'] = encrypt_data(profile['CVV'], key)

with open('user_profiles.json', 'w') as file:
    json.dump(profiles, file, indent=4)
