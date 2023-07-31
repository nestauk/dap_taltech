import requests, boto3, argparse, logging
from toolz import pipe
from typing import Dict, Sequence
import pandas as pd

# OpenAlex API corresponding to TalTech
cursor_url = "https://api.openalex.org/institutions?filter=country_code:EE&cursor={}&select=id,country_code&mailto=david.ampudia@nesta.org.uk"

logging.basicConfig(level=logging.INFO)

def institutions_generator() -> list:
    """Creates a generator that yields a list of institutions from the OpenAlex API.
    It uses cursor pagination to get all the institutions.

    Returns:
        list: A list of institutions from the OpenAlex API.

    Yields:
        Iterator[list]: A generator that yields a list of institutions from the OpenAlex API.
    """    
    cursor = "*"
    while cursor:
        r = requests.get(cursor_url.format(cursor))
        data = r.json()
        results = data.get("results")
        cursor = data["meta"].get("next_cursor", False)
        yield results

def get_all_institutions() -> pd.DataFrame:
    """Gets all the institutions from the OpenAlex API.

    Returns:
        pd.DataFrame: A DataFrame containing all the institutions from the OpenAlex API.
    """    
    oa_institutions = []    
    generator = institutions_generator()

    for institutions in generator:
        logging.info(f"Got {len(institutions)} institutions from the OpenAlex API.")
        if not institutions:
            continue
        df = pd.DataFrame(institutions)
        oa_institutions.append(df)

    if not oa_institutions:
        return pd.DataFrame()  # return an empty DataFrame if oa_institutions is empty
    else:
        return pd.concat(oa_institutions)

def save_to_s3(
        df: pd.DataFrame, 
        bucket: str = "dap-taltech", 
        key: str = "data/institutions_clean_EE.parquet"
    ) -> None:
    """Saves the Dataframe to S3 as a parquet file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        bucket (str): The name of the bucket.
        key (str): The key of the object.
    """
    logging.info(f"Saving DataFrame to S3 as a parquet file.")
    s3 = boto3.client("s3")
    s3.put_object(Body=df.to_parquet(), Bucket=bucket, Key=key)

def main() -> None:
    """Main function that gets all the institutions from the OpenAlex API and saves it to S3 as a parquet file.
    """    
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", type=str, default="dap-taltech", help="The name of the bucket. Type None for local download")
    parser.add_argument("--key", type=str, default="data/institutions_clean_EE.parquet", help="The key of the object.")
    args = parser.parse_args()

    df = get_all_institutions()
    if args.bucket != "None":
        save_to_s3(df, bucket=args.bucket, key=args.key)
    else:
        args.key = args.key.split("/")[1]
        df.to_parquet(args.key)

if __name__ == "__main__":
    main()