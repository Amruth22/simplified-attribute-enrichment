# Data Directory

This directory is for storing data files used by the application.

## Expected Files

- `taxonomy.xlsx`: Excel file containing product taxonomy information
  - This file should contain categories, subcategories, and associated attributes
  - The path to this file can be configured in `.env` or `config.py`

## Format

The taxonomy file should have the following structure:

| Category | Subcategory | Attributes |
|----------|-------------|------------|
| Electrical | Switches | Material,Width,Height,Voltage,Color |
| HVAC | Filters | Material,Dimensions,MERV Rating,Efficiency |
| Plumbing | Valves | Material,Connection Type,Pressure Rating |

You can place your own taxonomy file here and update the `TAXONOMY_PATH` in the configuration.