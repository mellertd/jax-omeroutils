"""
NOTE: This needs to be run as the service account that runs the OMERO server.
This should be separate from the service account that owns the image data, for
safety.
"""
import argparse
import json
from jax_omeroutils.config import OMERO_USER, OMERO_PASS
from jax_omeroutils.config import OMERO_HOST, OMERO_PORT
from jax_omeroutils.importer import Importer
from omero.gateway import BlitzGateway
from pathlib import Path


def main(import_md):

    # Load metadata to orchestrate import
    with open(import_md, 'r') as fp:
        batch_md = json.load(fp)

    import_user = batch_md['user']
    import_group = batch_md['group']
    file_metadata = batch_md['import_targets']
    data_dir = Path(batch_md['server_path'])

    # Create user connection
    suconn = BlitzGateway(OMERO_USER,
                          OMERO_PASS,
                          host=OMERO_HOST,
                          port=OMERO_PORT,
                          secure=True)
    suconn.connect()
    conn = suconn.suConn(import_user, import_group, 2160000000)
    suconn.close()

    # Import targets from import.json
    for md in file_metadata:
        filename = md['filename']
        file_path = data_dir / filename
        print(f'Preparing to import {str(file_path)}')
        imp_ctl = Importer(conn, file_path, md)
        imp_ctl.import_ln_s(OMERO_HOST, OMERO_PORT)
        print("import done")
        if imp_ctl.screen:
            print("it's a screen")
            imp_ctl.get_plate_ids()
            print(f"plate ids get! {str(imp_ctl.plate_ids[0])}")
            imp_ctl.organize_plates()
            print("plate organized")
            imp_ctl.annotate_plates()
            print("plate annotated")
        else:
            imp_ctl.get_image_ids()
            imp_ctl.organize_images()
            imp_ctl.annotate_images()

    conn.close()
    return


if __name__ == "__main__":
    description = 'Use import.json to orchestrate OMERO import'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('import_json',
                        type=str,
                        help='Full path to import.json')
    args = parser.parse_args()

    main(Path(args.import_json))
