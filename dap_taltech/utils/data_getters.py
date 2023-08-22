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
from typing import Sequence, Any, Literal
from PIL import Image
import numpy as np
import pandas as pd

import boto3
from io import BytesIO

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
        local=True,
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
            files = os.listdir(self.data_dir)
            if len(files) == 0:
                logger.warning(
                    "Neccessary data files are not downloaded. Downloading neccessary files..."
                )
                os.system(f'aws --no-sign-request --region=eu-west-1 s3 cp s3://{BUCKET_NAME}/data {self.data_dir} --recursive')
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
        return pd.read_parquet(file_path)

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
    
    def get_oa_articles(self, institution: str = "TT") -> pd.DataFrame:
        """Get research articles data.

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

        Args:
            institution (str, optional): Institution to filter articles by. Must be either TT, TT_p, or EE.
        
        Returns:
            pd.DataFrame: A pandas dataframe containing TalTech articles data.
        """
        assert institution in ["TT", "TT_p", "EE"], logger.error("Institution must be either TT (TalTech), TT_p (preprocessed TT) or EE (Estonia).")
        prefix = "articles_clean" if institution != "TT_p" else "articles_preprocessed"
        return self._fetch_data(f"{prefix}_{institution[:2]}.parquet")

    def get_surnames(self) -> pd.DataFrame:
        """Get surnames data.

        This data was collected using the Estonian Population Register, and 
        popular German and Ukrainian surnames from the website Forebears.

        The data includes information such as:
            - surname: surname of the person
            - origin: origin of the surname

        Returns:
            pd.DataFrame: A pandas dataframe containing surnames data.
        """
        return self._fetch_data("surnames.parquet")
    
    def get_bike_demand(self) -> pd.DataFrame:
        """Get bike demand data.

        This data was collected from the Kaggle competition Bike Sharing Demand.

        The data includes information such as:
            - dteday: date and time of the observation
            - season: season of the year
            - yr: year
            - mnth: month
            - hr: hour
            - holiday: whether the day is a holiday or not
            - workingday: whether the day is a working day or not
            - weekday: day of the week
            - weather: weather code
            - temp: temperature in Celsius
            - atemp: "feels like" temperature in Celsius
            - hum: relative humidity
            - windspeed: wind speed
            - casual: number of casual users
            - registered: number of registered users
            - cnt: total number of users

        Returns:
            pd.DataFrame: A pandas dataframe containing bike demand data.
        """
        return self._fetch_data("bike_riding_demand.parquet")
    
    def get_image_labels(self) -> pd.DataFrame:
        """Get estonian images data.

        This data was collected from the website Unsplash.

        The data includes information such as:
            - image_id: unique identifier for each image
            - label: label of the image

        Returns:
            pd.DataFrame: A pandas dataframe containing estonian images data.
        """
        return self._fetch_data("images/image_labels.parquet")
    
    def get_images(self) -> Sequence[Any]:
        """Get estonian images data.

        Returns:
            Sequence[Any]: A list of PIL images.
            Sequence[any]: The 224 x 224 x 3 images.
        """
        if self.local:        
            file_path = os.path.join(self.data_dir, "images")
            
            image_list = []
            for file in os.listdir(file_path):

                try:
                    image = Image.open(os.path.join(file_path, file))
                    image_list.append(tuple([file, image]))

                except:
                    pass
        else:
            s3 = boto3.client('s3')
            objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="data/images")
            image_list = []
            for obj in objects.get('Contents', []):
                response = s3.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])
                try:        
                    image = Image.open(BytesIO(response['Body'].read()))
                    image_list.append(tuple([obj['Key'], image]))
                except:
                    pass
        
        image_list = sorted(image_list, key=lambda x: int(x[0].split('_')[-1].split('.')[0]))
        
        return image_list

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
    
    def get_esco_skills_taxonomy(self) -> pd.DataFrame:
        """Get the European Commision's skills taxonomy in English.
        
        This is a curated dataset based on data from the 
            following source: https://esco.ec.europa.eu/en/use-esco/download 
            
        The dataset includes information such as:
            - the skill label;
            - the unique skill identifier; 
            - skill taxonomy label 

        Returns:
            pd.DataFrame: A pandas dataframe containing the European Commision's 
            skills taxonomy.
        """
        return self._fetch_data("esco_data_formatted.csv")

    def get_horizon2020_iprs(self) -> pd.DataFrame:
        """
        Intellectual Property Rights Data from CORDIS - EU
            research projects under Horizon 2020 (2014-2020).

        The dataset is about projects and their results funded by
        the European Union under the Horizon 2020 framework programme
        for research and innovation from 2014 to 2020. This dataset is from
        the following source:
            https://data.europa.eu/data/datasets/cordish2020projects?locale=en

        This data includes information such as:
            - title: the title of the project;
            - applicantName: the name of the applicant;
            - applicantDate: the date of the application;
            - patentType: the type of patent.

        There are ID columns in this dataset to link to other horizon2020 datasets:
             get_horizon2020_iprs, get_horizon2020_project_publications,
             get_horizon2020_project_deliverables, get_horizon2020_projects

        Returns:
            pd.DataFrame: A pandas dataframe containing Intellectual Property Rights Data
                from CORDIS - EU research projects under Horizon 2020 (2014-2020)
        """
        return self._fetch_data("cordis_horizon/h2020_project_iprs.csv")

    def get_horizon2020_project_publications(self) -> pd.DataFrame:
        """Project publications meta-data and links to publications
            included since May 2019 from CORDIS Data - EU research
            projects under Horizon 2020 (2014-2020).

        The dataset is about projects and their results funded by
        the European Union under the Horizon 2020 framework programme
        for research and innovation from 2014 to 2020. This dataset is from
        the following source:
            https://data.europa.eu/data/datasets/cordish2020projects?locale=en

        This data includes information such as:
            - title: the title of the project;
            - projectAcronym: the acronym of the project;
            - legalBasis: the legal basis of the project;
            - ibsn: the ibsn of the project;
            - isPublishedAs: Category of how the project is published.

        There are ID columns in this dataset to link to other horizon2020 datasets:
             get_horizon2020_iprs, get_horizon2020_project_publications,
             get_horizon2020_project_deliverables, get_horizon2020_projects

        Returns:
            pd.DataFrame: A pandas dataframe containing project publications meta-data and
                links to publications included since May 2019.
        """
        return self._fetch_data(
            "cordis_horizon/project_publications_clean.csv")

    def get_horizon2020_project_deliverables(self) -> pd.DataFrame:
        """Project deliverables meta-data and links to deliverables
        included since May 2019 from CORDIS Data - EU research projects
        under Horizon 2020 (2014-2020).

        The dataset is about projects and their results funded by
        the European Union under the Horizon 2020 framework programme
        for research and innovation from 2014 to 2020. This dataset is from
        the following source:
            https://data.europa.eu/data/datasets/cordish2020projects?locale=en

        This data includes information such as:
            - title: the title of the project;
            - deliverableType: the type of deliverable;
            - description: the description of the deliverable;
            - projectID: the ID of the project.
            - projectAcronym: the acronym of the project.

        There are ID columns in this dataset to link to other horizon2020 datasets:
             get_horizon2020_iprs, get_horizon2020_project_publications,
             get_horizon2020_project_deliverables, get_horizon2020_projects

        Returns:
            pd.DataFrame: A pandas dataframe containing project deliverables meta-data and
                links to deliverables included since May 2019.
        """
        return self._fetch_data(
            "cordis_horizon/project_deliverables_clean.csv")

    def get_horizon2020_projects(self,
                                 df_name: Literal['euro_sci_voc',
                                                  'legal_basis',
                                                  'organisation',
                                                  'project',
                                                  'topics',
                                                  'web_item',
                                                  'web_link'] = 'project') -> pd.DataFrame:
        """Project data from CORDIS - EU research projects under Horizon 2020 (2014-2020).

        This includes datasets on:
            - euro_sci_voc: classification with the European Science 
            Vocabulary (EuroSciVoc) ('projectID' in dataset);
            - legal_basis: legal basis information ('projectID' in dataset);
            - organisation: participating organisations ('projectID' in dataset);
            - project: project information ('id' in dataset);
            - topics: topic information ('projectID' in dataset);
            - web_item: image and project URLs (NO 'projectID' in dataset);
            - web_link: project URLs ('projectID' in dataset).

        The dataset is about projects and their results funded by
        the European Union under the Horizon 2020 framework programme
        for research and innovation from 2014 to 2020. This dataset is from
        the following source:
            https://data.europa.eu/data/datasets/cordish2020projects?locale=en

        There are ID columns in these datasets that can be used to
        linked to other horizon2020 datasets. Relevant joining keys include: 
        'projectID', 'id', organisationID.

        Args:
            df_name (str): the name of the dataset to be returned. It must be one of the following:
            ['euro_sci_voc', 'legal_basis', 'organisation', 'project', 'topics', 'web_item', 'web_link']. Defaults to 'project'.

        Returns:
            pd.DataFrame: A pandas dataframe containing project data from CORDIS - EU research.
        """
        horizon_2020_project_dfs = ['euro_sci_voc',
                                                  'legal_basis',
                                                  'organisation',
                                                  'project',
                                                  'topics',
                                                  'web_item',
                                                  'web_link']

        assert df_name in horizon_2020_project_dfs, logger.error(f"Project dataset name must be one of {horizon_2020_project_dfs}")
        return self._fetch_data(
            f"cordis_horizon/projects/{df_name}_clean.csv")

    def get_horizon2020_report_summaries(self) -> pd.DataFrame:
        """Periodic or final publishable summaries included since September 2018
        from CORDIS Data - EU research projects under Horizon 2020 (2014-2020).

        The dataset is about projects and their results funded by
        the European Union under the Horizon 2020 framework programme
        for research and innovation from 2014 to 2020. This dataset is from
        the following source:
            https://data.europa.eu/data/datasets/cordish2020projects?locale=en

        This data includes information such as:
            - projectID: the ID of the project;
            - title: the title of the project;
            - attachment: path to the attachment;

        There are ID columns in this dataset to link to other horizon2020 datasets:
             get_horizon2020_iprs, get_horizon2020_project_publications,
             get_horizon2020_project_deliverables, get_horizon2020_projects

        Returns:
            pd.DataFrame: A pandas dataframe containing report summaries since
                September 2018.
        """
        return self._fetch_data("cordis_horizon/report_summaries_clean.csv")
