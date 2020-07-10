import os
import pandas as pd
from flask import Flask, request
from config import opt


def init_check():
    if not os.path.exists(opt.upload_base_folder):
        os.mkdir(opt.upload_base_folder)
    if not os.path.exists(opt.upload_csv_folder):
        os.mkdir(opt.upload_csv_folder)
    if not os.path.exists(opt.upload_image_folder):
        os.mkdir(opt.upload_image_folder)
    if not os.path.exists(opt.base_csv_path):
        with open(opt.base_csv_path, 'w') as f:
            f.write(opt.csv_header)


def is_ext_valid(filename, allowed_ext=None):
    if allowed_ext is None:
        return True
    _, ext = os.path.splitext(filename)
    return ext[1:] in allowed_ext


def refine_name_and_dtype(df):
    return df.rename(columns=opt.columns_map).astype(opt.dtype_map)


def merge_df_to_base(base_df, new_df):
    # new_df = refine_name_and_dtype(new_df)
    return base_df.append(new_df).drop_duplicates().reset_index(drop=True)


def save_df_to_file(df, filename):
    df.to_csv(filename, index=False)


def parse_csv(csv_file, editable=False):
    df = pd.read_csv(csv_file)
    html = df.to_html(na_rep="NULL")
    html += '<br />\n<a href=" / "> Back to Home </a>'
    if editable:
        html = html.replace("<td>", "<td contenteditable=true>")
        html += '<br/ >\n<a href=" /save_database "> Submit </a></body>'
    return html
