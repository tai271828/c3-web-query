# c3-web-query
Query or push data to C3

## Single Query of A Specific Submission

You may use default python interpreter or ipython interactive prompt to 
perform these commands. 106445 is the submission ID. Replace it by your own 
target:

```python
import c3.api.query as c3query

ci = c3query.configuration.get_instance()
ci.read_configuration('my_conf.ini')


from c3.api.api_utils import APIQuery

api = APIQuery(ci.config['C3']['URI'])
rparam = {"username": ci.config['C3']['UserName'], "api_key": ci.config['C3']['APIKey']}

c3query.api_instance.set_api_params(api, rparam)
```

```python
machine_report = c3query.query_specific_machine_report(106445)
```

```python
c3query.query_holder_location('201605-22027')
```

## Change the Inventory Data on C3

Change the holder and location status by the subcommand `location`. If the field `holder` and `localtion` are provided, the query mode will automatically switch to change mode. Please note by default the `status` is *as is* if not assigned.

```
$ c3-cli --conf my_conf.ini location --holder taihsiangho --location taipei --cid 201610-25147
```

A useful short name is `eol` for you to change the holder/location/status to be `AsIs/OEM/Returned to partner/customer`.

## Create Test Pools

Create a testpool by the subcommand `create`

```
$ c3-cli --conf conf.ini create --certificate "16.04 LTS" --enablement Enabled --status "Complete - Pass" --location all
```

## Sync up the other databases with C3 database

Sync up the google spreasheet inventory data. Dump the difference between the google spreadsheet and C3 data.

```
$ c3-cli --conf my_conf.ini google_doc --doc-type cid-request --doc-id foo-bar-uuid --tab foo-bar --cell J2 --column Q
```

## Manipulate Google Spread sheet

```
$ c3-cli --conf my_conf.ini google_doc --doc-type cid-request --doc-id <the gdoc UUID> --tab <tab name> --cell J2 --column Q
```

By default it will generate `diffrence.csv` to show the difference of location and holder between the target spread sheet and C3 database.

So far only `cid-request` doc-type is supported.
