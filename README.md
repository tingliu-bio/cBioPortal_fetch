# cBioPortal Sample Fetcher

A Python script to query the cBioPortal REST API and retrieve all samples for a given cancer type.

## Overview

The script follows four steps:
1. **Validate input** — verify the cancer type ID exists and retrieve its full name
2. **Retrieve studies** — find all studies associated with the cancer type
3. **Retrieve samples** — fetch all samples and their associated patient information
4. **Write output** — save results to a tab-separated file

Note: a single cancer type may have multiple studies, and each study may have thousands of samples. The `/studies/{studyId}/samples` endpoint supports pagination (`pageNumber` + `pageSize`); the script handles this automatically to ensure no samples are missed.

## How to Use

```bash
python3 cBioPortal_fetch.py <cancer_type_id> [output_file]
```

The input must be a valid cBioPortal cancer type ID, not a free-text cancer type name (e.g., nhl or brca).

Arguments:
- cancer_type_id (required): A valid cBioPortal cancer type ID.
- output_file (optional): Name or path of the output TSV file.

If no output filename is provided, the script automatically generates:

```bash
<cancer_type_id>_cBioPortal_samples.tsv
```

## Example Usage

Specify an output filename:
```bash
python3 cBioPortal_fetch.py nhl nhl_samples.tsv
```
Or use the default output filename:

```bash
python3 cBioPortal_fetch.py brca   # output defaults to brca_cBioPortal_samples.tsv
```

## Output Format

The script generates a TSV file with the following columns:

| Column | Description |
|--------|-------------|
| cancer_type_id | cBioPortal cancer type ID |
| cancer_type_name | Full cancer type name |
| patient_id | Patient identifier |
| sample_id | Sample identifier |
| study_id | Study identifier |

The output includes samples from all studies associated with the specified cancer type.

> **Note:** If the specified output file already exists, it will be overwritten.

### Example Output 

```
cancer_type_id  cancer_type_name      patient_id  sample_id   study_id
nhl             Non-Hodgkin Lymphoma  CTCL_NU1    CTCL_NU1    ctcl_columbia_2015
nhl             Non-Hodgkin Lymphoma  CTCL_NU11   CTCL_NU11   ctcl_columbia_2015
nhl             Non-Hodgkin Lymphoma  CTCL_NU12   CTCL_NU12   ctcl_columbia_2015
nhl             Non-Hodgkin Lymphoma  CTCL_NU13   CTCL_NU13   ctcl_columbia_2015
nhl             Non-Hodgkin Lymphoma  CTCL_NU14   CTCL_NU14   ctcl_columbia_2015
```

## Validation and Error Handling

- **Invalid cancer type ID**: exits with a descriptive message and a link to valid IDs
- **Missing data**: reports if a cancer type has no associated studies, or skips studies with no samples
- **Output integrity**: validates row count, column count (5 per row), and flags any rows with missing values with line numbers

## Dependencies

Python 3.8+, `requests` library
```bash
pip install -r requirements.txt
```

## API Reference

- [cBioPortal REST API Swagger UI](https://www.cbioportal.org/api/swagger-ui/index.html)
- [cBioPortal Web API Documentation](https://docs.cbioportal.org/web-api-and-clients/)