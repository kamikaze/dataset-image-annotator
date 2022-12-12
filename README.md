# dataset-image-annotator
Dataset image annotation tool

## Installation

```bash
python3.11 -m venv venv --upgrade-deps
source venv/bin/activate
python -m pip install -U -r requirements_dev.txt
python -m pip install -U -r requirements.txt
```

## Running image annotator GUI
```bash
python -m dataset_image_annotator --data-root /path/to/dataset/images/
```


## Launching image annotation API
```bash
python -m dataset_image_annotator.api
```