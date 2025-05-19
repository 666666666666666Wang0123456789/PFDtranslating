import os

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze


local_image_dir, local_md_dir = "/home/left/Downloads/output/images", "/home/left/Downloads/output"
image_dir = "/home/left/Downloads/output/images"

os.makedirs(local_image_dir, exist_ok=True)

image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)

def pdf_to_md(pdf_file_name):
    name_without_suff = pdf_file_name.split(".")[0]
    reader1 = FileBasedDataReader("")
    pdf_bytes = reader1.read(pdf_file_name)

    ds = PymuDocDataset(pdf_bytes)

    output_path = f"{name_without_suff}.md"

    ds.apply(doc_analyze, ocr=False).pipe_txt_mode(image_writer).dump_md(
        md_writer, output_path, image_dir
    )

    return output_path