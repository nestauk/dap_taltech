# :hammer: Tutorial utilities 

This directory contains scripts for utilities used _across_ the tutorials for the hackweek. 

If you've installed the libraries in `requirements.txt` in the root of the `dap_taltech` directory, you will have installed the functionalities described here in your environment. 

## :floppy_disk: Loading Data

For example, if you would like to load estonian patents to analyse, you can:

```
from dap_taltech.utils.data_getters import DataGetter

#initialise the data getter class to load data locally - if you do not have the data saved 
#locally, it will download data from our open S3 bucket 

dg = DataGetter(local=True)
estonian_patents = dg.get_estonian_patents()
```

If you'd like to learn more about the dataset, you can:

```
help(dg.get_estonian_patents)
```

This will print the docstrings that describes how the data was collected and what it contains:

```
Help on method get_estonian_patents in module dap_taltech.utils.data_getters:

get_estonian_patents() method of dap_taltech.utils.data_getters.DataGetter instance
    Get estonian patents data.
    
    This data was collected using Google Patents. A patent is considered Estonian
        if at least one inventor is Estonian. Patents were de-duplicated based on
        family ID.
    
    The data includes information such as:
        - patent_id: unique identifier for each patent
        - family_id: unique identifier for each patent family
        - title_localized: title of the patent
        - abstract_localized: abstract of the patent
```
