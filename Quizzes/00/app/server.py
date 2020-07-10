import os
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for
from utils import init_check, is_ext_valid, parse_csv, merge_df_to_base, save_df_to_file
from config import opt

app = Flask(__name__)


@app.route('/')
def home():
    return app.send_static_file("index.html")


@app.route("/database")
def show_database():
    return parse_csv(opt.base_csv_path)


@app.route("/edit_database")
def edit_database():
    return parse_csv(opt.base_csv_path, editable=True)


@app.route("/show_image", methods=["GET", "POST"])
def input_to_show():
    if request.method == "POST":
        print(12345)
        return redirect(url_for("show_image"))
    return app.send_static_file("show_image.html")


@app.route("/show_upload")
def show_upload():
    csv_file = os.listdir(opt.upload_csv_folder)
    image_file = os.listdir(opt.upload_image_folder)
    return render_template("show_upload.html",
                           csv_file=csv_file,
                           image_file=image_file)


@app.route("/show_image/<string:name>")
def show_image(name):
    database = pd.read_csv(opt.base_csv_path)
    name_list = database["room"].tolist()
    if name in name_list:
        image_filename = database[database["name"].str.contains(
            name, case=False)]["picture"].values[0]
        image_path = os.path.join(opt.upload_image_folder, image_filename)
        print(image_path)
        return render_template("show_image.html", image="file://" + image_path)
    else:
        return render_template("image_failed.html", name=name)


@app.route("/upload_csv", methods=["GET", "POST"])
def upload_csv():
    if request.method == "POST":
        if "file" not in request.files:
            return app.send_static_file('failed.html')
        file = request.files["file"]
        if file.filename == '':
            return app.send_static_file('failed.html')
        # opt: allowed_csv_ext
        if file and is_ext_valid(file.filename, opt.allowed_csv_ext):
            filename = os.path.join(opt.upload_csv_folder, file.filename)
            file.save(filename)
            database = pd.read_csv(opt.base_csv_path)
            new_df = pd.read_csv(filename, skipinitialspace=True)
            database = merge_df_to_base(database, new_df)
            save_df_to_file(database, opt.base_csv_path)
            return app.send_static_file("success.html")
        else:
            return app.send_static_file("failed.html")
    return app.send_static_file("upload.html")


@app.route("/upload_image", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        if "file" not in request.files:
            return app.send_static_file('failed.html')
        file = request.files["file"]
        if file.filename == '':
            return app.send_static_file('failed.html')
        # opt: allowed_image_ext
        if file and is_ext_valid(file.filename, opt.allowed_image_ext):
            filename = file.filename
            # opt: upload_image_folder
            file.save(os.path.join(opt.upload_image_folder, filename))
            return app.send_static_file("success.html")
        else:
            return app.send_static_file("failed.html")
    return app.send_static_file("upload.html")


if __name__ == "__main__":
    init_check()
    app.run(host=opt.host, port=opt.port, debug=True)
