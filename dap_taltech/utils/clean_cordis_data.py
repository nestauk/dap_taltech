"""
This script cleans up the Horizon 2020 CORDIS data
for use in the Data Getters class.

It primarily:
    - loads files to s3 that don't need specific encoding or separator types;
    - merges project deliverables files;
    - renames project .csv file names

python dap_taltech/utils/cordis_data.py
"""
import pandas as pd
import os

from dap_taltech import BUCKET_NAME, logger

cordis_filepath = f"s3://{BUCKET_NAME}/data/cordis_horizon/"
deliverables_dirname = "h2020_project_deliverables"
project_dirname = "h2020_projects"

project_dirname_mapper = {
    'euroSciVoc': 'euro_sci_voc',
    'legalBasis': 'legal_basis',
    'organization': 'organisation',
    'project': 'project',
    'topics': 'topics',
    'webItem': 'web_item',
    'webLink': 'web_link',
}

if __name__ == '__main__':

    logger.info(
        'Loading project publications and saving without encoding/separator issues...')
    project_publications = pd.read_csv(
        os.path.join(
            cordis_filepath,
            'h2020_projectPublications.csv'),
        sep=';',
        encoding='latin-1')
    project_publications.to_csv(
        os.path.join(
            cordis_filepath,
            'project_publications_clean.csv'),
        index=False)
    
    logger.info(
        "Loading report summaries and saving without encoding/separator issues...")
    report_summaries = pd.read_csv(
        os.path.join(
            cordis_filepath,
            'report_summaries.csv'),
        sep=';',
        encoding='latin-1')
    report_summaries.to_csv(
        os.path.join(
            cordis_filepath,
            'report_summaries_clean.csv'),
        index=False)
    
    logger.info('Loading and merging project deliverables...')
    initial_project_deliverables = pd.read_csv(
        os.path.join(
            cordis_filepath,
            deliverables_dirname,
            'projectDeliverables.csv'),
        sep=';',
        encoding='latin-1')
    all_project_deliverables_dfs = []
    for i in range(2, 5):
        deliverables_filename = os.path.join(
            cordis_filepath,
            deliverables_dirname,
            f'projectDeliverables_{str(i)}.csv')
        project_deliverables_df = pd.read_csv(
            deliverables_filename, sep=';', encoding='latin-1')
        all_project_deliverables_dfs.append(project_deliverables_df)
    project_deliverables = pd.concat(all_project_deliverables_dfs)
    all_project_deliverables = pd.concat(
        [initial_project_deliverables, project_deliverables])
    logger.info("saving project deliverables to s3...")
    all_project_deliverables.to_csv(
        os.path.join(
            cordis_filepath,
            "project_deliverables_clean.csv"),
        index=False)

    logger.info(
        "Loading project metadata + rename + saving without encoding/separator issues...")
    project_filenames = list(project_dirname_mapper.keys())
    for file in project_filenames:
        file_path = os.path.join(
            cordis_filepath,
            project_dirname,
            f"{file}.csv")
        file_df = pd.read_csv(file_path, sep=';', encoding='latin-1')
        file_df.to_csv(
            os.path.join(
                cordis_filepath,
                'projects',
                f"{project_dirname_mapper.get(file)}_clean.csv"),
            index=False)
