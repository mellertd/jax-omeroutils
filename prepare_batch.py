"""
NOTE: This needs to be run as the service account that owns the directory
in which the image data will reside on the server. This should be separate
from the service account that runs OMERO, for safety.
"""

import argparse
from datetime import datetime
from jax_omeroutils.intake import ImportBatch
from jax_omeroutils.config import OMERO_USER, OMERO_PASS
from jax_omeroutils.config import OMERO_HOST, OMERO_PORT
from omero.gateway import BlitzGateway
from pathlib import Path


def main(import_batch_directory, log_directory, timestamp):

    # Validate import and write import.json
    conn = BlitzGateway(OMERO_USER,
                        OMERO_PASS,
                        host=OMERO_HOST,
                        port=OMERO_PORT)
    conn.connect()
    batch = ImportBatch(conn, import_batch_directory)
    batch.set_logging(log_directory, timestamp)
    batch.load_md()
    if not batch.md:
        raise ValueError('No metadata file found.')
    batch.validate_import_md()
    if not batch.valid_md:
        raise ValueError('Metadata file has fatal errors.')
    batch.validate_user_group()
    batch.set_server_path()
    batch.load_targets()
    batch.write_json()
    conn.close()


if __name__ == "__main__":
    description = 'Prepare a batch for OMERO import'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('import_batch_directory',
                        type=str,
                        help='Full path of directory containing images to'
                             ' import and single metadata file')
    parser.add_argument('log_directory',
                        type=str,
                        help='Directory for the log files')
    parser.add_argument('--timestamp',
                        type=str,
                        required=False,
                        default=datetime.now().strftime('%Y%m%d_%H%M%S'),
                        help='Timestamp for the log files')
    args = parser.parse_args()

    main(Path(args.import_batch_directory), Path(args.log_directory),
         args.timestamp)
