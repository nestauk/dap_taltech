"""
This script contains:
    A class to load data from either a local directory or s3 data that is relevant
        across tutorials.
    The methods in the class have detailed docstrings that act as a pseudo data 
        dictionary to describe the data.

To use the class:
    
    from dap_taltech.utils.data_getters import DataGetter

    dg = DataGetter(local=True)
    estonian_patents = dg.get_estonian_patents()

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
        self.verbose = verbose
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

    def _fetch_data(self, file_name: str) -> pd.DataFrame:
        """Fetch data from local directory or s3 bucket.

        Args:
            file_name (str): Name of the file to fetch.

        Returns:
            pd.DataFrame: A pandas dataframe containing the data.
        """        
        file_path = os.path.join(self.data_dir, file_name)
        if file_name.endswith('.parquet'):
            return pd.read_parquet(file_path)
        elif file_name.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            logger.error(f"File type {file_name.split('.')[-1]} is not supported.")

    def get_estonian_patents(self) -> pd.DataFrame:
        """Get estonian patents data.

        This data was collected using Google Patents. A patent is considered Estonian
            if at least one inventor is Estonian. Patents were de-duplicated based on
            family ID.

        The data includes information such as:
            - patent_id: unique identifier for each patent
            - family_id: unique identifier for each patent family
            - title_localized: title of the patent
            - abstract_localized: abstract of the patent
        
        Returns:
            pd.DataFrame: A pandas dataframe containing estonian patents data.
        """
        return self._fetch_data("patents_clean_EE.parquet")
    
    def get_taltech_articles(self) -> pd.DataFrame:
        """Get TalTech research articles data.

        This data was collected using OpenAlex.

        The data includes information such as:
            - id: unique identifier for each article
            - display_name: title of the article
            - publication_date: date of publication
            - primary_location: dictionary containing information about the location of the article
            - authors: list of dictionaries containing information about the authors of the article
            - cited_by_count: number of times the article has been cited
            - counts_by_year: dictionary containing the number of times the article has been cited by year
            - concepts: list of dictionaries containing information about the key concepts in the article
            - abstract: abstract of the article
        
        Returns:
            pd.DataFrame: A pandas dataframe containing TalTech articles data.
        """
        return self._fetch_data("articles_clean_TT.parquet")
    
    def get_armenian_job_adverts(self) -> pd.DataFrame:
        """Get Armenian job adverts data posted from 2004 to 2015.
        
        This data was sourced from the following website: https://www.kaggle.com/datasets/madhab/jobposts
        
        The data includes information such as:
            - jobpost: the original job post
            - Title: the title of the job
            - Company: the company that posted the job
            - AnnouncementCode: the announcement code of the job
            - Term: the term of the job
            - Eligibility: the eligibility of the job
            - Audience: the audience of the job
            - StartDate: the start date of the job
            - Location: the location of the job

        Returns:
            pd.DataFrame: A pandas dataframe containing Armenian job adverts data.
        """
        return self._fetch_data("job_postings.csv")
