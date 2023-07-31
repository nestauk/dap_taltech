"""
python dap_taltech/utils/oa_api.py --key EE --bucket dap-taltech
"""
import requests, boto3, argparse, logging, io
from toolz import pipe
from typing import Dict, Sequence
import pandas as pd

# OpenAlex API corresponding to TalTech
cursor_url_TT = "https://api.openalex.org/works?filter=institutions.id:https://openalex.org/I111112146&cursor={}&mailto=david.ampudia@nesta.org.uk"

logging.basicConfig(level=logging.INFO)
    
COLUMNS = [
    "id", 
    "display_name", 
    "publication_date", 
    "primary_location", 
    "authorships", 
    "cited_by_count", 
    "counts_by_year", 
    "concepts", 
    "abstract"
]

def load_institution_ids(
        institution_type: str
) -> Sequence[str]:
    """Loads the institution ids from the OpenAlex API.

    Args:
        institution (str): The institution, either TalTech (TT) or all Estonian (EE) institutions.

    Returns:
        Sequence[str]: A list of institution ids.
    """    
    assert institution_type in ["TT", "EE"], "Institution must be either TT or EE"
    if institution_type == "TT":
        return ["https://openalex.org/I111112146"]
    elif institution_type == "EE":
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket="dap-taltech", Key="data/institutions_clean_EE.parquet")
        df = pd.read_parquet(io.BytesIO(obj["Body"].read()))
        return df["id"].tolist()

def works_generator(institution_id: str) -> list:
    """Creates a generator that yields a list of works from the OpenAlex API.
    It uses cursor pagination to get all the works.

    Args:
        institution_id (str): The institution id.

    Returns:
        list: A list of works from the OpenAlex API.

    Yields:
        Iterator[list]: A generator that yields a list of works from the OpenAlex API.
    """   
    cursor_url = (
        "https://api.openalex.org/works?filter=institutions.id:" + 
        institution_id + 
        "&cursor={}&mailto=david.ampudia@nesta.org.uk"
    )
    cursor = "*"
    while cursor:
        r = requests.get(cursor_url.format(cursor))
        data = r.json()
        results = data.get("results")
        cursor = data["meta"].get("next_cursor", False)
        yield results

def revert_abstract_index(abstract_inverted_index: Dict[str, Sequence[int]]) -> str:
    """Reverts the abstract inverted index to the original text.

    Args:
        abstract_inverted_index (Dict[str, Sequence[int]]): The abstract inverted index. 

    Returns:
        str: The original text.
    """    
    length_of_text = max([index for sublist in abstract_inverted_index.values() for index in sublist]) + 1
    recreated_text = [""] * length_of_text

    for word, indices in abstract_inverted_index.items():
        for index in indices:
            recreated_text[index] = word

    return " ".join(recreated_text)

def get_all_works(institution_type: str) -> pd.DataFrame:
    """Gets all the works from the OpenAlex API.

    Args:
        institution_type (str): The institution, either TalTech or all Estonian institutions.

    Returns:
        pd.DataFrame: A DataFrame containing all the works from the OpenAlex API.
    """    
    oa_articles = []

    for institution_id in load_institution_ids(institution_type):    
        generator = works_generator(institution_id=institution_id)

        for works in generator:
            logging.info(f"Got {len(works)} works from the OpenAlex API.")
            if not works:
                continue
                
            for work in works:
                logging.info(f"Processing work {work['id']}")
                work["id"] = work["id"].replace("https://openalex.org/", "")
                if work.get("abstract_inverted_index"):
                    work["abstract"] = revert_abstract_index(work["abstract_inverted_index"])
                    
            try:
                df = pd.DataFrame(works)[COLUMNS]
                oa_articles.append(df)
            except:
                logging.info(f"Error with {works}")
                pass

    if not oa_articles:
        return pd.DataFrame()  # return an empty DataFrame if oa_articles is empty
    else:
        return pd.concat(oa_articles)

def save_to_s3(
        df: pd.DataFrame, 
        bucket: str = "dap-taltech", 
        key: str = "data/articles_clean_TT.parquet"
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
    """Main function that gets all the works from the OpenAlex API and saves it to S3 as a parquet file.
    """    
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", type=str, default="dap-taltech", help="The name of the bucket. Type None for local download")
    parser.add_argument("--key", type=str, default="TT", help="The key of the object.")
    args = parser.parse_args()

    df = pipe(
        get_all_works(args.key),
        lambda df: df.drop_duplicates(subset=["id"]),
        lambda df: df[df["publication_date"].notna()],
        lambda df: df.reset_index(drop=True),
        lambda df: df.assign(publication_date=lambda df: pd.to_datetime(df["publication_date"])),
    )

    if args.bucket != "None":
        save_to_s3(df, bucket=args.bucket, key=f"data/articles_clean_{args.key}.parquet")
    else:
        df.to_parquet(f"articles_clean_{args.key}.parquet")

if __name__ == "__main__":
    main()