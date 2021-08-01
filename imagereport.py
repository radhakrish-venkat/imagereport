#
# Copyright (c) Radhakrishnan Venkataramanan All rights reserved.
#
#
# The Licensed Software and Documentation are deemed to be commercial computer
# software as defined in FAR 12.212 and subject to restricted rights as defined
# in FAR Section 52.227-19 "Commercial Computer Software - Restricted Rights"
# and DFARS 227.7202, Rights in "Commercial Computer Software or Commercial
# Computer Software Documentation," as applicable, and any successor regulations,
# whether delivered on premises or hosted services.  Any use,
# modification, reproduction release, performance, display or disclosure of
# the Licensed Software and Documentation by the U.S. Government shall be
# solely in accordance with the terms of this Agreement.
#


import os
import logging
import time
import argparse
import xlsxwriter
import csv


def file_logging(log_file_name):
    global logger
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s', '%d-%m-%Y %H:%M:%S')
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def convert_epoch_date(epoch_date):
    'convert Epoch date to sql GMT  format'
    date_time = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(int(epoch_date)))
    return date_time


def get_image_info_from_file(bpimage_file, output_bpimage_file):
    'Read bpimagelist file list and get the image primary copy and tape media id'
    if os.path.exists(output_bpimage_file):
        os.remove(output_bpimage_file)
    # logger.info("Scanning Backup Images")
    with xlsxwriter.Workbook(output_bpimage_file) as xlsworkbook, open(bpimage_file, 'r') as bpimagefile:
        # with open(bpimage_file, 'r') as bpimagefile, open(output_bpimage_file, 'w') as workbook:
        # writer = csv.writer(workbook, delimiter=',', lineterminator='\n')
        # row_header = ('backupid','policyname','clientname','backuptime','expirytime','sizeinkb', 'numberofcopies','primarycopy')
        # writer.writerow(row_header)
        worksheet1 = xlsworkbook.add_worksheet('Image Information')
        header_fmt = xlsworkbook.add_format(
            {'font_name': 'courier new', 'font_size': '13', 'font_color': 'black', 'bold': 'true'})
        row_format = xlsworkbook.add_format({'font_name': 'courier new', 'font_size': '12', 'font_color': 'black'})
        header_row = (
            'Backup ID', 'Policy Name', 'Client Name', 'Backup Time', 'Expiry Time', 'Size in KB', 'Number of Copies',
            'Primary Copy', 'Image in DD', 'Image in Tape', 'Media ID')
        worksheet1.write_row(0, 0, header_row, header_fmt)
        row_number = 1

        for read_lines in bpimagefile:
            read_lines = read_lines.rstrip(os.linesep)
            split_lines = read_lines.split()

            if split_lines[0] == 'IMAGE':
                on_disk = False
                on_tape = False
                backup_id = split_lines[5]
                policy_name = split_lines[6]
                client_name = split_lines[1]
                backup_time = split_lines[13]
                expiration = split_lines[15]
                size_in_kb = split_lines[18]
                number_of_copies = split_lines[20]
                primary_copy = split_lines[27]
            elif split_lines[0] == 'FRAG':
                media_type = split_lines[5]
                media_id = split_lines[8]
                if media_type == "2":
                    on_tape = True
                if media_type == "0":
                    on_disk = True

                row_data = (
                    backup_id, policy_name, client_name, convert_epoch_date(backup_time),
                    convert_epoch_date(expiration),
                    size_in_kb, number_of_copies, primary_copy, on_disk, on_tape, media_id)
                worksheet1.write_row(row_number, 0, row_data, row_format)
                row_number += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Report utility to update Solaris backup size for Vmware')
    parser.add_argument('--bpimagelist_file', help="Provide bpimagelist file name", required=True)
    parser.add_argument('--create_report', help='Create Excel report', dest='action', action='store_const',
                        const='create_report')
    parsed_args = parser.parse_args()
    if parsed_args.action == None:
        parser.parse_args(['-h'])

    if parsed_args.action == 'create_report':
        input_file = parsed_args.bpimagelist_file
        output_base = os.path.splitext(input_file)[0]
        output_file = os.path.join(output_base+"."+"xlsx")
        get_image_info_from_file(bpimage_file=input_file,output_bpimage_file=output_file)
