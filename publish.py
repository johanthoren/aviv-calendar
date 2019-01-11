#!/usr/local/env python3
import re
import sys
import subprocess

REG = re.compile(r'\d+[.]\d+[.]\d+')

def main():
    text = read_file()
    current_version = find_version(text)
    print('Current version is: {}'.format(current_version))
    print('Please specify new version number:')
    new_version = input()

    while new_version == current_version:
        print('The new version number is the same as the old')
        print('Please try again')
        new_version = input()

    print('New version number is: {}, is this correct?'.format(new_version))
    confirm = query_yes_no('Is this correct?')

    if confirm is not True:
        print('Cancelled')
        sys.exit(2)
    elif confirm is True:
        print('Ok, moving on with version number {}'.format(new_version))

    new_text = replace_version(text, new_version)
    write_file(new_text)
    make_dists()

    source_name = 'dist/aviv-{}.tar.gz'.format(new_version)
    whl_name = 'dist/aviv-{}-py3-none-any.whl'.format(new_version)
    sign_dists(source_name, whl_name)

    source_sign = str(source_name + '.asc')
    whl_sign = str(whl_name + '.asc')
    upload_dists(source_name, source_sign, whl_name, whl_sign)

    print('All done!')

def read_file():
    s_file = open('setup.py', 'r')
    text = s_file.read()
    s_file.close()
    return text

def find_version(text):
    current_version = None
    mo = REG.search(text)
    current_version = mo.group()

    if current_version is None:
        raise Exception('No version number found!')
    return current_version

def replace_version(text, new_version):
    new_text = REG.sub(str(new_version), text)
    return new_text

def write_file(new_text):
    s_file = open('setup.py', 'w')
    s_file.write(new_text)
    s_file.close()

def make_dists():
    subprocess.run(["python", "setup.py", "sdist"])
    subprocess.run(["python", "setup.py", "bdist_wheel"])

def sign_dists(source_name, whl_name):
    subprocess.run(["gpg", "--detach-sign", "-a", source_name])
    subprocess.run(["gpg", "--detach-sign", "-a", whl_name])

def upload_dists(source_name, source_sign, whl_name, whl_sign):
    subprocess.run(["twine", "upload", source_name, source_sign])
    subprocess.run(["twine", "upload", whl_name, whl_sign])

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


if __name__ == '__main__':
    main()
