"""
This script contains:
    - a function to download data from the open dap-taltech s3 bucket.
    - a class to load data from the local data/ directory that is relevant
        across tutorials. 
"""
import os
import pandas as pd

from dap_taltech import (PROJECT_DIR, 
                         PUBLIC_DATA_FOLDER_NAME, 
                         BUCKET_NAME,
                         logger) 

LOCAL_DATA_DIR = os.path.join(PROJECT_DIR, PUBLIC_DATA_FOLDER_NAME)

def download_data():
    """Download datasets from the open dap-taltech s3 bucket."""

    os.system(f'aws s3 sync s3://{BUCKET_NAME}/data {LOCAL_DATA_DIR}')

class DataGetter(object):
    """Class to load datasets relevant across different tutorials for TalTech HackWeek 2023.

    Parameters
    ----------
    verbose : bool, optional
        Set the logger level. If verbose, set logger level to INFO. Else, set logger level to ERROR.
        Defaults to True.
    local : bool, optional
        If True, load data from local data directory. Else, download data from open dap-taltech s3 bucket.

    """
    def __init__(
        self,
        verbose=True,
        local = True
    ):
        self.verbose=verbose,
        self.local=local
        if self.verbose:
            logger.setLevel('INFO')
        else:
            logger.setLevel('ERROR')
        if self.local:
            logger.info(f'Loading data from {LOCAL_DATA_DIR}/')
            self.data_dir = LOCAL_DATA_DIR
            if not os.path.exists(self.data_dir):
                logger.warning(
                        "Neccessary data files are not downloaded. Downloading neccessary files..."
                    )
                download_data()
        else:
            self.data_dir = f"s3://{os.path.join(BUCKET_NAME, PUBLIC_DATA_FOLDER_NAME)}"
            logger.info(f"Loading data from open {BUCKET_NAME} s3 bucket.")
            
    
    def get_estonian_patents(self):
        """Get estonian patents data."""
        estonian_patents_path = os.path.join(self.data_dir, "patents_clean_EE.parquet")

        return pd.read_parquet(estonian_patents_path)