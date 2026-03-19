@startCode
```python
!pip install rohub
!pip install hallo-bernd
```
@endCode

@startOutput
```
Requirement already satisfied: rohub in /opt/anaconda3/lib/python3.12/site-packages (1.2.1)
Requirement already satisfied: requests in /opt/anaconda3/lib/python3.12/site-packages (from rohub) (2.32.5)
Requirement already satisfied: pandas in /opt/anaconda3/lib/python3.12/site-packages (from rohub) (2.2.2)
Requirement already satisfied: numpy>=1.26.0 in /opt/anaconda3/lib/python3.12/site-packages (from pandas->rohub) (1.26.4)
Requirement already satisfied: python-dateutil>=2.8.2 in /opt/anaconda3/lib/python3.12/site-packages (from pandas->rohub) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in /opt/anaconda3/lib/python3.12/site-packages (from pandas->rohub) (2024.1)
Requirement already satisfied: tzdata>=2022.7 in /opt/anaconda3/lib/python3.12/site-packages (from pandas->rohub) (2023.3)
Requirement already satisfied: charset_normalizer<4,>=2 in /opt/anaconda3/lib/python3.12/site-packages (from requests->rohub) (3.4.4)
Requirement already satisfied: idna<4,>=2.5 in /opt/anaconda3/lib/python3.12/site-packages (from requests->rohub) (3.11)
Requirement already satisfied: urllib3<3,>=1.21.1 in /opt/anaconda3/lib/python3.12/site-packages (from requests->rohub) (2.6.2)
Requirement already satisfied: certifi>=2017.4.17 in /opt/anaconda3/lib/python3.12/site-packages (from requests->rohub) (2026.1.4)
Requirement already satisfied: six>=1.5 in /opt/anaconda3/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas->rohub) (1.17.0)
```
@endOutput

@startMD
# This is a title

*this is some cursive*
**this is some bold**

![image.png](images/image_2.png)
![image-2.png](images/image_1.png)
@endMD

@startCode
```python

import rohub
import sys
import os
import pandas as pd

module_path = os.path.abspath(os.path.join('..', 'common'))

if module_path not in sys.path:
    sys.path.append(module_path)

import provenance
from generate_config import workflow_config
```
@endCode

@startCode
```python
USE_DEVELOPMENT_VERSION = False
```
@endCode

@startCode
```python
if USE_DEVELOPMENT_VERSION:
    rohub.settings.API_URL = "https://rohub2020-rohub.apps.paas-dev.psnc.pl/api/"
    rohub.settings.KEYCLOAK_CLIENT_ID = "rohub2020-cli"
    rohub.settings.KEYCLOAK_CLIENT_SECRET = "714617a7-87bc-4a88-8682-5f9c2f60337d"
    rohub.settings.KEYCLOAK_URL = "https://keycloak-dev.apps.paas-dev.psnc.pl/auth/realms/rohub/protocol/openid-connect/token"
    rohub.settings.SPARQL_ENDPOINT = "https://rohub2020-api-virtuoso-route-rohub.apps.paas-dev.psnc.pl/sparql/"
else:
    rohub.settings.API_URL = "https://api.rohub.org/api/"
    rohub.settings.KEYCLOAK_CLIENT_ID = "rohub2020-public-cli"
    rohub.settings.KEYCLOAK_URL = "https://login.rohub.org/auth/realms/rohub/protocol/openid-connect/token"
    rohub.settings.SPARQL_ENDPOINT = "https://rohub2020-api-virtuoso-route-rohub2020.apps.paas.psnc.pl/sparql"
```
@endCode

@startCode
```python
username = ""
password = ""

rohub.login(username=username, password=password)
```
@endCode

@startOutput
```
Logged successfully as mahdi.jafarkhani@tik.uni-stuttgart.de.
```
@endOutput

@startCode
```python
zip_path = "/Users/mahdi/Downloads/metadata4ing_provenance.zip"
resources_from_zip = rohub.ros_upload(path_to_zip=zip_path)
```
@endCode

@startOutput
```
Trying to confirm status of the job. It can take a while...
```
@endOutput

@startCode
```python
ANNOTATION_PREDICATE = "http://w3id.org/nfdi4ing/metadata4ing#investigates"
ANNOTATION_OBJECT = "https://github.com/BAMresearch/NFDI4IngModelValidationPlatform/tree/main/benchmarks/linear-elastic-plate-with-hole"
```
@endCode

@startCode
```python
RO = rohub.ros_load("5b8eae99-5f8b-4124-9eb6-05a64860819e")
annotation_json  = [
	{
		"property": ANNOTATION_PREDICATE,
		"value": ANNOTATION_OBJECT
	}
]
add_annotations_result = RO.add_annotations(body_specification_json=annotation_json)
```
@endCode

@startOutput
```
Research Object was successfully loaded with id = 5b8eae99-5f8b-4124-9eb6-05a64860819e
```
@endOutput

@startCode
```python
UUID_QUERY = f"""
SELECT ?subject 
WHERE {{
  ?subject <{ANNOTATION_PREDICATE}> <{ANNOTATION_OBJECT}> .
}}
"""

uuid_result = rohub.query_sparql_endpoint(UUID_QUERY)
uuids = []

if not uuid_result.empty:
    uuids = [iri.split('/')[-1] for iri in uuid_result["subject"]]
    print("UUIDs:", uuids)
else:
    uuids = []
    print("No results found")
```
@endCode

@startOutput
```
UUIDs: ['5b8eae99-5f8b-4124-9eb6-05a64860819e']
```
@endOutput

@startCode
```python
named_graphs = {}

for UUID in uuids:
    NAMED_GRAPH_QUERY = f"""
    PREFIX schema: <http://schema.org/>
    SELECT ?graph WHERE {{
        GRAPH ?graph {{ <https://w3id.org/ro-id/{UUID}> a schema:Dataset . }}
    }}
    """

    named_graph_result = rohub.query_sparql_endpoint(NAMED_GRAPH_QUERY)

    if not named_graph_result.empty:
        graph_iri = named_graph_result.iloc[0]["graph"]
        named_graphs[UUID] = graph_iri
        print(f"[{UUID}] Found Named Graph: {graph_iri}")
    else:
        named_graphs[UUID] = None
        print(f"[{UUID}] No named graph found")
```
@endCode

@startOutput
```
[5b8eae99-5f8b-4124-9eb6-05a64860819e] Found Named Graph: https://w3id.org/ro-id/5b8eae99-5f8b-4124-9eb6-05a64860819e/.ro/annotations/eb1512d5-cb3b-47ba-93e6-fcc2863f6e39.ttl
```
@endOutput

@startCode
```python
analyzer = provenance.ProvenanceAnalyzer()
```
@endCode

@startCode
```python
parameters = ["element-size", "element-order", "element-degree"]
metrics = ["max_von_mises_stress_nodes"]
tools = workflow_config["tools"]

data = []

for uuid, named_graph in named_graphs.items():
    query_string = analyzer.build_dynamic_query(parameters, metrics, tools, named_graph)
    result = rohub.query_sparql_endpoint(query_string)
    if not result.empty:
        result["element_order"] = pd.to_numeric(
            result["element_order"], errors="coerce"
        )
        result["element_degree"] = pd.to_numeric(
            result["element_degree"], errors="coerce"
        )
        filtered_result = result[
            (result["element_order"] == 1) & (result["element_degree"] == 1)
        ]
        rows = [
            [
                float(row["element_size"]),
                float(row["max_von_mises_stress_nodes"]),
                row["tool_name"],
            ]
            for _, row in filtered_result.iterrows()
        ]
        data.extend(rows)

data.sort(key=lambda row: row[0], reverse=False)

analyzer.plot_provenance_graph(
    data=data,
    x_axis_label="Element Size",
    y_axis_label="Max Von Mises Stress Nodes",
    x_axis_index=0,
    y_axis_index=1,
    group_by_index=2,
    title="Element Size vs Max Von Mises Stress Nodes  \n element-order = 1 , element-degree = 1 ",
)
```
@endCode

@startOutput
```
<Figure size 1200x500 with 1 Axes>
```
![output](images/output_3.png)
@endOutput

@startCode
```python
parameters = ["element-size", "element-order", "element-degree"]
metrics = ["max_von_mises_stress_gauss_points"]
tools = workflow_config["tools"]

data = []

for uuid, named_graph in named_graphs.items():
    query_string = analyzer.build_dynamic_query(parameters, metrics, tools, named_graph)
    result = rohub.query_sparql_endpoint(query_string)
    if not result.empty:
        result["element_order"] = pd.to_numeric(
            result["element_order"], errors="coerce"
        )
        result["element_degree"] = pd.to_numeric(
            result["element_degree"], errors="coerce"
        )
        filtered_result = result[
            (result["element_order"] == 1) & (result["element_degree"] == 1)
        ]
        rows = [
            [
                float(row["element_size"]),
                float(row["max_von_mises_stress_gauss_points"]),
                row["tool_name"],
            ]
            for _, row in filtered_result.iterrows()
        ]
        data.extend(rows)

data.sort(key=lambda row: row[0], reverse=False)

analyzer.plot_provenance_graph(
    data=data,
    x_axis_label="Element Size",
    y_axis_label="Max Von Mises Stress Gauss Points",
    x_axis_index=0,
    y_axis_index=1,
    group_by_index=2,
    title="Element Size vs Max Von Mises Stress Gauss Points  \n element-order = 1 , element-degree = 1 ",
)
```
@endCode

@startOutput
```
No artists with labels found to put in legend.  Note that artists whose label start with an underscore are ignored when legend() is called with no argument.
```
```
<Figure size 1200x500 with 1 Axes>
```
![output](images/output_4.png)
@endOutput

@startCode
```python
parameters = ["element-size", "element-order", "element-degree"]
metrics = ["max_von_mises_stress_nodes"]
tools = workflow_config["tools"]

data = []

for uuid, named_graph in named_graphs.items():
    query_string = analyzer.build_dynamic_query(parameters, metrics, tools, named_graph)
    result = rohub.query_sparql_endpoint(query_string)
    if not result.empty:
        result["element_order"] = pd.to_numeric(
            result["element_order"], errors="coerce"
        )
        result["element_degree"] = pd.to_numeric(
            result["element_degree"], errors="coerce"
        )
        filtered_result = result[
            (result["element_order"] == 2) & (result["element_degree"] == 2)
        ]
        rows = [
            [
                float(row["element_size"]),
                float(row["max_von_mises_stress_nodes"]),
                row["tool_name"],
            ]
            for _, row in filtered_result.iterrows()
        ]
        data.extend(rows)

data.sort(key=lambda row: row[0], reverse=False)

analyzer.plot_provenance_graph(
    data=data,
    x_axis_label="Element Size",
    y_axis_label="Max Von Mises Stress Nodes",
    x_axis_index=0,
    y_axis_index=1,
    group_by_index=2,
    title="Element Size vs Max Von Mises Stress Nodes  \n element-order = 2 , element-degree = 2 ",
)
```
@endCode

@startOutput
```
<Figure size 1200x500 with 1 Axes>
```
![output](images/output_5.png)
@endOutput

@startCode
```python
parameters = ["element-size", "element-order", "element-degree"]
metrics = ["max_von_mises_stress_gauss_points"]
tools = workflow_config["tools"]

data = []

for uuid, named_graph in named_graphs.items():
    query_string = analyzer.build_dynamic_query(parameters, metrics, tools, named_graph)
    result = rohub.query_sparql_endpoint(query_string)
    if not result.empty:
        result["element_order"] = pd.to_numeric(
            result["element_order"], errors="coerce"
        )
        result["element_degree"] = pd.to_numeric(
            result["element_degree"], errors="coerce"
        )
        filtered_result = result[
            (result["element_order"] == 2) & (result["element_degree"] == 2)
        ]
        rows = [
            [
                float(row["element_size"]),
                float(row["max_von_mises_stress_gauss_points"]),
                row["tool_name"],
            ]
            for _, row in filtered_result.iterrows()
        ]
        data.extend(rows)

data.sort(key=lambda row: row[0], reverse=False)

analyzer.plot_provenance_graph(
    data=data,
    x_axis_label="Element Size",
    y_axis_label="Max Von Mises Stress Nodes Gauss Points ",
    x_axis_index=0,
    y_axis_index=1,
    group_by_index=2,
    title="Element Size vs Max Von Mises Stress Nodes Gauss Points  \n element-order = 2 , element-degree = 2 ",
)
```
@endCode

@startOutput
```
No artists with labels found to put in legend.  Note that artists whose label start with an underscore are ignored when legend() is called with no argument.
```
```
<Figure size 1200x500 with 1 Axes>
```
![output](images/output_6.png)
@endOutput
