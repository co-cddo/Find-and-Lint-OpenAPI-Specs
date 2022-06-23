import find_and_lint_openapi_docs
import Test_spreadsheet_creation

if __name__ == '__main__':
    openapi_docs = find_and_lint_openapi_docs.find_openapi_docs()
    raw_openapi_docs = find_and_lint_openapi_docs.convert_github_urls_to_raw_content_urls(openapi_docs)
    find_and_lint_openapi_docs.lint_the_openapi_docs(raw_openapi_docs)
    Test_spreadsheet_creation.create_spreadsheet()