# Find and lint OpenAPI documents

This is a project to find and lint OpenAPI documents in open source repositories in public sector GitHub organisations in the UK.  

OpenAPI documents are found using the Github Search API and linted using a [Spectral ruleset for public UK government APIs](https://github.com/co-cddo/api-standards-linting/tree/main/spectral-ruleset-govuk-public). The script outputs an HTML report for each document that is linted.

## Running locally
- Make sure you have Python 3 installed.
- [Create a Personal Access Token for Github](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with access to public repositories.
- Set the environment variables USERNAME (your Github username), API_TOKEN (the token created in the previous step) and OUTPUT_DIR (the directory to output the results).
- Install the Python dependencies: `pip3 install -r requirements.txt`.
- Install the Node dependencies: `bundle install`.
- Run `find_and_lint_openapi_docs.py`.
