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
        local=True
    ):
        self.verbose = verbose,
        self.local = local
        if self.verbose:
            logger.setLevel('INFO')
        else:
            logger.setLevel('ERROR')
        if self.local:
            self.data_dir = os.path.join(PROJECT_DIR, PUBLIC_DATA_FOLDER_NAME)
            logger.info(f'Loading data from {self.data_dir}/')
            if not os.path.exists(self.data_dir):
                logger.warning(
                    "Neccessary data files are not downloaded. Downloading neccessary files..."
                )
                os.system(f'aws s3 sync s3://{BUCKET_NAME}/data {self.data_dir}')
        else:
            self.data_dir = f"s3://{os.path.join(BUCKET_NAME, PUBLIC_DATA_FOLDER_NAME)}"
            logger.info(f"Loading data from open {BUCKET_NAME} s3 bucket.")

    def get_estonian_patents(self):
        """Get estonian patents data.

        This data was collected using Google Patents. A patent is considered Estonian
            if at least one inventor is Estonian. Patents were de-duplicated based on
            family ID.

        The data includes information such as:
            - patent_id: unique identifier for each patent
            - family_id: unique identifier for each patent family
            - title_localized: title of the patent
            - abstract_localized: abstract of the patent
        """
        estonian_patents_path = os.path.join(
            self.data_dir, "patents_clean_EE.parquet")

        return pd.read_parquet(estonian_patents_path)
