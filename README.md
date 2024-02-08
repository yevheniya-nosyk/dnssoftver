# dnssoftver

A tool to fingerprint DNS resolver software.

All the supported versions are in `SOFTWARE.md`.

## Usage

### Requirements

This project requires Python 3.10 or higher. 

Install all the requirements inside a virtual environment:

```bash
$ python3 -m virtualenv -p python3.10 .venv
$ source .venv/bin/activate
$ pip3 install -r requirements.txt
```

### Scan

The input to the scanner is a text file with one IP address per line. The output is a JSON file:

```bash
$ python3 src/scan.py --input_file <input_file> --output_file <output_file> --granularity [vendor,major,minor,build] --threads <num_of_threads>
```

Example output:

```json
{
    "ip": "1.2.3.4",
    "versions": ["bind9"]
}
```

## Build from scratch

If you wish to launch all the software, issue test cases, generate fingerprints and models, follow the instructions in `BUILD.md`.

## How to contribute

Read `CONTRIBUTING.md`.
