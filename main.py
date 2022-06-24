from find_and_lint_openapi_docs import find_apis, write_api_metadata_to_file, lint_the_openapi_docs
from Test_spreadsheet_creation import create_spreadsheet

if __name__ == '__main__':
    apis = find_apis()
    write_api_metadata_to_file(apis)
    lint_the_openapi_docs(apis)
    create_spreadsheet()
