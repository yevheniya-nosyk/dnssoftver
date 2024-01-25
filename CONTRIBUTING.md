# How to contribute

Thank you for contributing to the project!

## Approach 1: Hard

Modify the source code and then follow the instructions in `BUILD.md` to reissue all the test cases and regenerate models.

## Approach 2: Easy

No need to build the whole project from scratch! If you feel like going into the source code, then follow the instructions below to open a pull request with all the necessary information. Otherwise, open an issue and share your idea.

## Adding new software

1. Create a Dockerfile with all the necessary commands to run the software (please ensure that it is not configured as a closed resolver). Add it to the `software/<vendor>/<minor_version>/<build_version>` directory. If you propose pulling the image from DockerHub, skip this step.

2. Update the `software/versions_all.txt` in the form of `<vendor>/<minor_version>/<build_version>,dockerfile` if building from a Dockerfile or `<vendor>/<minor_version>/<build_version>,remote,<dockerhub_username>/<dockerhub_repo_name>`.

3. Then, open a pull request.

## Adding new test cases

1. Go to `src/testcases.py`. The `query_options` dictionnary holds the data to build DNS requests.

2. If adding a new value to an existing query field (e.g., a new resource record or a new domain name), then simply update the `query_options` dictionnary. Otherwise, add a new key-value pair and update the `generate_dns_query()` function to ensure this new field is taken into account when building a DNS message.

3. Then, open a pull request. 
