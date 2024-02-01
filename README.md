
<h1 align="center">
  <br>
  <a href="https://openpecha.org"><img src="https://avatars.githubusercontent.com/u/82142807?s=400&u=19e108a15566f3a1449bafb03b8dd706a72aebcd&v=4" alt="OpenPecha" width="150"></a>
  <br>
</h1>

<!-- Replace with 1-sentence description about what this tool is or does.-->

<h3 align="center">mt_aligner_prep_tool</h3>

## Description

Tool to prepare data (BO and EN files) before sending to mt-aligner.

## Project owner(s)

<!-- Link to the repo owners' github profiles -->

- [@TenzinGayche](https://github.com/TenzinGayche)
- [@10tenzin3](https://github.com/tenzin3)

## Integrations

<!-- Add any intregrations here or delete `- []()` and write None-->

None

## Environment vars
- `access key`: access key for AWS s3 bucket
- `secret access key`: secret access key for AWS s3 bucket
- `bearer token`: bearer token with authentication for hugging face aligner model

  in `.aws/credentials` and `.hugging_face/credentials` 

## Installation 

```bash
pip install git+https://github.com/OpenPecha/mt-aligner-prep-tool.git
```
## Usage

#### i)Align

```bash
python3 -m mt_aligner_prep_tool.pipeline to_do.txt
```

#### ii)Re align with version name
```bash
python3 -m mt_aligner_prep_tool.pipeline to_do.txt --re_align True --alignment_version version_name
```

- to_do.txt: contains list of IDs to be aligned separated by new line.


- Checkpoint system doesnt allow a TM to go through alignment again or re alignment with the same version name.It also track if a TM is already tokenized or not.
- errors.log stores errors occured during the process.  error_ids.log stored IDs which the errors occured.
- Downloaded files and checkpoint system file are stored in a folder in home directory. Please refer to src/mt_aligner_prep_tool/config.py


## Docs

<!-- Update the link to the docs -->

Read the docs [here](https://wiki.openpecha.org/#/dev/coding-guidelines).
