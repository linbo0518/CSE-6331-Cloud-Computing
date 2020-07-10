import os


class Config:
    host = "0.0.0.0"
    port = int(os.getenv('PORT', '3000'))
    allowed_csv_ext = {"txt", 'csv'}
    allowed_image_ext = {'txt', 'jpg', 'jpeg', 'png'}
    project_folder = os.path.abspath(os.path.dirname(__file__))
    upload_base_folder = os.path.join(project_folder, "assets")
    upload_csv_folder = os.path.join(upload_base_folder, "csv")
    upload_image_folder = os.path.join(upload_base_folder, "images")
    base_csv_path = os.path.join(upload_base_folder, "database.csv")
    csv_header = "Name,Grade,Room,State,Picture,Keywords"


opt = Config()
