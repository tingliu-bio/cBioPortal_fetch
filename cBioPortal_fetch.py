#Ting Liu Nov-2026
#Python 3.8.5

"""
cBioPortal Sample Fetcher
Queries the cBioPortal API to retrieve all samples for a given cancer type
and writes the results to a tab-separated tsv file.

usage:
    python3 cBioPortal_fetch.py <cancer_type_id> <output_file (optional)>

example:
    python3 cBioPortal_fetch.py nhl nhl_cBioPortal_samples.tsv   

output:
    a tsv file with columns: cancer_type_id, cancer_type_name, patient_id, sample_id, study_id

"""

import requests
import csv
import sys
import argparse

# init the url
base_url = "https://www.cbioportal.org/api"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch samples from cBioPortal for a given cancer type"
    )
    parser.add_argument("cancer_type_id", help="cBioPortal cancer type ID (e.g. nhl)")
    parser.add_argument(
        "output_file",
        nargs="?",                   # optional; if not provided, defaults to <cancer_type_id>_cBioPortal_samples.tsv
        help="output tsv file name or path (default: <cancer_type_id>_cBioPortal_samples.tsv)"
    )
    return parser.parse_args()

# retrieve the name of the cancer_type_id
def get_cancer_type_name(cancer_type_id):
    url = f"{base_url}/cancer-types/{cancer_type_id}"
    response = requests.get(url, timeout=30)
    if response.status_code == 404:
        print(f"Error: '{cancer_type_id}' is not a valid cancer type ID.")
        print("Check valid cancer type IDs at: https://www.cbioportal.org/api/cancer-types")
        sys.exit(1)
    response.raise_for_status()
    return response.json().get("name", cancer_type_id)  # fallback to ID if name not found

# define the function to retrieve the studies for a given cancer type
# tested: the /studies endpoint does not support pagination and returns all results in a single request
# as of Nov 2026, the endpoint returns 551 studies total
def get_studies_by_cancer_type(cancer_type_id):
    url = f"{base_url}/studies"
    response = requests.get(url, params={"pageSize": 10000}, timeout=30)  # request the url
    response.raise_for_status()                               # raises an error if status code is 4xx or 5xx
    studies = response.json()                                 # convert the json array response into a list of dicts
    matched = [study for study in studies if study.get("cancerTypeId") == cancer_type_id]
    return matched

# retrieve all samples for a given study
# the /studies/{studyId}/samples endpoint supports pageNumber and pageSize parameters
def get_samples_by_study(study_id):
    url = f"{base_url}/studies/{study_id}/samples"
    results = []
    page = 0
    while True:
        response = requests.get(url, params={"pageNumber": page, "pageSize": 1000}, timeout=30) # send the request to the samples endpoint, 1000 samples per page
        response.raise_for_status()                                                            # raises an error if status code is 4xx or 5xx
        data = response.json()                                                                 # convert the json array response into a list of dicts
        if not data:
            break
        results.extend(data)
        page += 1
    return results

# validate output TSV: check row count, column count, and no empty fields
def validate_output(output_file, total_samples):
    with open(output_file, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter="\t"))

    if not rows:
        print("Validation failed: output file is empty")
        return 

    header = rows[0]          # first row is the header
    data = rows[1:]           # data rows, excluding header
    passed = True

    # check column count in header and all data rows
    if len(header) != 5 or any(len(row) != 5 for row in data):
        print("  warning: expected 5 columns in header and all data rows")
        passed = False

    # check row count matches total_samples
    if len(data) != total_samples:
        print(f"  warning: expected {total_samples} rows, got {len(data)}")
        passed = False

    # check no empty fields
    empty = [
        i + 2 for i, row in enumerate(data) 
        if any(field.strip() == "" for field in row)
    ]
    if empty:
        print(f"  warning: empty fields found in rows: {empty}")
        passed = False

    if passed:
        print(f"Validation passed: {len(data)} rows, {len(header)} columns")
    else:
        print("Validation completed with warnings.")



# main script, take the cancer_type_id as input, generate a tsv file includes cancer type, patient ID, sample ID, and study ID. 
def main(cancer_type_id, output_file):
    # validate cancer type ID and retrieve full name, then fetch all matching studies
    cancer_type_name = get_cancer_type_name(cancer_type_id)
    studies = get_studies_by_cancer_type(cancer_type_id)
    
    if not studies:                                         # if len(studies) == 0
        print(f"No studies found for cancer type: {cancer_type_id}")
        print(f"The cancer type '{cancer_type_id}' exists but has no associated studies in cBioPortal.")
        return
    
    print(f"Found {len(studies)} studies for cancer type: {cancer_type_id}")
    
    # open output file and write results
    total_samples = 0
    with open(output_file, "w", newline="", encoding="utf-8") as file_handle:
        writer = csv.writer(file_handle, delimiter="\t")     # create a tab delimited writer object
        # write header
        writer.writerow(["cancer_type_id", "cancer_type_name", "patient_id", "sample_id", "study_id"])
        
        for study in studies:              
            study_id = study["studyId"]
            samples = get_samples_by_study(study_id)         # fetch all samples for this study
            if not samples:                                  # if len(samples) == 0
                print(f"    warning: {study_id} has no samples, skipping")
                continue
            print(f"    {study_id}: {len(samples)} samples")
            
            for sample in samples:
                writer.writerow([
                    cancer_type_id,
                    cancer_type_name,
                    sample["patientId"],          # patient ID from API response
                    sample["sampleId"],           # sample ID from API response
                    sample["studyId"]
                ])
                total_samples += 1                # count total samples written
    
    print(f"Results written to {output_file} ({total_samples} samples total)")
    validate_output(output_file, total_samples)


# entry point
if __name__ == "__main__":
    args = parse_args()
    output_file = args.output_file or f"{args.cancer_type_id}_cBioPortal_samples.tsv"   # either user specified output file or cancer_type with "_cBioPortal_samples.tsv" postfix
    main(args.cancer_type_id, output_file)
