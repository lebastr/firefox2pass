from subprocess import *
import pandas as pd
import os
import re
import argparse

def check_mail(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return re.fullmatch(regex, email)

def read_gpg_id(dir):
    with open(os.path.join(dir, '.gpg-id'), 'r') as h:
        s = h.readline().strip() 

    if not check_mail(s):
        raise ValueError("It seems that I didn't read .gpg-id properly")

    return s
        
def import_logins(password_store_dir, logins_csv):
    df = pd.read_csv(logins_csv)
    gpg_id = read_gpg_id(password_store_dir)
    print(f"gpg-id: {gpg_id}")
    
    for _, row in df.iterrows():
        print(f"import logins from {row.url}")
        insert_row(password_store_dir, gpg_id, row)

def insert_row(password_store_dir, gpg_id, row):
    path = os.path.join(password_store_dir, *split_url(row.url))
    os.makedirs(path, exist_ok=True)

    fname = (row.username
             if not pd.isna(row.username) else "password") + ".gpg"

    enc = gpg_encrypt(row.password, gpg_id)
    with open(os.path.join(path, fname), 'wb') as h:
        h.write(enc)
        
def split_url(url):
    return list(filter(lambda p: len(p) > 0, url.split('/')))
    
def gpg_encrypt(inp, key_id):
    p = Popen(["gpg", "--encrypt", "--recipient", key_id], stdin=PIPE, stdout=PIPE)
    out, _ = p.communicate(str.encode(inp))
    return out


parser = argparse.ArgumentParser(description='Imports firefox logins into password-store')
parser.add_argument('password_store_path', type=str)
parser.add_argument('logins_csv_file_path', type=str)
args = parser.parse_args()

print(f"use password-store: {args.password_store_path}")
print(f"use firefox-csv-file: {args.logins_csv_file_path}")

import_logins(args.password_store_path, args.logins_csv_file_path)

