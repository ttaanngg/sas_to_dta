#! /usr/local/bin/python

# coding=utf-8
from __future__ import print_function
import os

import argparse
import pandas
import sys
import sas7bdat


parser = argparse.ArgumentParser()
parser.add_argument("target_path", help="target path to transform, file or directory.")
parser.add_argument("-x", "--extract_archive", help="determine to extract archive, only support zip.",action="store_true")
parser.parse_args()


def convert_sas_to_dta(file_path):
    with sas7bdat.SAS7BDAT(os.path.abspath(file_path)) as f:
        print("processing file {}.".format(f.path))
        df = f.to_data_frame()
        try:
            df.to_stata(file_path.replace(".sas7bdat", ".dta"))
        except ValueError as e:
            print("file transform failed, detail: {}.".format(e.message))


def recursive_convert_sas_to_dta(target_path):
    print("scaning directory {}.".format(target_path))
    for dir_name, subdir_list, file_list in os.walk(target_path):
        for subdir in subdir_list:
            recursive_convert_sas_to_dta(subdir)

        for file_name in file_list:
            if file_name.endswith(".sas7bdat") and target_path.replace(".sas7bdat", ".dta") not in file_list:
                convert_sas_to_dta(os.path.abspath(os.path.join(dir_name, file_name)))
            elif file_name.endswith(".zip") and parser.extract_archive:
                print("extracting zip {}".format(file_name))
                os.system("unzip -o {} -d {}".format(file_name, file_name.replace(".zip", "")))
                recursive_convert_sas_to_dta(file_name.replace(".zip", ""))


if __name__ == '__main__':

    target_path = str(parser.target)

    if os.path.isfile(target_path):
        if target_path.endswith(".sas7bdat"):
            convert_sas_to_dta(target_path)
    elif os.path.isdir(target_path):
        recursive_convert_sas_to_dta(target_path)
    else:
        print("unknown file type.")

    print("finish transforming.")
