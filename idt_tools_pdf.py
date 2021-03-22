import os
from os.path import isfile, join

import PyPDF2
import chardet
from fpdf import FPDF


def get_file_encoding(logfile):
    rawdata = open(logfile, "rb").read()
    result = chardet.detect(rawdata)
    charenc = result['encoding']
    encoding = "utf-8"
    if charenc == "UTF-16":
        encoding = "utf-16"
    return encoding


def separate_show_command_to_files_sequentially(log_folder, log_file_name, out_txt_folder):
    # TODO 先將不同的show command 分開為不同的檔案
    print(log_folder, log_file_name, out_txt_folder)
    if not os.path.exists(out_txt_folder):
        os.makedirs(out_txt_folder)
    hash_show = "show"
    hash = "#"
    full_file_name = os.path.join(log_folder, log_file_name)
    log_file = open(full_file_name, "r", encoding=get_file_encoding(full_file_name))
    lines = log_file.readlines()
    data_file_name = ""
    individual_show_file = None
    file_count = 0
    for line in lines:
        show_index = line.find(hash_show)
        hash_index = line.find(hash)
        if -1 < hash_index < show_index:
            # TODO open a new file
            command = ' '.join(line[show_index:].strip().split()).lower()
            if data_file_name != "":
                individual_show_file.close()
            file_count += 1
            data_file_name = "show_{:02d}.txt".format(file_count)
            full_file_name = os.path.join(out_txt_folder, data_file_name)
            individual_show_file = open(full_file_name, "w", encoding="utf-8")
            individual_show_file.write(line)
        else:
            if data_file_name != "":
                individual_show_file.write(line)

    if data_file_name != "":
        individual_show_file.close()

def txt_file_to_pdf(orient, infile, outfile):
    if orient == "land":
        pdf = FPDF('L', 'in', 'Letter')
        font_height = 0.12
    else:
        pdf = FPDF('P', 'in', 'Letter')
        font_height = 0.16

    pdf.add_page()
    pdf.set_margins(0.25, 0.25)
    pdf.set_auto_page_break(True, margin=0.25)
    if orient == 'land':
        pdf.set_font('Courier','', 8)
    else:
        pdf.set_font('Courier', '', 10)
    pdf.set_xy(0.25, 0.25)

    f = open(infile)
    for line in f:
        pdf.write(font_height, line)
    f.close()
    pdf.output(outfile, 'F')


def txt_file_to_command_first_page_pdf(in_dir, in_txt_file, out_txt_dir="", out_pdf_file=""):
    # orient = "land"
    orient = "port"
    if out_pdf_file == "":
        out_pdf_file = in_txt_file[:-4] + ".pdf"
    try:
        if out_txt_dir == "":
            out_txt_dir = os.path.join(in_dir, in_txt_file[:-4])
        separate_show_command_to_files_sequentially(in_dir, in_txt_file, out_txt_dir)
        txt_files = [f for f in os.listdir(out_txt_dir)
                     if f[-3:] == "txt" and isfile(join(out_txt_dir, f))]

        pdf_streams = []
        for txt_file in txt_files:
            infile = os.path.join(out_txt_dir, txt_file)
            out_pdf = os.path.join(out_txt_dir, txt_file[:-4] + ".pdf")
            txt_file_to_pdf(orient, infile, out_pdf)
            pdf_streams.append(open(out_pdf, 'rb'))

        writer = PyPDF2.PdfFileWriter()
        for reader in map(PyPDF2.PdfFileReader, pdf_streams):
            writer.addPage(reader.getPage(0))

        pdfOutputFile = open(os.path.join(in_dir, out_pdf_file), 'wb')
        writer.write(pdfOutputFile)
        pdfOutputFile.close()
    finally:
        for f in pdf_streams:
            f.close()
